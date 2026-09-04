# -*- coding: UTF-8 -*-
"""
pyDocusaurus
============

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
Inspired by Sphinx, this tool is designed for generating the Docusaurus documentation
project from Python docstrings.
"""

from pkgutil import extend_path

from . import version
from . import components
from . import core
from . import renderer
from . import clis

from .core import walker
from .renderer import render_obj, render_package_as_mdx

from .version import __version__

__all__ = (
    "version",
    "__version__",
    "components",
    "core",
    "renderer",
    "clis",
    "walker",
    "render_obj",
    "render_package_as_mdx",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
