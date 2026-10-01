// SPDX-License-Identifier: GPL-3.0-only

#pragma once

#include <pybind11/pybind11.h>

#include <rexlib/em/image/executor_image_source.hpp>
#include <rexlib/em/image/image_source.hpp>

#include <memory>

namespace rexlib
{

using image_source_class =
	pybind11::class_<em::image_source, std::shared_ptr<em::image_source>>;
using executor_image_source_class = pybind11::class_<
	em::executor_image_source,
	em::image_source,
	std::shared_ptr<em::executor_image_source>
>;

image_source_class declare_image_source(pybind11::module_ &m);
executor_image_source_class
declare_executor_image_source(pybind11::module_ &m);
void define_executor_image_source(executor_image_source_class &c);

} // namespace rexlib
