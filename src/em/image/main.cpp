// SPDX-License-Identifier: GPL-3.0-only

#include "main.hpp"

#include "image_descriptor.hpp"
#include "image_location.hpp"
#include "image_read.hpp"
#include "image_read_format_manager.hpp"
#include "image_reader_provider.hpp"
#include "image_source.hpp"
#include "image_write.hpp"
#include "image_write_format_manager.hpp"
#include "index_table.hpp"

namespace rexlib
{

void bind_image(pybind11::module_ &m)
{
	auto image_location = declare_image_location(m);
	auto image_descriptor = declare_image_descriptor(m);
	auto index_table = declare_index_table(m);
	declare_image_reader_provider(m);
	auto direct_provider = declare_direct_image_reader_provider(m);
	auto caching_provider = declare_caching_image_reader_provider(m);
	declare_image_source(m);
	auto executor_source = declare_executor_image_source(m);
	declare_image_read_format_manager(m);
	declare_image_write_format_manager(m);

	define_image_location(image_location);
	define_image_descriptor(image_descriptor, m);
	define_index_table(index_table);
	define_image_reader_provider(m);
	define_direct_image_reader_provider(direct_provider);
	define_caching_image_reader_provider(caching_provider);
	define_executor_image_source(executor_source);
	define_image_read_format_manager(m);
	define_image_write_format_manager(m);

	bind_image_read(m);
	bind_image_write(m);
}

} // namespace rexlib
