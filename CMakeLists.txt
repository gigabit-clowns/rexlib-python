cmake_minimum_required(VERSION 3.18)

# Define the project
file(READ ${CMAKE_CURRENT_SOURCE_DIR}/VERSION PROJECT_VERSION)
string(STRIP "${PROJECT_VERSION}" PROJECT_VERSION)
project(
  rexlib-python
	VERSION ${PROJECT_VERSION}
	LANGUAGES C CXX
)

# Include CTest to provide BUILD_TESTING option
include(CTest)

# Several of Boost's sub-libraries write BUILD_TESTING into the cache, so
# fetching rexlib turns this project's own tests off behind our back.
# Capture what was asked for before that can happen.
set(REXLIB_PYTHON_BUILD_TESTING ${BUILD_TESTING})
include(FetchContent)
include(GNUInstallDirs)

# Declare build options
#option(REXLIB_PYTHON_BUILD_DOC "Build documentation" ON)

# The version is the compatibility contract; the commit is only used by
# the bootstrap, when nothing is installed.
set(REXLIB_PYTHON_REXLIB_VERSION 0.1 CACHE STRING
	"Version of rexlib this binding requires")
set(REXLIB_PYTHON_REXLIB_COMMIT 474ba80d27c7ace6979b7193db53b3d481804885
	CACHE STRING "Commit the bootstrap builds when rexlib is not installed")
option(REXLIB_PYTHON_BOOTSTRAP
	"Build and install rexlib into the build tree when it is not found" OFF)

# Set the module path
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)

include(find_rexlib)
include(stage_rexlib)

# Most of a build here is the C++ library, so use a compiler cache when one
# is available.
# Skipped for MSVC, where ccache needs the debug information format
# pinned to work at all.
if(NOT DEFINED CMAKE_CXX_COMPILER_LAUNCHER AND NOT MSVC)
	find_program(REXLIB_PYTHON_CCACHE ccache)
	if(REXLIB_PYTHON_CCACHE)
		message(STATUS "Compiler cache: ${REXLIB_PYTHON_CCACHE}")
		set(CMAKE_C_COMPILER_LAUNCHER "${REXLIB_PYTHON_CCACHE}")
		set(CMAKE_CXX_COMPILER_LAUNCHER "${REXLIB_PYTHON_CCACHE}")
	endif()
endif()

# Find Python
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Obtain pybind11
FetchContent_Declare(
	pybind11
	GIT_REPOSITORY https://github.com/pybind/pybind11
	GIT_TAG v3.1.0
)
FetchContent_MakeAvailable(pybind11)

# Find the rexlib installation this binding wraps and carry it inside
# the wheel; the core repository ships no Python packaging of its own.
if (NOT TARGET rexlib::rexlib)
	find_rexlib(
		VERSION ${REXLIB_PYTHON_REXLIB_VERSION}
		COMMIT ${REXLIB_PYTHON_REXLIB_COMMIT}
	)
endif()

if(SKBUILD_PLATLIB_DIR)
	set(PYTHON_INSTALL_DIR "${SKBUILD_PLATLIB_DIR}")
else()
	set(PYTHON_INSTALL_DIR "${Python_SITEARCH}")
endif()

# Anchors everything installed into the package, rexlib included.
set(REXLIB_PYTHON_PACKAGE_DIR "${PYTHON_INSTALL_DIR}/rexlib")

# Carry the rexlib installation inside the package.
stage_rexlib("${REXLIB_PYTHON_PACKAGE_DIR}")

# Set project-wide compilation options
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED OFF)

# Add sources
add_subdirectory(src)

# Only build docs if it is the main project
#if(BUILD_DOC)
#	add_subdirectory(doc)
#endif()

# Only build tests if it is the main project
if(REXLIB_PYTHON_BUILD_TESTING)
	add_subdirectory(tests)
endif()

# Install python directory
install(DIRECTORY
	${CMAKE_CURRENT_SOURCE_DIR}/python/rexlib/
	DESTINATION "${REXLIB_PYTHON_PACKAGE_DIR}"
	PATTERN "__pycache__" EXCLUDE
)

# Type stubs are generated from the extension that was just installed, so
# this has to come after everything the import needs is in place.
#
# Generating them requires importing the extension, which a cross-compiling
# build cannot do. Those builds get stubs handed to them through
# REXLIB_STUBS_DIR instead; the stubs describe the Python API, which is the
# same whatever the target architecture.
set(REXLIB_STUBS_DIR "" CACHE PATH
	"Directory holding pre-generated stubs, for builds that cannot import \
the extension they produce. Generated during the build when empty.")

set(REXLIB_STUB_DESTINATION "${REXLIB_PYTHON_PACKAGE_DIR}/_binding")

# Relative to the project, so that the same value works on a runner and
# inside a build container, where the project is mounted elsewhere.
if(REXLIB_STUBS_DIR AND NOT IS_ABSOLUTE "${REXLIB_STUBS_DIR}")
	set(REXLIB_STUBS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/${REXLIB_STUBS_DIR}")
endif()

if(REXLIB_STUBS_DIR)
	# Stubs are not needed at run time, so shipping none of them would go
	# unnoticed until somebody wondered why their editor stopped helping.
	file(GLOB REXLIB_PROVIDED_STUBS "${REXLIB_STUBS_DIR}/*.pyi")
	if(NOT REXLIB_PROVIDED_STUBS)
		message(FATAL_ERROR
			"REXLIB_STUBS_DIR is set to '${REXLIB_STUBS_DIR}', which holds no "
			".pyi files."
		)
	endif()

	install(DIRECTORY "${REXLIB_STUBS_DIR}/"
		DESTINATION "${REXLIB_STUB_DESTINATION}"
		FILES_MATCHING PATTERN "*.pyi"
	)
else()
	install(CODE "
		execute_process(
			COMMAND \"${Python_EXECUTABLE}\"
				\"${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_stubs.py\"
				--module rexlib._binding
				--search-path \"${PYTHON_INSTALL_DIR}\"
				--output \"${REXLIB_STUB_DESTINATION}\"
			RESULT_VARIABLE REXLIB_STUBGEN_RESULT
		)
		if(NOT REXLIB_STUBGEN_RESULT EQUAL 0)
			message(FATAL_ERROR
				\"Could not generate the type stubs. Pass REXLIB_STUBS_DIR \"
				\"when the extension cannot be imported by the build.\"
			)
		endif()
	")
endif()
