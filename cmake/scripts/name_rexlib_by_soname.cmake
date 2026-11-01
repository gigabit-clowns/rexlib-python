cmake_minimum_required(VERSION 3.18)

# Points the CMake package of the rexlib under REXLIB_PYTHON_PACKAGE_DIR at
# its library by soname, librexlib.so.0 or librexlib.0.dylib, rather than by
# its full version.

file(GLOB TARGETS_FILES
	"${REXLIB_PYTHON_PACKAGE_DIR}/lib*/cmake/rexlib/rexlib-targets-*.cmake"
)

foreach(TARGETS_FILE IN LISTS TARGETS_FILES)
	file(READ "${TARGETS_FILE}" CONTENT)
	string(REGEX REPLACE
		"librexlib\\.so\\.([0-9]+)\\.[0-9]+\\.[0-9]+"
		"librexlib.so.\\1"
		CONTENT "${CONTENT}"
	)
	string(REGEX REPLACE
		"librexlib\\.([0-9]+)\\.[0-9]+\\.[0-9]+\\.dylib"
		"librexlib.\\1.dylib"
		CONTENT "${CONTENT}"
	)
	file(WRITE "${TARGETS_FILE}" "${CONTENT}")
endforeach()
