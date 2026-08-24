// SPDX-License-Identifier: GPL-3.0-only

#include "main.hpp"

#include "numerical_type.hpp"

namespace rexlib
{
namespace numerical
{

void bind_numerical(pybind11::module_ &m)
{
	auto numerical_type = declare_numerical_type(m);
	define_numerical_type(numerical_type);
}

} // namespace numerical
} // namespace rexlib
