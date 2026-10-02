// SPDX-License-Identifier: GPL-3.0-only

#include "index_table.hpp"

#include <rexlib/core/span.hpp>

#include <pybind11/stl.h>

#include <cstddef>
#include <vector>

namespace rexlib
{

namespace py = pybind11;

static void py_add(index_table &self, const std::vector<std::size_t> &index)
{
	self.add(make_span(index));
}

static py::tuple py_get(const index_table &self, std::size_t position)
{
	if (position >= self.get_index_count())
	{
		throw py::index_error("IndexTable index out of range");
	}

	const auto index = self.get(position);
	py::tuple result(index.size());
	for (std::size_t i = 0; i < index.size(); ++i)
	{
		result[i] = index[i];
	}
	return result;
}

index_table_class declare_index_table(pybind11::module_ &m)
{
	return index_table_class(m, "IndexTable");
}

void define_index_table(index_table_class &c)
{
	c
		.def(py::init<>())
		.def(py::init<std::size_t>(), py::arg("rank"))
		.def("add", &py_add, py::arg("index"))
		.def("clear", &index_table::clear)
		.def("reserve", &index_table::reserve, py::arg("count"))
		.def_property_readonly("rank", &index_table::get_rank)
		.def("__len__", &index_table::get_index_count)
		.def("__getitem__", &py_get, py::arg("position"));
}

} // namespace rexlib
