# -*- coding: UTF-8 -*-
"""
Components
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
The components used for building the documentations.
"""

from pkgutil import extend_path

from . import comprotocol
from . import apibar

__all__ = ("apibar", "comprotocol")

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
