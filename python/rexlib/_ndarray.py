# SPDX-License-Identifier: GPL-3.0-only

"""Arrays, enriched with the Python operators the bound type cannot carry.

Wraps `rexlib._binding.ndarray`, adding operators to `Array`.
Operators cannot take an execution context, so they go through
`rexlib`, which falls back to the active one (see
`rexlib.get_active_execution_context`).

The operators are installed onto the bound `Array` rather than onto a
subclass: every array is built in C++, so a subclass would only ever be
seen by callers that construct one by hand.

`Array` exposes its memory through the buffer protocol, which is what
`numpy.asarray` uses. `__array__` is here for the arrays that cannot: numpy
asks it last, and would otherwise wrap such an array in an object array
instead of failing.

`__dlpack__` and `__dlpack_device__` hand the same memory to whatever
library takes DLPack. The capsule is built by the binding; what the protocol
lets a consumer ask for is decided here.
"""

from __future__ import annotations

from . import _functional
from ._binding.ndarray import Array, get_dlpack_device, to_dlpack

def _binary_operator(function):
	def operator(self: Array, other: Array) -> Array:
		if not isinstance(other, Array):
			return NotImplemented
		return function(self, other)
	return operator

def _in_place_operator(function):
	def operator(self: Array, other: Array) -> Array:
		if not isinstance(other, Array):
			return NotImplemented
		function(self, other, out=self)
		return self
	return operator

def _unary_operator(function):
	def operator(self: Array) -> Array:
		return function(self)
	return operator

def _deep_copy(self: Array, memo: dict) -> Array:
	return _functional.copy(self)

def _to_numpy(self: Array, dtype=None, copy=None):
	import numpy  # noqa: PLC0415
	return numpy.array(memoryview(self), dtype=dtype, copy=copy)

def _dlpack_device(self: Array) -> tuple[int, int]:
	return get_dlpack_device(self)

def _dlpack(
	self: Array, *,
	stream=None, max_version=None, dl_device=None, copy=None
):
	if stream is not None:
		raise ValueError(
			"A stream orders work on a device, and rexlib only exchanges "
			"host memory. Pass stream=None."
		)
	if dl_device is not None and tuple(dl_device) != _dlpack_device(self):
		raise BufferError(
			"The array is not on the requested device, and rexlib does not "
			"move it there. Transfer it first."
		)

	versioned = max_version is not None and max_version[0] >= 1
	source = _functional.copy(self) if copy else self
	return to_dlpack(source, versioned, bool(copy))

Array.__add__ = _binary_operator(_functional.add)
Array.__sub__ = _binary_operator(_functional.subtract)
Array.__mul__ = _binary_operator(_functional.multiply)
Array.__truediv__ = _binary_operator(_functional.divide)
Array.__mod__ = _binary_operator(_functional.modulo)

Array.__iadd__ = _in_place_operator(_functional.add)
Array.__isub__ = _in_place_operator(_functional.subtract)
Array.__imul__ = _in_place_operator(_functional.multiply)
Array.__itruediv__ = _in_place_operator(_functional.divide)
Array.__imod__ = _in_place_operator(_functional.modulo)

Array.__neg__ = _unary_operator(_functional.negate)
Array.__abs__ = _unary_operator(_functional.abs)
Array.__pos__ = _unary_operator(_functional.copy)

Array.__copy__ = _unary_operator(_functional.copy)
Array.__deepcopy__ = _deep_copy

Array.__array__ = _to_numpy
Array.__dlpack__ = _dlpack
Array.__dlpack_device__ = _dlpack_device
