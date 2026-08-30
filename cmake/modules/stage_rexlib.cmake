cmake_minimum_required(VERSION 3.18)

# Copies the rexlib installation into the Python package, mirroring an
# ordinary prefix one level down: lib/, lib/cmake/rexlib/, include/.
#
# The shape matters twice. Plugins are discovered in a "rexlib-plugins"
# directory beside the shared library, and rexlib's package configuration
# resolves paths relative to itself, so it only survives being moved if
# its surroundings keep the same shape.
#
# Only the versioned library is copied. A wheel cannot hold a symlink, so
# pip would turn each one into another full copy of a 50 MB file; the
# extension links the SONAME, so the real file is enough.
function(stage_rexlib DESTINATION)
	# Only a rexlib found through find_package has a prefix to copy. A
	# super-build supplies the target straight from its own build tree, and
	# rexlib_DIR is what tells the two apart: without this, the install rule
	# below expands to "/" and copies the filesystem root.
	if(NOT rexlib_DIR)
		message(STATUS
			"rexlib did not come from find_package; not staging it into the "
			"Python package"
		)
		return()
	endif()

	get_target_property(
		INCLUDE_DIRS rexlib::rexlib INTERFACE_INCLUDE_DIRECTORIES
	)
	list(GET INCLUDE_DIRS 0 INCLUDE_DIR)

	if(WIN32)
		install(
			FILES $<TARGET_FILE:rexlib::rexlib>
			DESTINATION ${DESTINATION}/bin
		)
		install(
			FILES $<TARGET_LINKER_FILE:rexlib::rexlib>
			DESTINATION ${DESTINATION}/lib
		)
	else()
		install(
			FILES $<TARGET_FILE:rexlib::rexlib>
			DESTINATION ${DESTINATION}/lib
		)
	endif()

	install(
		DIRECTORY "${INCLUDE_DIR}/rexlib"
		DESTINATION ${DESTINATION}/include
	)
	install(
		DIRECTORY "${rexlib_DIR}/"
		DESTINATION ${DESTINATION}/lib/cmake/rexlib
	)
endfunction()
