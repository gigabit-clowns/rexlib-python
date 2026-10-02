# SPDX-License-Identifier: GPL-3.0-only

import pytest

import rexlib

IndexTable = rexlib.IndexTable

def test_default_holds_indices_of_no_coordinates():
	table = IndexTable()
	assert table.rank == 0
	assert len(table) == 0

def test_keeps_the_rank_it_was_given():
	assert IndexTable(3).rank == 3

def test_rank_is_accepted_by_name():
	assert IndexTable(rank=2).rank == 2

def test_starts_empty():
	assert len(IndexTable(2)) == 0

def test_added_indices_are_read_back_in_order():
	table = IndexTable(2)
	table.add((10, 20))
	table.add((30, 40))
	assert len(table) == 2
	assert table[0] == (10, 20)
	assert table[1] == (30, 40)

def test_an_index_is_a_tuple():
	table = IndexTable(2)
	table.add([10, 20])
	assert isinstance(table[0], tuple)

@pytest.mark.parametrize(
	"index",
	[
		pytest.param([10, 20], id="List"),
		pytest.param((10, 20), id="Tuple"),
		pytest.param(range(10, 12), id="Range"),
	]
)
def test_accepts_any_sequence_as_an_index(index):
	table = IndexTable(2)
	table.add(index)
	assert table[0] == tuple(index)

def test_an_index_of_another_rank_is_refused():
	table = IndexTable(2)
	with pytest.raises(ValueError):
		table.add((10, 20, 30))

def test_reading_past_the_end_raises_index_error():
	table = IndexTable(2)
	table.add((10, 20))
	with pytest.raises(IndexError):
		table[1]

def test_can_be_iterated():
	table = IndexTable(2)
	table.add((10, 20))
	table.add((30, 40))
	assert list(table) == [(10, 20), (30, 40)]

def test_clear_drops_the_indices_and_keeps_the_rank():
	table = IndexTable(2)
	table.add((10, 20))
	table.clear()
	assert len(table) == 0
	assert table.rank == 2

def test_reserve_holds_no_index():
	table = IndexTable(2)
	table.reserve(16)
	assert len(table) == 0
