// SPDX-License-Identifier: GPL-3.0-only

#include "image_source.hpp"

#include <rexlib/core/concurrency/executor.hpp>
#include <rexlib/em/image/image_reader_provider.hpp>

#include <memory>

namespace rexlib
{

namespace py = pybind11;

image_source_class declare_image_source(pybind11::module_ &m)
{
	return image_source_class(m, "ImageSource");
}

executor_image_source_class
declare_executor_image_source(pybind11::module_ &m)
{
	return executor_image_source_class(m, "ExecutorImageSource");
}

void define_executor_image_source(executor_image_source_class &c)
{
	c.def(
		py::init<
			std::shared_ptr<em::image_reader_provider>,
			std::shared_ptr<executor>
		>(),
		py::arg("readers"), py::arg("executor")
	);
}

} // namespace rexlib
