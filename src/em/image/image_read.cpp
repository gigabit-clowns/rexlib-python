// SPDX-License-Identifier: GPL-3.0-only

#include "image_read.hpp"

#include <rexlib/em/image/image_read.hpp>

#include <rexlib/core/dispatch/execution_context.hpp>
#include <rexlib/core/ndarray/array.hpp>
#include <rexlib/core/numerical/numerical_type.hpp>
#include <rexlib/em/image/image_location.hpp>
#include <rexlib/em/image/image_reader_provider.hpp>

#include <pybind11/stl.h>

#include <optional>
#include <string>

namespace rexlib
{

namespace py = pybind11;

static array py_read_path(
	const std::string &path,
	em::image_reader_provider &readers,
	const execution_context &context,
	std::optional<numerical_type> data_type
)
{
	return em::read(
		path,
		readers,
		context,
		data_type.value_or(numerical_type::unknown)
	);
}

static array py_read_location(
	const em::image_location &location,
	em::image_reader_provider &readers,
	const execution_context &context,
	std::optional<numerical_type> data_type
)
{
	return em::read(
		location,
		readers,
		context,
		data_type.value_or(numerical_type::unknown)
	);
}

void bind_image_read(pybind11::module_ &m)
{
	m.def(
		"read", &py_read_path,
		py::arg("path"), py::arg("readers"), py::arg("context"),
		py::arg("data_type") = py::none(),
		py::call_guard<py::gil_scoped_release>()
	);
	m.def(
		"read", &py_read_location,
		py::arg("location"), py::arg("readers"), py::arg("context"),
		py::arg("data_type") = py::none(),
		py::call_guard<py::gil_scoped_release>()
	);
}

} // namespace rexlib
