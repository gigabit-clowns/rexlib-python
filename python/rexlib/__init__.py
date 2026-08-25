# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from ._binding import (
	__doc__ as __doc__, __version__ as __version__,
	hardware as hardware,
	numerical as numerical, dispatch as dispatch,
	ServiceCatalog as ServiceCatalog,
	PluginManager as PluginManager, Plugin as Plugin,
	get_plugin_directory as get_plugin_directory,
	get_default_plugin_directory as get_default_plugin_directory,
	Version as Version,
)
from ._catalog import get_default_catalog as get_default_catalog
from ._context import get_active_execution_context as get_active_execution_context
from ._device import device as device
from ._paths import get_cmake_dir as get_cmake_dir, get_include as get_include
from . import functional as functional
from . import ndarray as ndarray
