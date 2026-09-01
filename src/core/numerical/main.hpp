// SPDX-License-Identifier: GPL-3.0-only

#pragma once

#include <pybind11/pybind11.h>

namespace rexlib
{
namespace numerical
{

void bind_numerical(pybind11::module_ &m);

} // namespace numerical
} // namespace rexlib
