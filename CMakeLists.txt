cmake_minimum_required(VERSION 3.21)

file(READ ${CMAKE_CURRENT_SOURCE_DIR}/VERSION PROJECT_VERSION)
string(STRIP "${PROJECT_VERSION}" PROJECT_VERSION)
project(
	rexlib-python
	VERSION ${PROJECT_VERSION}
	LANGUAGES C CXX
)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)

include(CTest)
include(find_rexlib)
include(stage_rexlib)
include(python_stubs)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# ---------------------------------------------------------------------------
# Options
#
# Everything a packaging tool, a CI job or a distributor needs to influence
# is one of these. Nothing below asks who is driving the build. Where a
# default is taken from the environment it is a default only, and setting
# the option wins.
# ---------------------------------------------------------------------------

# Its own option rather than BUILD_TESTING: dependencies of dependencies
# write that one into the cache, and this project's tests should not be at
# their mercy.
option(REXLIB_PYTHON_BUILD_TESTING "Build this project's tests" ${BUILD_TESTING})

# scikit-build-core stages a wheel elsewhere; a plain build installs into
# the interpreter that CMake found. Either way the option holds the answer.
set(DEFAULT_INSTALL_DIR "${SKBUILD_PLATLIB_DIR}")
if(NOT DEFAULT_INSTALL_DIR)
	set(DEFAULT_INSTALL_DIR "${Python_SITEARCH}")
endif()
set(REXLIB_PYTHON_INSTALL_DIR "${DEFAULT_INSTALL_DIR}" CACHE PATH
	"Directory the Python package is installed into")
unset(DEFAULT_INSTALL_DIR)

# Empty lets pybind11 take the suffix from the interpreter it found, which
# is right unless that interpreter is not the one being targeted.
# cibuildwheel publishes the target's suffix in the environment.
set(REXLIB_PYTHON_MODULE_SUFFIX "$ENV{SETUPTOOLS_EXT_SUFFIX}" CACHE STRING
	"Extension suffix, for example .cp312-win_arm64.pyd")

set(REXLIB_PYTHON_STUBS_DIR "" CACHE PATH
	"Directory of pre-generated .pyi stubs. Empty generates them, which \
requires importing the extension this build produces")

set(REXLIB_PYTHON_REXLIB_VERSION 0.1 CACHE STRING
	"Version of rexlib this binding requires")

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED OFF)

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

if(REXLIB_PYTHON_MODULE_SUFFIX)
	# Read by pybind11 when it is brought in below, which is when it
	# decides how to name the module.
	set(PYTHON_MODULE_EXTENSION "${REXLIB_PYTHON_MODULE_SUFFIX}")
endif()

include(FetchContent)
FetchContent_Declare(
	pybind11
	GIT_REPOSITORY https://github.com/pybind/pybind11
	GIT_TAG v3.1.0
)
FetchContent_MakeAvailable(pybind11)

# The guard leaves a superbuild that already provides the target alone.
if(NOT TARGET rexlib::rexlib)
	find_rexlib(VERSION ${REXLIB_PYTHON_REXLIB_VERSION})
endif()

# ---------------------------------------------------------------------------
# The package
# ---------------------------------------------------------------------------

set(REXLIB_PYTHON_PACKAGE_DIR "${REXLIB_PYTHON_INSTALL_DIR}/rexlib")

add_subdirectory(src)

if(REXLIB_PYTHON_BUILD_TESTING)
	add_subdirectory(tests)
endif()

install(
	DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python/rexlib/
	DESTINATION "${REXLIB_PYTHON_PACKAGE_DIR}"
	PATTERN "__pycache__" EXCLUDE
	PATTERN "*.in" EXCLUDE
)

# Same source as the wheel metadata, so the two cannot drift.
configure_file(
	${CMAKE_CURRENT_SOURCE_DIR}/python/rexlib/_version.py.in
	${CMAKE_CURRENT_BINARY_DIR}/_version.py
	@ONLY
)
install(
	FILES ${CMAKE_CURRENT_BINARY_DIR}/_version.py
	DESTINATION "${REXLIB_PYTHON_PACKAGE_DIR}"
)

# Carries the rexlib installation this was built against inside the
# package, so the wheel is self-contained.
stage_rexlib("${REXLIB_PYTHON_PACKAGE_DIR}")

# After everything the import needs is in place.
install_python_stubs(
	MODULE rexlib._binding
	DESTINATION "${REXLIB_PYTHON_PACKAGE_DIR}/_binding"
	SEARCH_PATH "${REXLIB_PYTHON_INSTALL_DIR}"
	STUBS_DIR "${REXLIB_PYTHON_STUBS_DIR}"
	GENERATOR "${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_stubs.py"
)
