// SPDX-License-Identifier: GPL-3.0-only

#include "dlpack.hpp"

#include <rexlib/core/hardware/buffer.hpp>
#include <rexlib/core/hardware/memory_resource.hpp>
#include <rexlib/core/hardware/memory_resource_kind.hpp>
#include <rexlib/core/layout/strided_layout.hpp>
#include <rexlib/core/ndarray/array.hpp>
#include <rexlib/core/ndarray/array_descriptor.hpp>
#include <rexlib/core/ndarray/array_ref.hpp>
#include <rexlib/core/ndarray/host_access.hpp>
#include <rexlib/core/numerical/numerical_type.hpp>

#include <dlpack/dlpack.h>

#include <cstddef>
#include <cstdint>
#include <memory>
#include <sstream>
#include <vector>

namespace rexlib
{

namespace py = pybind11;

namespace
{

const char* get_capsule_name(const DLManagedTensor* /*tag*/) noexcept
{
	return "dltensor";
}

const char* get_capsule_name(const DLManagedTensorVersioned* /*tag*/) noexcept
{
	return "dltensor_versioned";
}

void set_version_and_flags(
	DLManagedTensor& /*managed*/,
	std::uint64_t /*flags*/
) noexcept
{
}

void set_version_and_flags(
	DLManagedTensorVersioned &managed,
	std::uint64_t flags
) noexcept
{
	managed.version.major = DLPACK_MAJOR_VERSION;
	managed.version.minor = DLPACK_MINOR_VERSION;
	managed.flags = flags;
}

DLDataType get_dlpack_data_type(numerical_type type)
{
	DLDataType result;
	result.bits = static_cast<std::uint8_t>(8 * get_size(type));
	result.lanes = 1;

	switch (get_category(type))
	{
	case numerical_type_category::boolean:
		result.code = kDLBool;
		break;
	case numerical_type_category::signed_integer:
		result.code = kDLInt;
		break;
	case numerical_type_category::unsigned_integer:
		result.code = kDLUInt;
		break;
	case numerical_type_category::floating_point:
		result.code = kDLFloat;
		break;
	case numerical_type_category::complex:
		result.code = kDLComplex;
		break;
	default:
		{
			std::ostringstream oss;
			oss << "DLPack has no data type for " << type << ".";
			throw py::buffer_error(oss.str());
		}
	}

	return result;
}

/**
 * A tensor handed out through DLPack, with what it points to: the storage
 * it shares and the shape and strides that describe it.
 */
template <typename Managed>
class dlpack_export
{
public:
	dlpack_export(array &source, void *data, std::uint64_t flags);
	dlpack_export(const dlpack_export &other) = delete;
	dlpack_export(dlpack_export &&other) = delete;
	~dlpack_export() = default;

	dlpack_export& operator=(const dlpack_export &other) = delete;
	dlpack_export& operator=(dlpack_export &&other) = delete;

	Managed* get_managed() noexcept;

private:
	std::shared_ptr<buffer> m_storage;
	std::vector<std::int64_t> m_shape;
	std::vector<std::int64_t> m_strides;
	Managed m_managed;

	static void destroy(Managed *managed);
};

template <typename Managed>
dlpack_export<Managed>::dlpack_export(
	array &source,
	void *data,
	std::uint64_t flags
)
	: m_storage(source.share_storage())
	, m_managed()
{
	const auto &descriptor = source.get_descriptor();
	const auto &layout = descriptor.get_layout();
	const auto data_type = descriptor.get_data_type();

	std::vector<std::size_t> extents;
	layout.get_extents(extents);
	m_shape.assign(extents.cbegin(), extents.cend());

	std::vector<std::ptrdiff_t> strides;
	layout.get_strides(strides);
	m_strides.assign(strides.cbegin(), strides.cend());

	const auto first_byte =
		layout.get_offset() * static_cast<std::ptrdiff_t>(get_size(data_type));

	auto &tensor = m_managed.dl_tensor;
	tensor.data = static_cast<char*>(data) + first_byte;
	tensor.device.device_type = kDLCPU;
	tensor.device.device_id = 0;
	tensor.ndim = static_cast<std::int32_t>(m_shape.size());
	tensor.dtype = get_dlpack_data_type(data_type);
	tensor.shape = m_shape.data();
	tensor.strides = m_strides.data();
	tensor.byte_offset = 0;

	set_version_and_flags(m_managed, flags);
	m_managed.manager_ctx = this;
	m_managed.deleter = &destroy;
}

template <typename Managed>
Managed* dlpack_export<Managed>::get_managed() noexcept
{
	return &m_managed;
}

template <typename Managed>
void dlpack_export<Managed>::destroy(Managed *managed)
{
	delete static_cast<dlpack_export*>(managed->manager_ctx);
}

template <typename Managed>
void destroy_capsule(PyObject *capsule)
{
	const auto *name = get_capsule_name(static_cast<const Managed*>(nullptr));

	// A consumer renames the capsule when it takes the tensor over.
	if (PyCapsule_IsValid(capsule, name) != 0)
	{
		auto *managed =
			static_cast<Managed*>(PyCapsule_GetPointer(capsule, name));
		managed->deleter(managed);
	}
}

template <typename Managed>
py::capsule make_capsule(array &source, void *data, std::uint64_t flags)
{
	auto exported =
		std::make_unique<dlpack_export<Managed>>(source, data, flags);

	py::capsule result(
		exported->get_managed(),
		get_capsule_name(static_cast<const Managed*>(nullptr)),
		&destroy_capsule<Managed>
	);

	// The capsule owns the export from here on.
	(void)exported.release();
	return result;
}

py::capsule to_dlpack(array &source, bool versioned, bool copied)
{
	void *data = nullptr;
	{
		const py::gil_scoped_release release;
		data = get_host_data(array_ref(source));
	}

	if (versioned)
	{
		return make_capsule<DLManagedTensorVersioned>(
			source,
			data,
			copied ? DLPACK_FLAG_BITMASK_IS_COPIED : 0
		);
	}

	return make_capsule<DLManagedTensor>(source, data, 0);
}

py::tuple get_dlpack_device(const array &source)
{
	const auto *storage = source.get_storage();
	if (storage == nullptr)
	{
		throw py::buffer_error("The array is not initialized.");
	}

	if (!is_host_accessible(storage->get_memory_resource().get_kind()))
	{
		throw py::buffer_error(
			"The storage of the array can not be reached from the host, and "
			"only host memory is exchanged through DLPack."
		);
	}

	return py::make_tuple(static_cast<int>(kDLCPU), 0);
}

} // anonymous namespace

void bind_dlpack(pybind11::module_ &m)
{
	m.def(
		"to_dlpack",
		&to_dlpack,
		py::arg("array"), py::arg("versioned"), py::arg("copied")
	);
	m.def(
		"get_dlpack_device",
		&get_dlpack_device,
		py::arg("array")
	);
}

} // namespace rexlib
