// SPDX-License-Identifier: GPL-3.0-only

#include "image_write.hpp"

#include <rexlib/em/image/image_write.hpp>

#include <rexlib/core/ndarray/array.hpp>
#include <rexlib/core/numerical/numerical_type.hpp>
#include <rexlib/em/image/image_descriptor.hpp>
#include <rexlib/em/image/image_write_format_manager.hpp>

#include <pybind11/stl.h>

#include <optional>
#include <string>

namespace rexlib
{

namespace py = pybind11;

static void py_write_single(
	const array &arr,
	const std::string &path,
	const em::image_write_format_manager &manager,
	std::optional<numerical_type> data_type
)
{
	em::write_single(
		arr,
		path,
		manager,
		data_type.value_or(numerical_type::unknown)
	);
}

static void py_write_stack(
	const array &arr,
	const std::string &path,
	const em::image_write_format_manager &manager,
	std::optional<numerical_type> data_type
)
{
	em::write_stack(
		arr,
		path,
		manager,
		data_type.value_or(numerical_type::unknown)
	);
}

static void py_write(
	const array &arr,
	const std::string &path,
	const em::image_write_format_manager &manager,
	const em::image_descriptor &descriptor
)
{
	em::write(arr, path, manager, descriptor);
}

void bind_image_write(pybind11::module_ &m)
{
	m.def(
		"write_single", &py_write_single,
		py::arg("array"), py::arg("path"), py::arg("manager"),
		py::arg("data_type") = py::none(),
		py::call_guard<py::gil_scoped_release>()
	);
	m.def(
		"write_stack", &py_write_stack,
		py::arg("array"), py::arg("path"), py::arg("manager"),
		py::arg("data_type") = py::none(),
		py::call_guard<py::gil_scoped_release>()
	);
	m.def(
		"write", &py_write,
		py::arg("array"), py::arg("path"), py::arg("manager"),
		py::arg("descriptor"),
		py::call_guard<py::gil_scoped_release>()
	);
}

} // namespace rexlib
