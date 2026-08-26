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

# Set the module path
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)

include(fetch_rexlib)

# Most of a build here is the C++ library, so use a compiler cache when one
# is available. Detected rather than demanded: a missing ccache degrades to
# an ordinary build instead of failing every compile, which is what setting
# CMAKE_CXX_COMPILER_LAUNCHER from the outside would do. Set before rexlib
# is added so the subproject inherits it.
# Skipped for MSVC, where ccache needs the debug information format
# pinned to work at all. The runners carry an unrelated ccache.exe in
# Strawberry Perl's bin directory, which a plain search would find.
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

# Build rexlib and stage it inside the Python package. The wheel carries
# the library it was built against rather than depending on a separate
# one; the core repository ships no Python packaging of its own.
#
# The guard leaves a superbuild that already provides the target alone.
#
# Pinned by commit because rexlib publishes no release tags yet: its only
# tag is "development", which its CI force-moves on every push to main, so
# pinning it would mean the same wheel version silently containing
# different libraries. Switch to VERSION once releases are cut - the
# module already takes it, and Renovate can then track it the way it
# tracks pybind11 below.
#
# TODO: re-pin once gigabit-clowns/rexlib#427 merges; this SHA is on a
# branch and a squash-merge would orphan it.
if (NOT TARGET rexlib::rexlib)
	fetch_rexlib(
		COMMIT 1d9a608fd1a1a35fc7b29ae2d041a42ccc6f1b6e
		DESTINATION rexlib
	)
endif()

if(SKBUILD_PLATLIB_DIR)
	set(PYTHON_INSTALL_DIR "${SKBUILD_PLATLIB_DIR}")
else()
	set(PYTHON_INSTALL_DIR "${Python_SITEARCH}")
endif()

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
	DESTINATION "${PYTHON_INSTALL_DIR}/rexlib"
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

set(REXLIB_STUB_DESTINATION "${PYTHON_INSTALL_DIR}/rexlib/_binding")

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
