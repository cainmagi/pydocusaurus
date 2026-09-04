# -*- coding: UTF-8 -*-
"""
Core
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
The core functionalities used to analyze the Python codes and docstrings.
"""

from pkgutil import extend_path

from . import inspectors
from . import analyzer
from . import attree
from . import texts
from . import functions
from . import ops
from . import classes
from . import datacls
from . import enums
from . import typeddicts
from . import protocols
from . import typealiases
from . import modules
from . import walker

from .walker import PackageWalker

__all__ = (
    "inspectors",
    "analyzer",
    "attree",
    "texts",
    "functions",
    "ops",
    "classes",
    "datacls",
    "enums",
    "typeddicts",
    "protocols",
    "typealiases",
    "modules",
    "walker",
    "PackageWalker",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
