cmake_minimum_required(VERSION 3.21)

include(FetchContent)

# Finds the rexlib installation this binding wraps. Any will do: a system
# one, a hand-built prefix, or the one CI stages before building wheels.
#
# REXLIB_PYTHON_BOOTSTRAP builds one first, for a clean checkout with
# nothing installed. It still goes through find_package, so there is one
# consumption path rather than two.
#
# A macro, not a function: find_package() defines variables in the calling
# scope, and staging needs the ones rexlib's configuration carries.
macro(find_rexlib)
	set(_oneValueArgs VERSION COMMIT)
	cmake_parse_arguments(_rexlib "" "${_oneValueArgs}" "" ${ARGN})

	if(REXLIB_PYTHON_BOOTSTRAP)
		_rexlib_bootstrap("${_rexlib_COMMIT}")
	endif()

	find_package(rexlib ${_rexlib_VERSION} REQUIRED)
	message(STATUS "rexlib ${rexlib_VERSION} at ${PACKAGE_PREFIX_DIR}")
endmacro()

# Configure-time, not build-time: find_package() has to succeed while this
# project is still configuring.
function(_rexlib_bootstrap COMMIT)
	set(ARCHIVE https://github.com/gigabit-clowns/rexlib/archive)
	set(PREFIX "${CMAKE_BINARY_DIR}/rexlib-bootstrap")

	if(NOT EXISTS "${PREFIX}/lib/cmake/rexlib")
		# SOURCE_SUBDIR names no CMakeLists.txt, so this only populates.
		cmake_policy(SET CMP0135 NEW) # To avoid warnings
		FetchContent_Declare(
			rexlib
			URL ${ARCHIVE}/${COMMIT}.tar.gz
			SOURCE_SUBDIR do-not-build
		)
		FetchContent_MakeAvailable(rexlib)

		message(STATUS "Bootstrapping rexlib into ${PREFIX}")
		execute_process(
			COMMAND ${CMAKE_COMMAND}
				-S "${rexlib_SOURCE_DIR}"
				-B "${PREFIX}/build"
				-DCMAKE_BUILD_TYPE=Release
				-DCMAKE_INSTALL_PREFIX=${PREFIX}
				-DBUILD_TESTING=OFF
			COMMAND_ERROR_IS_FATAL ANY
			OUTPUT_QUIET
		)
		execute_process(
			COMMAND ${CMAKE_COMMAND}
				--build "${PREFIX}/build"
				--config Release
				--target install
				--parallel
			COMMAND_ERROR_IS_FATAL ANY
			OUTPUT_QUIET
		)
	endif()

	list(PREPEND CMAKE_PREFIX_PATH "${PREFIX}")
	set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH}" PARENT_SCOPE)
endfunction()
