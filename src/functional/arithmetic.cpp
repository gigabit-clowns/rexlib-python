// SPDX-License-Identifier: GPL-3.0-only

#include "arithmetic.hpp"

#include <rexlib/functional/arithmetic.hpp>
#include <rexlib/core/ndarray/array.hpp>
#include <rexlib/core/dispatch/execution_context.hpp>

#include <nanobind/stl/optional.h>

#include <optional>

namespace rexlib
{

namespace nb = nanobind;

static array py_add(const array &x, const array &y, const execution_context &context, std::optional<array*> out)
{
	return rexlib::add(x, y, context, out.value_or(nullptr));
}

static array py_subtract(const array &x, const array &y, const execution_context &context, std::optional<array*> out)
{
	return rexlib::subtract(x, y, context, out.value_or(nullptr));
}

static array py_negate(const array &x, const execution_context &context, std::optional<array*> out)
{
	return rexlib::negate(x, context, out.value_or(nullptr));
}

static array py_abs(const array &x, const execution_context &context, std::optional<array*> out)
{
	return rexlib::abs(x, context, out.value_or(nullptr));
}

static array py_multiply(const array &x, const array &y, const execution_context &context, std::optional<array*> out)
{
	return rexlib::multiply(x, y, context, out.value_or(nullptr));
}

static array py_divide(const array &x, const array &y, const execution_context &context, std::optional<array*> out)
{
	return rexlib::divide(x, y, context, out.value_or(nullptr));
}

static array py_modulo(const array &x, const array &y, const execution_context &context, std::optional<array*> out)
{
	return rexlib::modulo(x, y, context, out.value_or(nullptr));
}

void bind_arithmetic(nanobind::module_ &m)
{
	m.def(
		"add", &py_add,
		nb::arg("x"), nb::arg("y"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"subtract", &py_subtract,
		nb::arg("x"), nb::arg("y"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"negate", &py_negate,
		nb::arg("x"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"abs", &py_abs,
		nb::arg("x"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"multiply", &py_multiply,
		nb::arg("x"), nb::arg("y"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"divide", &py_divide,
		nb::arg("x"), nb::arg("y"), nb::arg("context"), nb::arg("out") = nb::none()
	);
	m.def(
		"modulo", &py_modulo,
		nb::arg("x"), nb::arg("y"), nb::arg("context"), nb::arg("out") = nb::none()
	);
}

} // namespace rexlib
