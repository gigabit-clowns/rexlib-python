# SPDX-License-Identifier: GPL-3.0-only

"""Electron microscopy file formats.

One module per area of `rexlib::em`, named after the directory the area
occupies in rexlib rather than after a C++ namespace, which is how every
other module here is named. Each one carries the vocabulary of its area,
so the areas that come after images never have to rename anything.
"""

from __future__ import annotations

from . import image as image

__all__ = ["image"]
