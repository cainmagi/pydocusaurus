# -*- coding: UTF-8 -*-
"""
Type Aliases
============
@ pyDocusaurus - Core

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The documentation extraction of type aliases.
"""

import ast
import inspect
import logging
from functools import cached_property

from typing import Any
from collections.abc import Sequence
from typing_extensions import Literal, TypeGuard

from pydantic import BaseModel, Field

import black
import mdformat

from .inspectors import get_obj_slang
from ..components.comprotocol import ProtocolComponent

_GENERIC_TYPE_CALLS: set[str] = {"TypeVar", "ParamSpec", "TypeVarTuple"}
_RUNTIME_ROOT_NAMES: set[str] = {"sys", "os", "pathlib", "importlib", "logging"}

__all__ = (
    "DocTypeAlias",
    "is_generic_type_alias_call",
    "is_runtime_root",
    "is_possibly_type_expression",
    "parse_type_aliases_doc",
)
log = logging.getLogger("pydocusaurus")


class DocTypeAlias(BaseModel):
    """The docstring of a typed alias."""

    type: Literal["alias"] = "alias"
    """The identifier of this documentation item."""

    name: str = Field(min_length=1)
    """The name of the dict item."""

    definition: str
    """The full declaration of the type alias. It is usually an assignment code."""

    descr: str = ""
    """The docstring of the dict item, it is defined in codes."""

    slang: str = ""
    """The internal code identifying this type alias."""

    lineno: int = 0
    """The line number where the alias is defined. If the number is unknown, this
    value will be `0`."""

    @cached_property
    def is_private(self) -> bool:
        """A flag specifying whether the type is private."""
        valid = "(private)"
        return self.descr.strip()[: len(valid)].casefold() == valid

    @staticmethod
    def is_node_type_alias_expr(node: ast.TypeAlias) -> str | None:
        """Check whether an `ast.Node` containing a type alias expression is a type
        alias definition.

        Arguments
        ---------
        node: `ast.TypeAlias`
            An `ast` node that is possibly a type alias expression.

        Returns
        -------
        #1: `str | None`
            The type alias name if is valid.
        """
        name = node.name.id if isinstance(node.name, ast.Name) else None
        if not name or name.startswith("_"):
            return None

        # skip: type Alias[T] = ...
        type_param = getattr(node, "type_params", None)
        if type_param is not None and len(type_param) > 0:
            return None

        value = node.value
        if not is_possibly_type_expression(value):
            return None
        return name

    @staticmethod
    def is_node_anno_assign_expr(node: ast.AnnAssign) -> str | None:
        """Check whether an `ast.Node` containing an annotated assignment expression
        is a type alias definition.

        Arguments
        ---------
        node: `ast.Assign`
            An `ast` node that is possibly a type alias expression.

        Returns
        -------
        #1: `str | None`
            The type alias name if is valid.
        """
        if not isinstance(node.target, ast.Name):
            return None

        name = node.target.id
        if name.startswith("_"):
            return None

        # exclude `None` assignment.
        value = node.value
        if value is None:
            return None

        # exclude plain variables
        if is_generic_type_alias_call(value):
            return None
        if not is_possibly_type_expression(value):
            return None
        return name

    @staticmethod
    def is_node_assign_expr(node: ast.Assign) -> str | None:
        """Check whether an `ast.Node` containing an assignment expression is a type
        alias definition.

        Arguments
        ---------
        node: `ast.Assign`
            An `ast` node that is possibly a type alias expression.

        Returns
        -------
        #1: `str | None`
            The type alias name if is valid.
        """
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            return None

        name = node.targets[0].id
        if name.startswith("_"):
            return None

        value = node.value
        if is_generic_type_alias_call(value):
            return None
        if not is_possibly_type_expression(value):
            return None
        return name

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        type Alias = TypeA | TypeB
        ```

        Note that the v2 string is the same as the definition in the source codes.
        It is also the same as the default plain string.
        """
        res_p = black.format_str(self.definition, mode=black.Mode()).strip()
        return res_p

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        return self.str_v2

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the type alias.
        """
        texts: list[str] = []
        texts.append(
            str(
                renderer.apibar(
                    type="type", is_private=self.is_private, slang=self.slang
                )
            )
        )
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.descr:
            texts.append(self.descr)
        return mdformat.text("\n\n".join(texts))


def is_generic_type_alias_call(value: ast.AST) -> TypeGuard[ast.Call]:
    """Check whether an `ast.Node` is specified by a function call of `TypeVar` and
    `ParamSpec`.

    This method is used for excluding the generic types defined in a module.

    Arguments
    ---------
    value: `ast.AST`
        The `ast` node to be checked.

    Returns
    -------
    #1: `bool`
        A flag. It is `True` if RHS is a `TypeVar`/`ParamSpec`/etc. call.
    """
    if isinstance(value, ast.Call):
        func = value.func
        if isinstance(func, ast.Name):
            return func.id in _GENERIC_TYPE_CALLS
        if isinstance(func, ast.Attribute):
            return func.attr in _GENERIC_TYPE_CALLS
    return False


def is_runtime_root(node: ast.AST) -> TypeGuard[ast.Name]:
    """Check whether an `ast.Node` is specified by a known run-time root.

    This method is used for excluding global variables defined by `getitem` method
    such as `os.environ[...]`.

    Arguments
    ---------
    node: `ast.AST`
        The `ast` node to be checked.

    Returns
    -------
    #1: `bool`
        A flag. It is `True` if it is provided by `os`, `sys`, and some other global
        modules.
    """
    return isinstance(node, ast.Name) and node.id in _RUNTIME_ROOT_NAMES


def is_possibly_type_expression(node: ast.AST) -> bool:
    """A heuristic checker for detecting the possible type expression.

    Note that this method does not guarantee that the given `node` is definitely a
    type alias. Extra run-time checks need to be performed to secure the results.

    Arguments
    ---------
    node: `ast.AST`
        The `ast` node to be checked.

    Returns
    -------
    #1: `bool`
        A flag. It is `True` if node looks like a type expression rather than a
        variable.
    """
    # plain assignments
    if isinstance(node, ast.Name):
        return not is_runtime_root(node)

    if isinstance(node, ast.Attribute):
        return not is_runtime_root(node.value)

    if isinstance(node, ast.Subscript):
        if is_runtime_root(node.value) or (not is_possibly_type_expression(node.value)):
            return False
        return True

    # type union
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return True

    # nested assignment (recursive)
    if isinstance(node, ast.Tuple):
        return all(is_possibly_type_expression(elt) for elt in node.elts)

    # exclude function results, constant, and plain variables.
    if isinstance(node, (ast.Call, ast.Constant, ast.List, ast.Dict, ast.Set)):
        return False

    return False


def _get_docstring_after(
    index: int, body: Sequence[ast.stmt], n_body: int
) -> str | None:
    """(Private) Attempt to get the docstring after a specific code line.

    Arguments
    ---------
    index: `int`
        The line index in the source code.

    body: `list[ast.stmt]`
        The body of the parsed source codes.

    n_body: `int`
        The `len(body)`.

    Returns
    -------
    #1: `str | None`
        The extracted docstring. It is `None` if the docstring cannot be found.
    """
    if index + 2 > n_body:
        return None
    next_node = body[index + 1]
    if not (
        isinstance(next_node, ast.Expr) and isinstance(next_node.value, ast.Constant)
    ):
        return None
    value = next_node.value
    if isinstance(value.value, str):
        return value.value
    return None


def parse_type_aliases_doc(obj: Any) -> list[DocTypeAlias]:
    """Parse the docstring of all type aliases defined in a module.

    Arguments
    ---------
    obj: `Any`
        The place where the attributes will be checked for detecting the type aliases.
        In most cases, this value should be a module.

    Returns
    -------
    #1: `list[DocTypeAlias]`
        The parsed docstrings of the type aliases. Note that these results are purely
        inferred from the codes. The members are not guaranteed to be type aliases.
        Extra run-time checks need to be done to secure results.
    """
    source = inspect.getsource(obj)
    tree = ast.parse(source)
    body = tree.body
    n_body = len(body)

    results: list[DocTypeAlias] = []

    for idx, node in enumerate(body):
        if isinstance(node, ast.TypeAlias):
            name = DocTypeAlias.is_node_type_alias_expr(node)
        elif isinstance(node, ast.Assign):
            name = DocTypeAlias.is_node_assign_expr(node)
        elif isinstance(node, ast.AnnAssign):
            name = DocTypeAlias.is_node_anno_assign_expr(node)
        else:
            name = None

        if name is None:
            continue

        doc = _get_docstring_after(idx, body=body, n_body=n_body)
        if not doc:
            log.warning("Type {0} is undocumented.".format(name))
        definition = ast.get_source_segment(source, node)

        results.append(
            DocTypeAlias(
                name=name,
                definition=definition if definition else "",
                descr=doc if doc else "",
                slang="{0}.{1}".format(get_obj_slang(obj), name),
                lineno=node.lineno,
            )
        )

    return results
