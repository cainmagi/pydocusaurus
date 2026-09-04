# -*- coding: UTF-8 -*-
"""
Modules: Render Example
=======================
@ pyDocusaurus - Tests

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
An example package used for testing the performance of the documentation rendering.
"""

from pkgutil import extend_path

from . import subpackage
from . import classes
from . import funcs
from . import typecls

from .funcs import example_complicated_func
from .typecls import CustomType

__all__ = (
    "subpackage",
    "classes",
    "funcs",
    "typecls",
    "example_complicated_func",
    "CustomType",
    "ExampleRootClass",
    "example_root_func",
)


class ExampleRootClass:
    """An example class in the package root."""


def example_root_func(arg: int) -> int:
    """An example function in the package root.

    Arguments
    ---------
    arg: `int`
        The input argument.

    Returns
    -------
    #1: `int`
        The returned value.
    """
    raise NotImplementedError


# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
