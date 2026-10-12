// SPDX-License-Identifier: GPL-3.0-only

#include "cast.hpp"

#include <rexlib/functional/cast.hpp>
#include <rexlib/core/ndarray/array.hpp>
#include <rexlib/core/numerical/numerical_type.hpp>
#include <rexlib/core/dispatch/execution_context.hpp>

#include <nanobind/stl/optional.h>

#include <optional>

namespace rexlib
{

namespace nb = nanobind;

static array py_cast_copy(
	const array &input,
	numerical_type target_type,
	const execution_context &context,
	std::optional<array*> out
)
{
	return rexlib::cast_copy(input, target_type, context, out.value_or(nullptr));
}

void bind_cast(nanobind::module_ &m)
{
	m.def(
		"cast",
		&rexlib::cast,
		nb::arg("input"), nb::arg("target_type"), nb::arg("context")
	);
	m.def(
		"cast_copy", &py_cast_copy,
		nb::arg("input"), nb::arg("target_type"), nb::arg("context"),
		nb::arg("out") = nb::none()
	);
}

} // namespace rexlib
