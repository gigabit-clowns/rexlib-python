# SPDX-License-Identifier: GPL-3.0-only

"""Image files: where one is, what it holds, and how it is read and written.

`ImageLocation` addresses a file, or one image or volume of a stack, and
`ImageDescriptor` states the shape and data type of what a file holds.
The two format managers hold the formats that can be read and written.
Both are services, reached from a `rexlib.ServiceCatalog` the way the
device and program managers are.

`read`, `write_single`, `write_stack` and `write` carry a file into and
out of an `Array`. They take their formats from the default catalog and
`read` its execution context from the active one.

`read_batch_async` and `read_patches_async` fill an array a caller
already has, through an `ImageSource`, and return a completion rather
than wait. `source` assembles one over a thread pool.

A string is never parsed into an `ImageLocation` on its way anywhere: a
path handed to the constructor, or to `read`, is a path, and
`ImageLocation.from_string` is the one thing that reads `"3@stack.mrc"`
as an index in a stack. It is the inverse of `str`, and raises
`ValueError` on anything it cannot read.
"""

from __future__ import annotations

from ..._binding.em.image import (
	CachingImageReaderProvider as CachingImageReaderProvider,
	DirectImageReaderProvider as DirectImageReaderProvider,
	ExecutorImageSource as ExecutorImageSource,
	ImageDescriptor as ImageDescriptor,
	ImageLocation as ImageLocation,
	ImageReaderProvider as ImageReaderProvider,
	ImageSource as ImageSource,
	ImageReadFormatManager as ImageReadFormatManager,
	ImageWriteFormatManager as ImageWriteFormatManager,
	IndexTable as IndexTable,
	get_core_extents as get_core_extents,
	get_image_read_format_manager as get_image_read_format_manager,
	get_image_write_format_manager as get_image_write_format_manager,
	read_batch_async as read_batch_async,
)
from ._functions import (
	query_descriptor as query_descriptor,
	read as read,
	read_patches_async as read_patches_async,
	reader_provider as reader_provider,
	source as source,
	write as write,
	write_single as write_single,
	write_stack as write_stack,
)

__all__ = [
	"CachingImageReaderProvider",
	"DirectImageReaderProvider",
	"ExecutorImageSource",
	"ImageDescriptor",
	"ImageLocation",
	"ImageReadFormatManager",
	"ImageReaderProvider",
	"ImageSource",
	"ImageWriteFormatManager",
	"IndexTable",
	"get_core_extents",
	"get_image_read_format_manager",
	"get_image_write_format_manager",
	"query_descriptor",
	"read",
	"read_batch_async",
	"read_patches_async",
	"reader_provider",
	"source",
	"write",
	"write_single",
	"write_stack",
]
