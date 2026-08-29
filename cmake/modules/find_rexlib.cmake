cmake_minimum_required(VERSION 3.21)

# Finds the rexlib installation this binding wraps. Any will do: a system
# one, a hand-built prefix, or the one CI stages before building wheels.
# Point CMAKE_PREFIX_PATH at it if it is somewhere CMake would not look.
#
# A macro, not a function: find_package() defines variables in the calling
# scope, and staging needs the ones rexlib's configuration carries.
macro(find_rexlib)
	set(_oneValueArgs VERSION)
	cmake_parse_arguments(_rexlib "" "${_oneValueArgs}" "" ${ARGN})

	find_package(rexlib ${_rexlib_VERSION} QUIET)

	if(NOT rexlib_FOUND)
		message(FATAL_ERROR
			"rexlib ${_rexlib_VERSION} not found. Install it, or build one "
			"with:\n"
			"    python scripts/install_rexlib.py --prefix <prefix>\n"
			"and point CMAKE_PREFIX_PATH at that prefix."
		)
	endif()

	message(STATUS "rexlib ${rexlib_VERSION} at ${PACKAGE_PREFIX_DIR}")
endmacro()
