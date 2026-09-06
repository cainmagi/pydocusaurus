# -*- coding: UTF-8 -*-
"""
Renderer
============
@ pyDocusaurus

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The centralized renderer used to produce the Markdown format of the documentation.
Some test.
"""

from pkgutil import extend_path

from . import components
from . import saver
from . import resources
from . import page
from . import package

from .page import render_obj
from .package import render_package_as_mdx

__all__ = (
    "components",
    "saver",
    "resources",
    "page",
    "package",
    "render_obj",
    "render_package_as_mdx",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
