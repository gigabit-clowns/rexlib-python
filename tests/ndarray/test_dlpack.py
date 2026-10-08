# SPDX-License-Identifier: GPL-3.0-only

import gc

import numpy
import pytest

import rexlib

HOST = rexlib.hardware.MemoryResourceAffinity.host
CPU = (1, 0)
CUDA = (2, 0)

class Exported:
	"""Hands a capsule that already exists to a consumer of DLPack."""

	def __init__(self, capsule):
		self.capsule = capsule

	def __dlpack__(self, **_):
		return self.capsule

	def __dlpack_device__(self):
		return CPU

def test_reports_the_host_as_its_device(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	assert array.__dlpack_device__() == CPU

@pytest.mark.parametrize(
	('data_type', 'dtype'),
	[
		(rexlib.NumericalType.boolean, numpy.bool_),
		(rexlib.NumericalType.int8, numpy.int8),
		(rexlib.NumericalType.uint8, numpy.uint8),
		(rexlib.NumericalType.int16, numpy.int16),
		(rexlib.NumericalType.uint16, numpy.uint16),
		(rexlib.NumericalType.int32, numpy.int32),
		(rexlib.NumericalType.uint32, numpy.uint32),
		(rexlib.NumericalType.int64, numpy.int64),
		(rexlib.NumericalType.uint64, numpy.uint64),
		(rexlib.NumericalType.float16, numpy.float16),
		(rexlib.NumericalType.float32, numpy.float32),
		(rexlib.NumericalType.float64, numpy.float64),
		(rexlib.NumericalType.complex_float32, numpy.complex64),
		(rexlib.NumericalType.complex_float64, numpy.complex128),
	]
)
def test_numpy_sees_the_data_type(data_type, dtype, __setup_context):
	array = __setup_empty([2, 3], data_type, __setup_context)
	assert numpy.from_dlpack(array).dtype == dtype

def test_numpy_sees_the_shape_and_the_values(__setup_context):
	array = __setup_full([2, 3], 2.5, __setup_context)
	expected = numpy.full((2, 3), 2.5, dtype=numpy.float32)
	assert numpy.array_equal(numpy.from_dlpack(array), expected)

def test_the_memory_is_shared_and_not_copied(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	assert numpy.shares_memory(
		numpy.from_dlpack(array), numpy.asarray(array)
	)

def test_a_write_by_an_operation_is_seen_by_the_consumer(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	view = numpy.from_dlpack(array)
	rexlib.fill(array, 5, __setup_context)
	assert numpy.array_equal(view, numpy.full((2, 3), 5, dtype=numpy.float32))

def test_the_consumer_keeps_the_memory_alive(__setup_context):
	view = numpy.from_dlpack(__setup_ones([2, 3], __setup_context))
	gc.collect()
	assert view.sum() == 6

def test_a_capsule_nobody_takes_is_released(__setup_context):
	capsule = __setup_ones([2, 3], __setup_context).__dlpack__()
	del capsule
	gc.collect()

def test_the_capsule_is_unversioned_by_default(__setup_context):
	capsule = __setup_ones([2, 3], __setup_context).__dlpack__()
	assert '"dltensor"' in repr(capsule)

def test_the_capsule_is_unversioned_for_an_old_consumer(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	capsule = array.__dlpack__(max_version=(0, 8))
	assert '"dltensor"' in repr(capsule)

def test_the_capsule_is_versioned_for_a_consumer_that_can_take_it(
	__setup_context
):
	array = __setup_ones([2, 3], __setup_context)
	capsule = array.__dlpack__(max_version=(1, 0))
	assert '"dltensor_versioned"' in repr(capsule)

def test_numpy_takes_a_versioned_capsule(__setup_context):
	array = __setup_full([2, 3], 2.5, __setup_context)
	exported = Exported(array.__dlpack__(max_version=(1, 0)))
	expected = numpy.full((2, 3), 2.5, dtype=numpy.float32)
	assert numpy.array_equal(numpy.from_dlpack(exported), expected)

def test_the_device_the_array_is_on_can_be_asked_for(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	exported = Exported(array.__dlpack__(dl_device=CPU))
	assert numpy.from_dlpack(exported).shape == (2, 3)

def test_another_device_is_refused(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	with pytest.raises(BufferError):
		array.__dlpack__(dl_device=CUDA)

def test_a_stream_is_refused(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	with pytest.raises(ValueError, match='stream'):
		array.__dlpack__(stream=1)

def test_a_copy_is_made_when_asked_for(__setup_context):
	array = __setup_ones([2, 3], __setup_context)
	with rexlib.device('cpu'):
		exported = Exported(array.__dlpack__(copy=True))
	copied = numpy.from_dlpack(exported)
	assert numpy.array_equal(copied, numpy.ones((2, 3), dtype=numpy.float32))
	assert not numpy.shares_memory(copied, numpy.asarray(array))

def test_a_type_dlpack_cannot_name_is_refused(__setup_context):
	array = __setup_empty(
		[2, 3], rexlib.NumericalType.char8, __setup_context
	)
	with pytest.raises(BufferError):
		array.__dlpack__()

def test_torch_shares_the_memory(__setup_context):
	torch = pytest.importorskip('torch')
	array = __setup_full([2, 3], 2.5, __setup_context)
	tensor = torch.from_dlpack(array)
	assert tensor.shape == (2, 3)
	assert tensor.dtype == torch.float32
	assert bool((tensor == 2.5).all())
	tensor[0, 0] = 7
	assert numpy.asarray(array)[0, 0] == 7

def test_jax_reads_the_values(__setup_context):
	jax_numpy = pytest.importorskip('jax.numpy')
	array = __setup_full([2, 3], 2.5, __setup_context)
	values = jax_numpy.from_dlpack(array)
	assert values.shape == (2, 3)
	assert bool((values == 2.5).all())

def __setup_empty(shape, data_type, context):
	descriptor = rexlib.make_contiguous_array_descriptor(shape, data_type)
	return rexlib.empty(descriptor, HOST, context)

def __setup_ones(shape, context):
	descriptor = rexlib.make_contiguous_array_descriptor(
		shape, rexlib.NumericalType.float32
	)
	return rexlib.ones(descriptor, HOST, context)

def __setup_full(shape, value, context):
	descriptor = rexlib.make_contiguous_array_descriptor(
		shape, rexlib.NumericalType.float32
	)
	return rexlib.full(descriptor, HOST, value, context)

@pytest.fixture
def __setup_context():
	catalog = rexlib.ServiceCatalog()
	manager = rexlib.hardware.get_device_manager(catalog)
	session = manager.create_device_session(
		rexlib.hardware.DeviceIndex('cpu', 0)
	)
	device_context = rexlib.hardware.DeviceContext(session)
	program_manager = rexlib.dispatch.get_program_manager(catalog)
	dispatcher = rexlib.dispatch.make_eager_dispatcher(program_manager)
	return rexlib.dispatch.ExecutionContext(device_context, dispatcher)
