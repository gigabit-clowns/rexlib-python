"""Locate the C++ side of rexlib that ships inside this package."""

from __future__ import annotations

import pathlib

# The wheel nests a complete rexlib install prefix in the package
# directory, so these are the same paths a standalone install exposes,
# just rooted here.
__PREFIX = pathlib.Path(__file__).parent


def get_cmake_dir() -> str:
	"""
	Get the directory holding rexlib's CMake package configuration.

	Pass it to CMake as `rexlib_DIR` to build a plugin, or anything else
	that links rexlib, against the copy shipped in this package.

	Returns:
		str: Directory containing rexlib-config.cmake.
	"""
	return str(__PREFIX / "lib" / "cmake" / "rexlib")


def get_include() -> str:
	"""
	Get the directory holding rexlib's C++ headers.

	Returns:
		str: Directory to add to a compiler's include path.
	"""
	return str(__PREFIX / "include")
