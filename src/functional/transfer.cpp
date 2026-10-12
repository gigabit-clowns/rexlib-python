// SPDX-License-Identifier: GPL-3.0-only

#include "transfer.hpp"

#include <rexlib/functional/transfer.hpp>
#include <rexlib/core/ndarray/array.hpp>
#include <rexlib/core/hardware/memory_resource_affinity.hpp>
#include <rexlib/core/dispatch/execution_context.hpp>

#include <nanobind/stl/optional.h>

#include <optional>

namespace rexlib
{

namespace nb = nanobind;

static array py_transfer_copy(
	const array &input,
	memory_resource_affinity affinity,
	const execution_context &context,
	std::optional<array*> out
)
{
	return rexlib::transfer_copy(input, affinity, context, out.value_or(nullptr));
}

static array py_to_device_copy(const array &input, const execution_context &context, std::optional<array*> out)
{
	return rexlib::to_device_copy(input, context, out.value_or(nullptr));
}

static array py_to_host_copy(const array &input, const execution_context &context, std::optional<array*> out)
{
	return rexlib::to_host_copy(input, context, out.value_or(nullptr));
}

void bind_transfer(nanobind::module_ &m)
{
	m.def(
		"transfer",
		&rexlib::transfer,
		nb::arg("input"), nb::arg("affinity"), nb::arg("context")
	);
	m.def(
		"transfer_copy", &py_transfer_copy,
		nb::arg("input"), nb::arg("affinity"), nb::arg("context"),
		nb::arg("out") = nb::none()
	);
	m.def(
		"to_device",
		&rexlib::to_device,
		nb::arg("input"), nb::arg("context")
	);
	m.def(
		"to_device_copy", &py_to_device_copy,
		nb::arg("input"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"to_host",
		&rexlib::to_host,
		nb::arg("input"), nb::arg("context")
	);
	m.def(
		"to_host_copy", &py_to_host_copy,
		nb::arg("input"), nb::arg("context"), nb::arg("out") = nb::none()
	);
}

} // namespace rexlib
