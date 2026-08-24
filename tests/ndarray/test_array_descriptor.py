# SPDX-License-Identifier: GPL-3.0-only

import rexlib

def test_default_descriptor_is_not_initialized():
	descriptor = rexlib.ndarray.ArrayDescriptor()
	assert not rexlib.ndarray.is_initialized(descriptor)

def test_contiguous_descriptor_has_requested_data_type():
	descriptor = rexlib.ndarray.make_contiguous_array_descriptor(
		[2, 3], rexlib.numerical.NumericalType.float32
	)
	assert rexlib.ndarray.is_initialized(descriptor)
	assert descriptor.data_type == rexlib.numerical.NumericalType.float32

def test_equal_descriptors_compare_equal():
	d1 = rexlib.ndarray.make_contiguous_array_descriptor(
		[2, 3], rexlib.numerical.NumericalType.int32
	)
	d2 = rexlib.ndarray.make_contiguous_array_descriptor(
		[2, 3], rexlib.numerical.NumericalType.int32
	)
	assert d1 == d2

def test_different_descriptors_compare_not_equal():
	d1 = rexlib.ndarray.make_contiguous_array_descriptor(
		[2, 3], rexlib.numerical.NumericalType.int32
	)
	d2 = rexlib.ndarray.make_contiguous_array_descriptor(
		[3, 2], rexlib.numerical.NumericalType.int32
	)
	assert d1 != d2
