# SPDX-License-Identifier: GPL-3.0-only

import xmipp4

def test_no_active_context_by_default():
	assert xmipp4.get_active_execution_context() is None

def test_device_activates_context_for_the_duration_of_the_block():
	assert xmipp4.get_active_execution_context() is None
	with xmipp4.device('cpu') as ctx:
		assert xmipp4.get_active_execution_context() is ctx
	assert xmipp4.get_active_execution_context() is None

def test_device_accepts_a_device_index():
	index = xmipp4.hardware.DeviceIndex('cpu', 0)
	with xmipp4.device(index) as ctx:
		assert xmipp4.get_active_execution_context() is ctx

def test_nested_device_restores_the_outer_context():
	with xmipp4.device('cpu') as outer:
		with xmipp4.device('cpu') as inner:
			assert xmipp4.get_active_execution_context() is inner
			assert inner is not outer
		assert xmipp4.get_active_execution_context() is outer
	assert xmipp4.get_active_execution_context() is None

def test_device_restores_previous_context_on_exception():
	with xmipp4.device('cpu') as outer:
		try:
			with xmipp4.device('cpu'):
				raise ValueError('boom')
		except ValueError:
			pass
		assert xmipp4.get_active_execution_context() is outer

def test_nested_device_preserves_the_outer_dispatcher():
	with xmipp4.device('cpu') as outer, xmipp4.device('cpu') as inner:
		assert inner.dispatcher is outer.dispatcher
		assert inner.device_context is not outer.device_context
