# SPDX-License-Identifier: GPL-3.0-only

import pytest

import rexlib

def test_empty_returns_array(__setup_context):
	result = rexlib.functional.empty(
		__setup_descriptor(),
		rexlib.hardware.MemoryResourceAffinity.host,
		__setup_context
	)
	assert isinstance(result, rexlib.ndarray.Array)

def test_zeros_returns_array(__setup_context):
	result = rexlib.functional.zeros(
		__setup_descriptor(),
		rexlib.hardware.MemoryResourceAffinity.host,
		__setup_context
	)
	assert isinstance(result, rexlib.ndarray.Array)

def test_ones_returns_array(__setup_context):
	result = rexlib.functional.ones(
		__setup_descriptor(),
		rexlib.hardware.MemoryResourceAffinity.host,
		__setup_context
	)
	assert isinstance(result, rexlib.ndarray.Array)

def test_full_returns_array(__setup_context):
	result = rexlib.functional.full(
		__setup_descriptor(),
		rexlib.hardware.MemoryResourceAffinity.host,
		3.5,
		__setup_context
	)
	assert isinstance(result, rexlib.ndarray.Array)

def test_full_supports_float16(__setup_context):
	descriptor = rexlib.ndarray.make_contiguous_array_descriptor(
		[2, 2], rexlib.numerical.NumericalType.float16
	)
	result = rexlib.functional.full(
		descriptor,
		rexlib.hardware.MemoryResourceAffinity.host,
		1.5,
		__setup_context
	)
	assert isinstance(result, rexlib.ndarray.Array)

def test_copy_returns_array(__setup_context):
	source = rexlib.functional.zeros(
		__setup_descriptor(),
		rexlib.hardware.MemoryResourceAffinity.host,
		__setup_context
	)
	result = rexlib.functional.copy(source, __setup_context)
	assert isinstance(result, rexlib.ndarray.Array)

def test_fill_does_not_raise(__setup_context):
	target = rexlib.functional.empty(
		__setup_descriptor(),
		rexlib.hardware.MemoryResourceAffinity.host,
		__setup_context
	)
	rexlib.functional.fill(target, 7.0, __setup_context)

def __setup_descriptor():
	return rexlib.ndarray.make_contiguous_array_descriptor(
		[2, 3], rexlib.numerical.NumericalType.float32
	)

@pytest.fixture
def __setup_context():
	catalog = rexlib.ServiceCatalog()
	manager = rexlib.hardware.get_device_manager(catalog)
	session = manager.create_device_session(rexlib.hardware.DeviceIndex('cpu', 0))
	device_context = rexlib.hardware.DeviceContext(session)
	program_manager = rexlib.dispatch.get_program_manager(catalog)
	dispatcher = rexlib.dispatch.make_eager_dispatcher(program_manager)
	return rexlib.dispatch.ExecutionContext(device_context, dispatcher)
