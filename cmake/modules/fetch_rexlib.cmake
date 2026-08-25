cmake_minimum_required(VERSION 3.18)

include(FetchContent)

# Builds rexlib from source and stages it inside the Python package, so
# that the wheel carries the shared library, the headers and the CMake
# package configuration it was built against.
#
# The library must sit in a prefix nested in the package rather than
# beside the extension: rexlib finds its plugins in a "rexlib-plugins"
# directory next to the shared object, so reproducing the standalone
# prefix layout is what makes plugin wheels land in the right place with
# no special case on either side.
function(fetch_rexlib)
	set(options)
	set(oneValueArgs COMMIT DESTINATION)
	set(multiValueArgs)
	cmake_parse_arguments(PARSE_ARGV 0 arg
		"${options}" "${oneValueArgs}" "${multiValueArgs}"
	)

	# GNUInstallDirs is what rexlib derives every install destination
	# from, REXLIB_PLUGINS_INSTALL_DIR included, so redirecting these
	# three is the whole of the layout change.
	set(CMAKE_INSTALL_LIBDIR "${arg_DESTINATION}/lib")
	set(CMAKE_INSTALL_INCLUDEDIR "${arg_DESTINATION}/include")
	# Beside the extension module on Windows, where there is no RPATH and
	# the loader searches the directory of the .pyd for its dependencies.
	set(CMAKE_INSTALL_BINDIR "${arg_DESTINATION}")

	set(BUILD_TESTING OFF)
	set(REXLIB_BUILD_DOC OFF)

	cmake_policy(SET CMP0135 NEW) # To avoid warnings
	FetchContent_Declare(
		rexlib
		URL https://github.com/gigabit-clowns/rexlib/archive/${arg_COMMIT}.tar.gz
	)
	FetchContent_MakeAvailable(rexlib)

	# A wheel cannot hold a symlink, so pip materialises librexlib.so and
	# librexlib.so.0.1.0 as two full copies of a 50 MB library. Nothing
	# here needs the soname: the extension and any plugin resolve the
	# library by RPATH from a fixed relative location, and CMake's
	# exported target points consumers straight at the file.
	set_property(TARGET rexlib PROPERTY VERSION)
	set_property(TARGET rexlib PROPERTY SOVERSION)
endfunction()
