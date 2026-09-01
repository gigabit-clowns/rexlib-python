// SPDX-License-Identifier: GPL-3.0-only

#pragma once

#include <pybind11/pybind11.h>

#include <rexlib/core/ndarray/array.hpp>

#include <memory>

namespace rexlib
{
namespace ndarray
{

using array_class = pybind11::class_<array>;

array_class declare_array(pybind11::module_ &m);

} // namespace ndarray
} // namespace rexlib
