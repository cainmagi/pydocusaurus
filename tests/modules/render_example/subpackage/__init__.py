# -*- coding: UTF-8 -*-
"""
Subpackage
==========
@ pyDocusaurus - Tests: Render Example

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
An example subpackage with a sole function inside it.
"""

from pkgutil import extend_path

__all__ = ("ExampleAnno", "empty_function")


type ExampleAnno = float
"""An annotation in a subpackage root."""


def empty_function() -> None:
    """An example empty function without inputs and outputs."""
    raise NotImplementedError


# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
