// SPDX-License-Identifier: GPL-3.0-only

#pragma once

#include <pybind11/pybind11.h>

#include <rexlib/em/image/executor_image_sink.hpp>
#include <rexlib/em/image/image_sink.hpp>

#include <memory>

namespace rexlib
{

using image_sink_class =
	pybind11::class_<em::image_sink, std::shared_ptr<em::image_sink>>;
using executor_image_sink_class = pybind11::class_<
	em::executor_image_sink,
	em::image_sink,
	std::shared_ptr<em::executor_image_sink>
>;

image_sink_class declare_image_sink(pybind11::module_ &m);
executor_image_sink_class declare_executor_image_sink(pybind11::module_ &m);
void define_image_sink(image_sink_class &c);
void define_executor_image_sink(executor_image_sink_class &c);

} // namespace rexlib
