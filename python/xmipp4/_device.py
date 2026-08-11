# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from types import TracebackType

from ._catalog import get_default_catalog
from ._context import _set_active_execution_context, get_active_execution_context
from ._core_binding import dispatch, hardware


class _ActiveDeviceContext:
	"""Context manager that activates an ExecutionContext for its duration."""

	def __init__(self, spec: str | hardware.DeviceIndex) -> None:
		self.__spec = spec
		self.__previous: dispatch.ExecutionContext | None = None

	def __enter__(self) -> dispatch.ExecutionContext:
		index = (
			hardware.DeviceIndex(self.__spec)
			if isinstance(self.__spec, str)
			else self.__spec
		)

		catalog = get_default_catalog()
		session = hardware.get_device_manager(catalog).create_device_session(index)
		device_context = hardware.DeviceContext(session)

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

def device(spec: str | hardware.DeviceIndex) -> _ActiveDeviceContext:
	"""
	Activate a device as the current thread's execution context.

	Derives an execution context from whatever is currently active (see
	`xmipp4.get_active_execution_context`) by replacing its device context,
	and makes it active for the duration of the `with` block, restoring the
	previously active one on exit. Everything but the device context (e.g.
	the dispatcher) is preserved.

	Args:
		spec: The device to activate, either a "backend:id" /
			"backend" string (see `xmipp4.hardware.DeviceIndex`) or an
			already constructed DeviceIndex.

	Returns:
		A context manager yielding the activated ExecutionContext.
	"""
	return _ActiveDeviceContext(spec)
