# SPDX-License-Identifier: GPL-3.0-only

"""Reading and writing image files, with the collaborators defaulted.

Wraps `rexlib._binding.em.image`: the same functions, but the format
manager and the reader provider default to ones over the default catalog
(see `rexlib.get_default_catalog`) and `read`'s `context` to the active
execution context, the way `rexlib.add` and its siblings take theirs. A
collaborator that takes a default comes after the arguments that do not.
"""

from __future__ import annotations

from ..._binding.dispatch import ExecutionContext
from ..._binding.em import image as _raw
from ..._binding.em.image import (
	CachingImageReaderProvider,
	DirectImageReaderProvider,
	ImageDescriptor,
	ImageLocation,
	ImageReaderProvider,
	ImageReadFormatManager,
	ImageWriteFormatManager,
	get_image_read_format_manager,
	get_image_write_format_manager,
)
from ..._binding.ndarray import Array
from ..._binding.numerical import NumericalType
from ..._catalog import get_default_catalog
from ..._functional import _resolve_context

def _resolve_read_manager(
	manager: ImageReadFormatManager | None
) -> ImageReadFormatManager:
	if manager is None:
		manager = get_image_read_format_manager(get_default_catalog())
	return manager

def _resolve_write_manager(
	manager: ImageWriteFormatManager | None
) -> ImageWriteFormatManager:
	if manager is None:
		manager = get_image_write_format_manager(get_default_catalog())
	return manager

def _resolve_readers(
	readers: ImageReaderProvider | None
) -> ImageReaderProvider:
	if readers is None:
		readers = reader_provider()
	return readers

def reader_provider(
	cache: int | None = None,
	manager: ImageReadFormatManager | None = None
) -> ImageReaderProvider:
	"""
	Assemble a reader provider over the formats a manager holds.

	Args:
		cache: How many open readers to keep between reads. Defaults to
			opening a file every time it is asked for, which is what
			suits reads that do not revisit a file.
		manager: The formats to recognize files with. Defaults to the
			ones the default catalog holds.

	Returns:
		ImageReaderProvider: The assembled provider.
	"""
	readers = DirectImageReaderProvider(_resolve_read_manager(manager))
	if cache is not None:
		readers = CachingImageReaderProvider(readers, cache)
	return readers

def query_descriptor(
	path: str,
	readers: ImageReaderProvider | None = None
) -> ImageDescriptor:
	"""
	Get the shape and data type of what an image file holds.

	The extents are those of the whole file, slowest axis first, so a
	stack reports the axis it stacks along before the shape of one of
	its images. `get_core_extents` leaves that axis out, which is the
	shape a batch destination carries beside its leading extent:

		descriptor = query_descriptor(path)
		destination = rexlib.make_contiguous_array_descriptor(
			(len(locations), *get_core_extents(descriptor)),
			descriptor.data_type
		)

	Args:
		path: The file to ask about.
		readers: Where the file becomes a reader. Defaults to a provider
			that opens it with the formats the default catalog holds.

	Returns:
		ImageDescriptor: The descriptor of the file.
	"""
	return _raw.query_descriptor(_resolve_readers(readers), path)

def read(
	path: str | ImageLocation,
	readers: ImageReaderProvider | None = None,
	context: ExecutionContext | None = None,
	data_type: NumericalType | None = None
) -> Array:
	"""
	Read an image file into an array.

	The array is allocated on the host whatever device is active, so
	reaching a device with it is an explicit `rexlib.to_device`. An
	execution context is still required, the same one array creation
	takes, so a bare read outside `with rexlib.device(...):` raises.

	Args:
		path: The file to read, or an `ImageLocation` addressing one
			image or volume of it. A string is a path and only a path;
			read `"3@stack.mrc"` by handing it to
			`ImageLocation.from_string` first.
		readers: Where the file becomes a reader. Defaults to a provider
			that opens it with the formats the default catalog holds.
		context: The execution context to allocate under. Defaults to the
			active one.
		data_type: The type to read the values as. Defaults to the one
			the file holds.

	Returns:
		Array: What the path or the location names, on the host.
	"""
	return _raw.read(
		path,
		_resolve_readers(readers),
		_resolve_context(context),
		data_type
	)

def write_single(
	array: Array,
	path: str,
	manager: ImageWriteFormatManager | None = None,
	data_type: NumericalType | None = None
) -> None:
	"""
	Write an array to an image file as one image or volume.

	The array has to be reachable from the host; writing one that lives
	on a device raises rather than transferring it, so the transfer is
	an explicit `rexlib.to_host`.

	Args:
		array: The values to write.
		path: The file to write them to.
		manager: The formats to choose from. Defaults to the ones the
			default catalog holds.
		data_type: The type to store the values as. Defaults to the one
			the array already carries.
	"""
	_raw.write_single(array, path, _resolve_write_manager(manager), data_type)

def write_stack(
	array: Array,
	path: str,
	manager: ImageWriteFormatManager | None = None,
	data_type: NumericalType | None = None
) -> None:
	"""
	Write an array to an image file as a stack of images or volumes.

	The leading extent of the array is the axis the file stacks along
	and the rest are the shape of one image or volume. The array has to
	be reachable from the host, as for `write_single`.

	Args:
		array: The values to write.
		path: The file to write them to.
		manager: The formats to choose from. Defaults to the ones the
			default catalog holds.
		data_type: The type to store the values as. Defaults to the one
			the array already carries.
	"""
	_raw.write_stack(array, path, _resolve_write_manager(manager), data_type)

def write(
	array: Array,
	path: str,
	descriptor: ImageDescriptor,
	manager: ImageWriteFormatManager | None = None
) -> None:
	"""
	Write an array to an image file as a descriptor states.

	The core rank of the descriptor is what makes the file a stack
	rather than a single image or volume, and its data type is the one
	the file stores. The array has to be reachable from the host, as for
	`write_single`.

	Args:
		array: The values to write. Its shape has to be the extents of
			`descriptor`.
		path: The file to write them to.
		descriptor: What the file holds.
		manager: The formats to choose from. Defaults to the ones the
			default catalog holds.
	"""
	_raw.write(array, path, _resolve_write_manager(manager), descriptor)
