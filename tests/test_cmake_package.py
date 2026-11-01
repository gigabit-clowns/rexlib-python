# SPDX-License-Identifier: GPL-3.0-only

import pathlib
import re

import pytest

import rexlib

PACKAGE = pathlib.Path(rexlib.__file__).parent
TARGETS = sorted(PACKAGE.glob("lib*/cmake/rexlib/rexlib-targets-*.cmake"))
LOCATION = re.compile(
	r'IMPORTED_(?:LOCATION|IMPLIB)_\w+ "\$\{_IMPORT_PREFIX\}/([^"]+)"'
)

@pytest.mark.skipif(not TARGETS, reason="no rexlib ships inside the package")
@pytest.mark.parametrize("targets", TARGETS, ids=lambda path: path.name)
def test_cmake_package_names_only_files_the_package_ships(targets):
	located = LOCATION.findall(targets.read_text())
	assert located
	for path in located:
		assert (PACKAGE / path).is_file(), path
