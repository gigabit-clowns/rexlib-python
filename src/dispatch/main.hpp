// SPDX-License-Identifier: GPL-3.0-only

#pragma once

#include <pybind11/pybind11.h>

namespace rexlib
{
namespace dispatch
{

void bind_dispatch(pybind11::module_ &m);

} // namespace dispatch
} // namespace rexlib
