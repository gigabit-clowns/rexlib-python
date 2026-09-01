# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

# Imported first: on Windows it puts the bundled library on the DLL
# search path, which importing the extension depends on.
from . import _paths as _paths

from ._binding import (
	__doc__ as __doc__,
	hardware as hardware,
	numerical as numerical, dispatch as dispatch,
	ServiceCatalog as ServiceCatalog,
	PluginManager as PluginManager, Plugin as Plugin,
	get_plugin_search_path as get_plugin_search_path,
	get_default_plugin_directory as get_default_plugin_directory,
	Version as Version,
	rexlib_version as rexlib_version,
	rexlib_binding_version as rexlib_binding_version,
)
from ._catalog import get_default_catalog as get_default_catalog
from ._context import get_active_execution_context as get_active_execution_context
from ._device import device as device
from ._paths import get_cmake_dir as get_cmake_dir, get_include as get_include
from . import functional as functional
from . import ndarray as ndarray

__version__ = str(rexlib_binding_version)
