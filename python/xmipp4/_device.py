# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from types import TracebackType
from typing import Union

from ._catalog import get_default_catalog
from ._context import _set_active_execution_context, get_active_execution_context
from ._core_binding import dispatch, hardware

DeviceSpec = Union[
	str, hardware.DeviceIndex, hardware.DeviceSession, hardware.DeviceContext
]

def _resolve_device_context(spec: DeviceSpec) -> hardware.DeviceContext:
	if isinstance(spec, hardware.DeviceContext):
		return spec
	if isinstance(spec, hardware.DeviceSession):
		return hardware.DeviceContext(spec)

	index = (
		hardware.DeviceIndex(spec)
		if isinstance(spec, str)
		else spec
	)
	catalog = get_default_catalog()
	session = hardware.get_device_manager(catalog).create_device_session(index)
	return hardware.DeviceContext(session)

class _ActiveDeviceContext:
	"""Context manager that activates an ExecutionContext for its duration."""

	def __init__(self, spec: DeviceSpec) -> None:
		self.__spec = spec
		self.__previous: dispatch.ExecutionContext | None = None

	def __enter__(self) -> dispatch.ExecutionContext:
		device_context = _resolve_device_context(self.__spec)
		context = get_active_execution_context().with_device_context(device_context)
		self.__previous = _set_active_execution_context(context)
		return context

	def __exit__(
		self,
		exc_type: type[BaseException] | None,
		exc_value: BaseException | None,
		traceback: TracebackType | None,
	) -> None:
		_set_active_execution_context(self.__previous)

def device(spec: DeviceSpec) -> _ActiveDeviceContext:
	"""
	Activate a device as the current thread's execution context.

	Derives an execution context from whatever is currently active (see
	`xmipp4.get_active_execution_context`) by replacing its device context,
	and makes it active for the duration of the `with` block, restoring the
	previously active one on exit. Everything but the device context (e.g.
	the dispatcher) is preserved.

	Args:
		spec: The device to activate. One of:
			- A "backend:id" / "backend" string, or a `DeviceIndex`
			  (see `xmipp4.hardware.DeviceIndex`): a new `DeviceSession` is
			  created for it, which is expensive and not shareable with any
			  other logical device handle -- prefer one of the options below
			  when activating the same device repeatedly (e.g. in a loop).
			- A `DeviceSession` (see `xmipp4.hardware.DeviceSession`),
			  reused as-is.
			- A `DeviceContext` (see `xmipp4.hardware.DeviceContext`),
			  used as-is.

	Returns:
		A context manager yielding the activated ExecutionContext.
	"""
	return _ActiveDeviceContext(spec)
