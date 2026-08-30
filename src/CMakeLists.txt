cmake_minimum_required(VERSION 3.16)

# Register all source and header files
file(GLOB_RECURSE SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp ${CMAKE_CURRENT_SOURCE_DIR}/*.c)
file(GLOB_RECURSE HEADERS ${PROJECT_SOURCE_DIR}/include/*.h ${PROJECT_SOURCE_DIR}/include/*.hpp)
file(GLOB_RECURSE INLINE_SOURCES ${PROJECT_SOURCE_DIR}/include/*.inl)

# Create the shared library
set(TARGET_NAME "_binding")
pybind11_add_module(${TARGET_NAME} ${SOURCES})

# librexlib ships in lib/ inside this package, so the loader resolves it
# from the extension's own location. Windows needs nothing: the DLL sits
# beside the .pyd and CPython loads extensions with
# LOAD_WITH_ALTERED_SEARCH_PATH.
if(APPLE)
	set_target_properties(
		${TARGET_NAME}
		PROPERTIES INSTALL_RPATH "@loader_path/lib"
	)
elseif(UNIX)
	set_target_properties(
		${TARGET_NAME}
		PROPERTIES INSTALL_RPATH "$ORIGIN/lib"
	)
endif()

target_link_libraries(
	${TARGET_NAME}
	PRIVATE 
		rexlib::rexlib
)
if(MSVC)
	target_compile_options(${TARGET_NAME} PRIVATE /W4 /WX)
else()
	target_compile_options(${TARGET_NAME} PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Install library's binary files and headers
if(REXLIB_PYTHON_INSTALL)
	install(
		TARGETS ${TARGET_NAME}
		LIBRARY
		DESTINATION "${REXLIB_PYTHON_PACKAGE_DIR}"
	)
endif()
