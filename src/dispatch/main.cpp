// SPDX-License-Identifier: GPL-3.0-only

#include "main.hpp"

#include "dispatcher.hpp"
#include "execution_context.hpp"
#include "program_manager.hpp"

namespace xmipp4
{
namespace dispatch
{

void bind_dispatch(pybind11::module_ &m)
{
	// Every type is registered before any of them defines a member, so that
	// pybind11 can resolve cross-references in signatures whichever way they
	// point, which makes the order below irrelevant.
	declare_dispatcher(m);
	auto execution_context = declare_execution_context(m);
	declare_program_manager(m);

	define_dispatcher(m);
	define_execution_context(execution_context);
	define_program_manager(m);
}

} // namespace dispatch
} // namespace xmipp4
