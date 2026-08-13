// SPDX-License-Identifier: GPL-3.0-only

#include "main.hpp"

#include "array.hpp"
#include "array_descriptor.hpp"

namespace xmipp4
{
namespace ndarray
{

void bind_ndarray(pybind11::module_ &m)
{
	// Every type is registered before any of them defines a member, so that
	// pybind11 can resolve cross-references in signatures whichever way they
	// point, which makes the order below irrelevant.
	declare_array(m);
	auto array_descriptor = declare_array_descriptor(m);

	define_array_descriptor(array_descriptor, m);
}

} // namespace ndarray
} // namespace xmipp4
