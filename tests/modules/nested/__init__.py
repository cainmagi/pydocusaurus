# -*- coding: UTF-8 -*-
"""
Modules: Nested
===============
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
A minimal package containing a member module.
"""

from pkgutil import extend_path

from . import member
from . import empty

from .member import example_func

__all__ = ("member", "empty", "example_func", "ExampleRootClass", "example_root_func")


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
