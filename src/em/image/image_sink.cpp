// SPDX-License-Identifier: GPL-3.0-only

#include "image_sink.hpp"

#include <rexlib/core/concurrency/executor.hpp>
#include <rexlib/em/image/image_writer_provider.hpp>

#include <memory>

namespace rexlib
{

namespace py = pybind11;

image_sink_class declare_image_sink(pybind11::module_ &m)
{
	return image_sink_class(m, "ImageSink");
}

executor_image_sink_class declare_executor_image_sink(pybind11::module_ &m)
{
	return executor_image_sink_class(m, "ExecutorImageSink");
}

void define_image_sink(image_sink_class &c)
{
	c.def(
		"flush", &em::image_sink::flush,
		py::call_guard<py::gil_scoped_release>()
	);
}

void define_executor_image_sink(executor_image_sink_class &c)
{
	c.def(
		py::init<
			std::shared_ptr<em::image_writer_provider>,
			std::shared_ptr<executor>
		>(),
		py::arg("writers"), py::arg("executor")
	);
}

} // namespace rexlib
