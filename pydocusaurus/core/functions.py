# -*- coding: UTF-8 -*-
"""
Functions
=========
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
The documentation extraction of functions and methods.
"""

import re
import inspect
import enum
import annotationlib
import logging

from typing import Any
from typing_extensions import Literal, Self, get_overloads
from collections.abc import Sequence, Callable

from functools import cached_property
from pydantic import BaseModel, Field

import mdformat
import black

from . import texts as _texts
from .inspectors import (
    get_obj_slang,
    get_arg_default_name,
    is_user_defined_method,
    is_func_yield,
    unpack_annotation,
    strip_annotation_name,
)
from ..components.comprotocol import ProtocolComponent

__all__ = (
    "ParameterKind",
    "FunctionType",
    "DocArgument",
    "DocFunction",
    "parse_argument_docs",
    "parse_return_docs",
    "parse_func_docs",
)
log = logging.getLogger("pydocusaurus")


class ParameterKind(enum.Enum):
    """Replica of the `inspect._ParameterKind`."""

    POSITIONAL_ONLY = "positional-only"
    """The parameter can only be positional."""

    POSITIONAL_OR_KEYWORD = "positional or keyword"
    """The parameter can be specified by positional or keyword argument."""

    VAR_POSITIONAL = "variadic positional"
    """The parameter is specified by the pattern like "*args"."""

    KEYWORD_ONLY = "keyword-only"
    """The parameter can only be keyword."""

    VAR_KEYWORD = "variadic keyword"
    """The parameter is specified by the pattern like "**kwargs"."""

    @classmethod
    def from_param(cls, param: inspect.Parameter) -> "ParameterKind":
        """Get the `ParameterKind` enum item from the inspected function parameter.

        Arguments
        ---------
        param: `Parameter`
            A parameter inspected from a function.

        Returns
        -------
        #1: `ParameterKind`
            The parameter type which is eqivalent to `param.kind`.
        """
        kind = param.kind
        if kind == param.POSITIONAL_ONLY:
            return cls.POSITIONAL_ONLY
        elif kind == param.POSITIONAL_OR_KEYWORD:
            return cls.POSITIONAL_OR_KEYWORD
        elif kind == param.VAR_POSITIONAL:
            return cls.VAR_POSITIONAL
        elif kind == param.KEYWORD_ONLY:
            return cls.KEYWORD_ONLY
        elif kind == param.VAR_KEYWORD:
            return cls.VAR_KEYWORD
        else:
            return cls.POSITIONAL_OR_KEYWORD


class FunctionType(enum.Enum):
    """The type of a callable object (function)."""

    CLASSMETHOD = "classmethod"
    """The function is a classmethod."""

    STATICMETHOD = "staticmethod"
    """The function is a staticmethod."""

    METHOD = "method"
    """The function is used as an instance method of a class."""

    FUNCTION = "function"
    """The function is defined globally."""

    @classmethod
    def get_method_validator(
        cls: type[Self],
        base_cls: type[Any] | None,
    ) -> Callable[[Any], Self | None]:
        """Get the method type validator for a specific class.

        Arguments
        ---------
        base_cls: `type[Any] | None`
            The base class use for producing the parameter. This base class needs to
            be used when the function is viewed as method candidates which are checked
            under a class scope. If not provided, this validator will only verify
            whether an object is a function.

        Returns
        -------
        #1: `(func: Any) -> FunctionType | None`
            A function validating the function type of the given object. If it is not
            callable or not a function, return `None`.
        """

        def validator(func: Any) -> Self | None:
            """The validator customized for the given class."""
            if not callable(func):
                return None
            if base_cls is None:
                return cls(cls.FUNCTION) if inspect.isfunction(func) else None
            obj = inspect.getattr_static(base_cls, func.__name__, default=None)
            if obj is None:
                return cls(cls.FUNCTION) if inspect.isfunction(func) else None
            if isinstance(obj, classmethod):
                return cls(cls.CLASSMETHOD)
            elif isinstance(obj, staticmethod):
                return cls(cls.STATICMETHOD)
            if inspect.isfunction(obj):
                return cls(cls.METHOD)
            else:
                return None

        return validator


class DocArgument(BaseModel):
    """The docstring of a function/method argument."""

    name: str = Field(min_length=1)
    """The name of the argument."""

    type: str
    """The type of the argument. It is usually the typehint (annotation)."""

    p_type: ParameterKind = ParameterKind.POSITIONAL_OR_KEYWORD
    """The argument/parameter type, see `inspect._ParameterKind`."""

    default: str = ""
    """The formatted default value of the argument."""

    doc: list[str] = Field(default_factory=list)
    """The docstring (line-by-line) of the argument."""

    def format_doc(self) -> str:
        """Format the docstring.

        Returns
        -------
        #1: `str`
            The docstring of the current argument.
        """
        idx_first = 0
        idx_end = len(self.doc) - 1
        while idx_first < len(self.doc):
            if self.doc[idx_first].strip():
                break
            idx_first = idx_first + 1
        while idx_end > 0:
            if self.doc[idx_end].strip():
                break
            idx_end = idx_end - 1
        texts = self.doc[idx_first : (idx_end + 1)]
        leading_space = min(
            set(len(text) - len(text.lstrip()) for text in texts if text.strip()),
            default=0,
        )
        return mdformat.text(
            "\n".join(
                [(text[leading_space:] if text.strip() else "\n") for text in texts]
            ),
            options={"wrap": "no"},
        ).strip()


class DocFunctionOverload(BaseModel):
    """The docstring and basic information of a function overload.

    This data type will override the default argument and result rendering of a
    function if it exists.
    """

    descr: str
    """The description body of the function."""

    args: list[DocArgument] = Field(default_factory=list)
    """The list of input arguments of the function."""

    retval: list[DocArgument] = Field(default_factory=list)
    """The list of returned values of the function."""

    is_yield: bool = False
    """A flag. If it is `True`, the function returns an iterator."""

    def format_args(
        self, parent: "DocFunction", ignore_self: bool = False
    ) -> tuple[str, ...]:
        """Format argument list in the "name: type = default" style.

        This method is modified from `inspect.Signature.format()`.

        Arguments
        ---------
        parent: `DocFunction`
            The parent data model containing the shared information.

        ignore_self: `bool`
            A flag. If specified, will remove `self` and `cls` arguments in methods.

        Returns
        -------
        #1: `tuple[str, ...]`
            A list of formatted arguments.
        """
        result: list[str] = []
        render_pos_only_separator = False
        render_kw_only_separator = True
        syms = {ParameterKind.VAR_POSITIONAL: "*", ParameterKind.VAR_KEYWORD: "**"}
        args = self.args
        if (
            ignore_self
            and len(args) > 0
            and (
                (parent.f_type == FunctionType.METHOD)
                or (parent.f_type == FunctionType.CLASSMETHOD)
            )
        ):
            args = args[1:]
        for arg in args:
            kind = arg.p_type
            formatted = "{sym}{arg}: {type}{default}".format(
                arg=arg.name,
                type=(arg.type if arg.type else "Unknown"),
                default=" = {0}".format(arg.default) if arg.default else "",
                sym=syms.get(kind, ""),
            )

            if kind == ParameterKind.POSITIONAL_ONLY:
                render_pos_only_separator = True
            elif render_pos_only_separator:
                # It's not a positional-only parameter, and the flag
                # is set to 'True' (there were pos-only params before.)
                result.append("/")
                render_pos_only_separator = False

            if kind == ParameterKind.VAR_POSITIONAL:
                # OK, we have an '*args'-like parameter, so we won't need
                # a '*' to separate keyword-only arguments
                render_kw_only_separator = False
            elif kind == ParameterKind.KEYWORD_ONLY and render_kw_only_separator:
                # We have a keyword-only parameter to render and we haven't
                # rendered an '*args'-like parameter before, so add a '*'
                # separator to the parameters list ("foo(arg1, *, arg2)" case)
                result.append("*")
                # This condition should be only triggered once, so
                # reset the flag
                render_kw_only_separator = False

            result.append(formatted)

        if render_pos_only_separator:
            # There were only positional-only parameters, hence the
            # flag was not reset to 'False'
            result.append("/")

        return tuple(result)

    @staticmethod
    def _str_v2_ret(ret: str, ret_len: int) -> str:
        """(Private) Normalize the returned value of V2 string.

        Arguments
        ---------
        ret: `str`
            The full string of returned arguments.

        ret_len: `int`
            The number of returned arguments.

        Returns
        -------
        #1: `str`
            The formatted returned value.
        """
        res_p1 = black.format_str(
            "def f({ret}): ...".format(ret=ret), mode=black.Mode()
        )[5:]
        res_p1 = res_p1[: res_p1.rfind(":")]
        if ret_len == 1:
            res_p1 = res_p1[(res_p1.find("(") + 1) :]
            res_p1 = res_p1[: res_p1.rfind(")")]
            res_p1 = res_p1.rstrip().rstrip(",").rstrip()
            res_p1 = "\n".join([ln for ln in res_p1.splitlines() if ln.strip()])
            res_p1 = inspect.cleandoc(res_p1)
        return res_p1

    def str_v2(self, parent: "DocFunction") -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        ret: type = name(arg1: type1, arg2: type2 = default2, ...)
        ```
        which is more compact than the default string.

        Arguments
        ---------
        parent: `DocFunction`
            The parent data model containing the shared information.

        Returns
        -------
        #1: `str`
            The formatted signature of the overload.
        """
        args = ", ".join(self.format_args(parent=parent, ignore_self=True))
        ret = ", ".join(
            "{name}: {type}".format(
                name="{0}".format("v_{0}".format(idx) if "#" in arg.name else arg.name),
                type=(arg.type if arg.type else "Unknown"),
            )
            for idx, arg in enumerate(self.retval, start=1)
        )
        if len(self.retval) > 0:
            res_p1 = self._str_v2_ret(ret, len(self.retval))
            res_p2 = black.format_str(
                "def {name}({args}): ...".format(name=parent.name, args=args),
                mode=black.Mode(),
            )[4:]
            if parent.prefix:
                res_p2 = "{0}.{1}".format(parent.prefix, res_p2)
            res_p2 = res_p2[: res_p2.rfind(":")].splitlines()
            res: list[str] = [*res_p1.splitlines()]
            if len(res[-1]) + len(res_p2) < 85:
                res[-1] = "{0} {2} {1}".format(
                    res[-1], res_p2[0], "in" if self.is_yield else "="
                )
                res.extend(res_p2[1:])
            else:
                if len(self.retval) > 1:
                    res_p1 = res_p1[1:]
                    res_p1 = res_p1[: res_p1.rfind(")")]
                res = [
                    "(",
                    *res_p1.splitlines(),
                    ") {1} {0}".format(res_p2[0], "in" if self.is_yield else "="),
                    *res_p2[1:],
                ]
            return "\n".join(res)
        else:
            res_p = black.format_str(
                "def {name}({args}): ...".format(name=parent.name, args=args),
                mode=black.Mode(),
            )[4:]
            if parent.prefix:
                res_p = "{0}.{1}".format(parent.prefix, res_p)
            res_p = res_p[: res_p.rfind(":")]
            return res_p

    def str_v1(self, parent: "DocFunction") -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.

        Arguments
        ---------
        parent: `DocFunction`
            The parent data model containing the shared information.

        Returns
        -------
        #1: `str`
            The formatted signature of the overload.
        """
        args = ", ".join(self.format_args(parent=parent, ignore_self=False))
        ret = ", ".join(
            "{type}".format(type=(arg.type if arg.type else "Unknown"))
            for arg in self.retval
        )
        if len(self.retval) > 1:
            ret = "tuple[{0}]".format(ret)
        elif len(self.retval) == 0:
            ret = "None"
        if self.is_yield:
            ret = "Iterator[{0}]".format(ret)
        res = black.format_str(
            "def {name}({args}) -> {ret}: ...".format(
                name=parent.name, args=args, ret=ret
            ),
            mode=black.Mode(),
        ).rstrip()
        if parent.f_type == FunctionType.CLASSMETHOD:
            res = "@classmethod\n{0}".format(res)
        elif parent.f_type == FunctionType.STATICMETHOD:
            res = "@staticmethod\n{0}".format(res)
        return res

    def table_args(
        self,
        renderer: ProtocolComponent,
        ignore_self: bool = False,
        has_type: bool = True,
        has_required: bool = True,
        has_default: bool = False,
        has_doc: bool = True,
    ) -> str:
        """Format the arguments as a table.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        ignore_self: `bool`
            A flag. Needs to be specified when the function is a method/classmethod
            of a class. In this case, the first argument will be skipped.

        has_type: `bool`
            A flag. If specified, will display the argument type.

        has_required: `bool`
            A flag. If specified, will display whether the argument is required.

        has_default: `bool`
            A flag. If specified, will display the default value of the argument.

        has_doc: `bool`
            A flag. If specified, will display the docstring of the argument.

        Returns
        -------
        #1: `str`
            The Markdown table of the arguments.
        """
        cols: list[str] = (
            ["Name"]
            + (["Type"] if has_type else [])
            + (["Required"] if has_required else [])
            + (["Default"] if has_default else [])
            + (["Description"] if has_doc else [])
        )
        idx_type: int | None = cols.index("Type") if "Type" in cols else None
        idx_required: int | None = (
            cols.index("Required") if "Required" in cols else None
        )
        idx_default: int | None = cols.index("Default") if "Default" in cols else None
        idx_doc: int | None = (
            cols.index("Description") if "Description" in cols else None
        )
        col_styles: dict[int, Literal["l", "c", "r", "n"]] = {0: "c"}
        for idx, style in zip(
            (idx_type, idx_required, idx_default, idx_doc), ("c", "c", "c", "l")
        ):
            if idx:
                col_styles[idx] = style
        table = _texts.Table(
            n_rows=len(self.args) + (0 if ignore_self else 1),
            n_cols=len(cols),
            col_styles=col_styles,
            cells={(0, 0): cols[0]},
        )
        for idx in (idx_type, idx_required, idx_default):
            if idx is not None:
                table.cells[(0, idx)] = cols[idx]
        if idx_doc is not None:
            table.cells[(0, idx_doc)] = "<center>{0}</center>".format(cols[idx_doc])
        args = self.args
        if len(args) > 0 and ignore_self:
            args = args[1:]
        for idx, arg in enumerate(args, start=1):
            name = (
                ("*" if arg.p_type == ParameterKind.VAR_POSITIONAL else "")
                + ("**" if arg.p_type == ParameterKind.VAR_KEYWORD else "")
                + arg.name
            )
            table.cells[(idx, 0)] = "`{0}`".format(name) if name else ""
            if idx_type is not None:
                table.cells[(idx, idx_type)] = (
                    "`{0}`".format(arg.type.replace("|", R"\|")) if arg.type else ""
                )
            if idx_required is not None:
                table.cells[(idx, idx_required)] = (
                    renderer.inline_icon("check") if (not arg.default) else ""
                )
            if idx_default is not None:
                table.cells[(idx, idx_default)] = (
                    "`{0}`".format(arg.default.replace("|", R"\|"))
                    if arg.default
                    else ""
                )
            if idx_doc is not None:
                table.cells[(idx, idx_doc)] = arg.format_doc().replace("|", R"\|")
        return table.as_md_text()

    def table_retval(
        self,
        is_renamed: bool = True,
        has_type: bool = True,
        has_doc: bool = True,
    ) -> str:
        """Format the returned values as a table.

        Arguments
        ---------
        is_renamed: `bool`
            A flag. If specified, will automatically rename the numbered returned
            value in the v2 format.

        has_type: `bool`
            A flag. If specified, will display the argument type.

        has_doc: `bool`
            A flag. If specified, will display the docstring of the argument.

        Returns
        -------
        #1: `str`
            The Markdown table of the arguments.
        """
        cols: list[str] = (
            ["Name"]
            + (["Type"] if has_type else [])
            + (["Description"] if has_doc else [])
        )
        idx_type: int | None = cols.index("Type") if "Type" in cols else None
        idx_doc: int | None = (
            cols.index("Description") if "Description" in cols else None
        )
        col_styles: dict[int, Literal["l", "c", "r", "n"]] = {0: "c"}
        for idx, style in zip((idx_type, idx_doc), ("c", "l")):
            if idx:
                col_styles[idx] = style
        table = _texts.Table(
            n_rows=len(self.retval) + 1,
            n_cols=len(cols),
            col_styles=col_styles,
            cells={(0, 0): cols[0]},
        )
        if idx_type is not None:
            table.cells[(0, idx_type)] = cols[idx_type]
        if idx_doc is not None:
            table.cells[(0, idx_doc)] = "<center>{0}</center>".format(cols[idx_doc])
        for idx, arg in enumerate(self.retval, start=1):
            name = "{0}".format(
                "v_{0}".format(idx) if (is_renamed and ("#" in arg.name)) else arg.name
            )
            table.cells[(idx, 0)] = "`{0}`".format(name) if name else ""
            if idx_type is not None:
                table.cells[(idx, idx_type)] = (
                    "`{0}`".format(arg.type.replace("|", R"\|")) if arg.type else ""
                )
            if idx_doc is not None:
                table.cells[(idx, idx_doc)] = arg.format_doc().replace("|", R"\|")
        return table.as_md_text()

    def as_md_text(
        self,
        renderer: ProtocolComponent,
        has_descr: bool = True,
        ignore_self: bool = False,
        title: str = "Arguments",
        title_level: int = 3,
    ) -> str:
        """Render as Markdown text.

        This overload rendering will only contains the information specified in the
        overload data model.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        has_descr: `bool`
            A flag. If specified, will add the overload description to the results.

        ignore_self: `bool`
            A flag. If specified, will ignore the first argument (`self` or `cls`)
            in the argument list. Needs to be specified when the function is a
            method/classmethod of a class. In this case, the first argument will be
            skipped.

        title: `str`
            The title of the overload information.

        title_level: `int`
            The level of the title when displaying this overload.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the overload of the function.
        """
        title_mark = "#" * title_level
        res_texts: list[str] = []
        len_args = len(self.args) - (1 if ignore_self else 0)
        if (len_args > 0) or self.retval or (has_descr and self.descr):
            if title:
                res_texts.append("{0} {1}".format(title_mark, title))
        else:
            return ""
        if self.descr:
            res_texts.append("{0}".format(self.descr))
        if len_args > 0:
            res_texts.append("{0}# Requires".format(title_mark))
            res_texts.append(
                self.table_args(renderer=renderer, ignore_self=ignore_self)
            )
        if self.retval:
            res_texts.append(
                "{0}# {1}".format(title_mark, "Yields" if self.is_yield else "Returns")
            )
            res_texts.append(self.table_retval())
        return "\n\n".join(res_texts).strip()


class DocFunction(BaseModel):
    """The docstring and basic information of a function.

    This serializable data type contains the signature of a function, and the
    corresponding docstring of function body, arguments, and results.
    """

    type: Literal["function"] = "function"
    """The identifier of this documentation item."""

    name: str
    """The name of the function."""

    descr: str
    """The description body of the function."""

    args: list[DocArgument] = Field(default_factory=list)
    """The list of input arguments of the function."""

    retval: list[DocArgument] = Field(default_factory=list)
    """The list of returned values of the function."""

    is_yield: bool = False
    """A flag. If it is `True`, the function returns an iterator."""

    f_type: FunctionType = FunctionType.FUNCTION
    """The type of the function."""

    prefix: str = ""
    """An optional prefix. If specified, will add it before the function name in the
    v2 signature."""

    slang: str = ""
    """The internal code identifying this function. It needs to be specified when the
    function is a vanilla function (`f_type` is `"function"`) to provide the
    identification of the source code."""

    lineno: int = 0
    """The line number where the function is defined. If the number is unknown, this
    value will be `0`."""

    overloads: list[DocFunctionOverload] = Field(default_factory=list)
    """The overloads of this function. If existing, will override the default
    docstrings."""

    @cached_property
    def is_private(self) -> bool:
        """A flag specifying whether the function is private."""
        valid = "(private)"
        return self.descr.strip()[: len(valid)].casefold() == valid

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        ret: type = name(arg1: type1, arg2: type2 = default2, ...)
        ```
        which is more compact than the default string.
        """
        if not self.overloads:
            _overload = DocFunctionOverload(
                descr=self.descr,
                args=self.args,
                retval=self.retval,
                is_yield=self.is_yield,
            )
            return DocFunctionOverload.str_v2(_overload, parent=self)
        _overloads = [_overload.str_v2(parent=self) for _overload in self.overloads]
        return "\n".join(_overloads)

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        if not self.overloads:
            _overload = DocFunctionOverload(
                descr=self.descr,
                args=self.args,
                retval=self.retval,
                is_yield=self.is_yield,
            )
            return DocFunctionOverload.str_v1(_overload, parent=self)
        _overloads = [_overload.str_v1(parent=self) for _overload in self.overloads]
        return "\n\n".join(_overloads)

    def _as_md_text_method(self, renderer: ProtocolComponent) -> str:
        """(Private) Render as Markdown text when the function is a method.

        The "method" rendering will be in a simpler format.
        """
        texts: list[str] = []
        texts.append("### {0} `{1}`".format(renderer.icon_obj("method"), self.name))
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.descr:
            texts.append(self.descr)

        is_self_ignored = (self.f_type == FunctionType.METHOD) or (
            self.f_type == FunctionType.CLASSMETHOD
        )
        if not self.overloads:
            _overload = DocFunctionOverload(
                descr="", args=self.args, retval=self.retval, is_yield=self.is_yield
            )
            texts.append(
                _overload.as_md_text(
                    renderer=renderer,
                    has_descr=False,
                    ignore_self=is_self_ignored,
                    title="",
                    title_level=3,
                )
            )
            return mdformat.text("\n\n".join(texts))
        if len(self.overloads) == 1:
            texts.append(
                self.overloads[0].as_md_text(
                    renderer=renderer,
                    has_descr=True,
                    ignore_self=is_self_ignored,
                    title="",
                    title_level=3,
                )
            )
            return mdformat.text("\n\n".join(texts))
        for idx, _overload in enumerate(self.overloads, start=1):
            texts.append(
                _overload.as_md_text(
                    renderer=renderer,
                    has_descr=True,
                    ignore_self=is_self_ignored,
                    title="Arguments (ver. {0})".format(idx),
                    title_level=4,
                )
            )
        return mdformat.text("\n\n".join(texts))

    def _as_md_text_function(self, renderer: ProtocolComponent) -> str:
        """(Private) Render as Markdown text when the function is a vanilla function.

        The "function" rendering will be in the full format.
        """
        texts: list[str] = []
        texts.append(
            str(
                renderer.apibar(
                    type="func", is_private=self.is_private, slang=self.slang
                )
            )
        )
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.descr:
            texts.append(self.descr)

        arg_secs: list[str] = []
        if not self.overloads:
            _overload = DocFunctionOverload(
                descr="", args=self.args, retval=self.retval, is_yield=self.is_yield
            )
            _arg_text = _overload.as_md_text(
                renderer=renderer,
                has_descr=False,
                ignore_self=False,
                title="Arguments",
                title_level=2,
            )
            if _arg_text:
                arg_secs.append(_arg_text)
            texts.extend(
                arg_secs if arg_secs else ["## Arguments", "No argument is needed."]
            )
            return mdformat.text("\n\n".join(texts))
        if len(self.overloads) == 1:
            _arg_text = self.overloads[0].as_md_text(
                renderer=renderer,
                has_descr=True,
                ignore_self=False,
                title="Arguments",
                title_level=2,
            )
            if _arg_text:
                arg_secs.append(_arg_text)
            texts.extend(
                arg_secs if arg_secs else ["## Arguments", "No argument is needed."]
            )
            return mdformat.text("\n\n".join(texts))
        for idx, _overload in enumerate(self.overloads, start=1):
            _arg_text = _overload.as_md_text(
                renderer=renderer,
                has_descr=True,
                ignore_self=False,
                title="Arguments (ver. {0})".format(idx),
                title_level=2,
            )
            if _arg_text:
                arg_secs.append(_arg_text)
        texts.extend(
            arg_secs if arg_secs else ["## Arguments", "No argument is needed."]
        )
        return mdformat.text("\n\n".join(texts))

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the function.
        """
        if self.f_type == FunctionType.FUNCTION:
            return self._as_md_text_function(renderer=renderer)
        return self._as_md_text_method(renderer=renderer)


def parse_argument_docs(
    func: Any,
    docstring: Sequence[str],
    func_name: str | None = None,
    warn_supp: bool = False,
) -> list[DocArgument]:
    """(Private) Parse the docstring related to function arguments.

    It is a part of `parse_func_docs(...)`. Calling this function direclty is not
    recommended.

    Arguments
    ---------
    func: `Any`
        A function object to be parsed. It can be a vanilla function or a method.

    docstring: `list[str]`
        The line-by-line docstring of all arguments. This value should be provided
        by an analyzed `Section` object.

    func_name: `str | None`
        The function name displayed in messages. If not specified, will automatically
        infer it.

    warn_supp: `bool`
        A flag. If specified, will not display warning messages. It is used for
        excluding special/private functions.

    Returns
    -------
    #1: `list[DocArgument]`
        A list of parsed docstrings of all input arguments.
    """
    if isinstance(func, (classmethod, staticmethod)):
        func = func.__func__
    sig = inspect.signature(func)
    params = sig.parameters
    anno = annotationlib.get_annotations(func, format=annotationlib.Format.STRING)
    if "return" in anno:
        anno.pop("return")
    names = set(re.escape(name.strip()) for name in params.keys())
    pattern = re.compile(r"^\**?((?!\*)[^\s\*]*)\s*?:\s*?(?:\:*)(?!\s)(.*?)(?:\:*)$")

    args: dict[str, DocArgument] = {}
    _func_name = getattr(func, "__name__", "Unknown") if not func_name else func_name

    cur_doc: DocArgument | None = None
    for line in docstring:
        reobj = pattern.match(line)
        if reobj is not None:
            if cur_doc is not None:
                args[cur_doc.name] = cur_doc
            _name = reobj.group(1).strip()
            cur_doc = (
                DocArgument(
                    name=_name,
                    type=reobj.group(2).strip().strip("`:").strip(),
                    default=(
                        get_arg_default_name(params[_name].default)
                        if _name in params
                        else ""
                    ),
                    doc=[],
                )
                if _name
                else None
            )
            continue
        if cur_doc is None:
            continue
        cur_doc.doc.append(line)
    if cur_doc is not None and cur_doc.name in names:
        args[cur_doc.name] = cur_doc

    res: list[DocArgument] = []
    for name, param in params.items():
        _type = strip_annotation_name(anno[name]) if name in anno else "Any"
        if name in args:
            arg = args[name]
            arg.p_type = ParameterKind.from_param(param)
            arg.type = _type if (_type != "Any" or (not arg.type)) else arg.type
        else:
            if (not warn_supp) and (name not in ("self", "cls")):
                log.warning(
                    "Function argument {0}({1}) is "
                    "undocumented.".format(_func_name, name)
                )
            arg = DocArgument(
                name=name,
                type=_type,
                p_type=ParameterKind.from_param(param),
                default=(
                    get_arg_default_name(params[name].default) if name in params else ""
                ),
                doc=[],
            )
        res.append(arg)

    return res


def parse_return_docs(
    func: Any,
    docstring: Sequence[str],
    func_name: str | None = None,
    warn_supp: bool = False,
) -> list[DocArgument]:
    """(Private) Parse the docstring related to function returned values.

    It is a part of `parse_func_docs(...)`. Calling this function direclty is not
    recommended.

    Arguments
    ---------
    func: `Any`
        A function object to be parsed. It can be a vanilla function or a method.

    docstring: `list[str]`
        The line-by-line docstring of all returned values. This value should be
        provided by an analyzed `Section` object.

    func_name: `str | None`
        The function name displayed in messages. If not specified, will automatically
        infer it.

    warn_supp: `bool`
            A flag. If specified, will not display warning messages. It is used for
            excluding special/private functions.

    Returns
    -------
    #1: `list[DocArgument]`
        A list of parsed docstrings of all returned values.
    """
    if isinstance(func, (classmethod, staticmethod)):
        func = func.__func__
    annotations = annotationlib.get_annotations(func, format=annotationlib.Format.VALUE)
    return_annotation, _, _ = unpack_annotation(annotations.get("return", "Unknown"))

    anno = (
        tuple()
        if return_annotation
        and (return_annotation[0] is None or return_annotation[0] == "Unknown")
        else tuple(
            strip_annotation_name(_anno_item) for _anno_item in return_annotation
        )
    )

    pattern = re.compile(r"^\#(\d+?)\s*?:\s*?(?:\:*)(?!\s)(.*?)(?:\:*)$")

    args: dict[int, DocArgument] = {}

    cur_doc: DocArgument | None = None
    for line in docstring:
        reobj = pattern.match(line)
        if reobj is not None:
            if cur_doc is not None:
                args[int(cur_doc.name[1:])] = cur_doc
            _idx = int(reobj.group(1).strip())
            cur_doc = (
                DocArgument(
                    name="#{0}".format(_idx),
                    type=reobj.group(2).strip().strip("`:").strip(),
                    p_type=ParameterKind.POSITIONAL_ONLY,
                    doc=[],
                )
                if _idx
                else None
            )
            continue
        if cur_doc is None:
            continue
        cur_doc.doc.append(line)
    if cur_doc is not None:
        args[int(cur_doc.name[1:])] = cur_doc

    _func_name = getattr(func, "__name__", "Unknown") if not func_name else func_name
    if (not warn_supp) and return_annotation == ("Unknown",) and (not docstring):
        log.warning(
            "Function returned values {0}(...) -> ... are "
            "undocumented.".format(_func_name)
        )
        return [
            DocArgument(
                name="#1",
                type="Unknown",
                p_type=ParameterKind.POSITIONAL_ONLY,
                doc=[],
            )
        ]

    res: list[DocArgument] = []
    if return_annotation == ("Unknown",) and args:
        idx_argmax = max(args.keys(), default=0)
        for idx in range(1, idx_argmax + 1):
            if idx in args:
                res.append(args[idx])
            else:
                if not warn_supp:
                    log.warning(
                        "Function returned value with {0}(...) -> #{1} are "
                        "undocumented.".format(_func_name, idx)
                    )
                res.append(
                    DocArgument(
                        name="#{0}".format(idx),
                        type="Unknown",
                        p_type=ParameterKind.POSITIONAL_ONLY,
                        doc=[],
                    )
                )
        return res

    for idx, _type in enumerate(anno, start=1):
        if idx in args:
            arg = args[idx]
            arg.type = _type if (_type != "Any" or (not arg.type)) else arg.type
        else:
            if not warn_supp:
                log.warning(
                    "Function returned value with {0}(...) -> #{1} are "
                    "undocumented.".format(_func_name, idx)
                )
            arg = DocArgument(
                name="#{0}".format(idx),
                type=_type,
                p_type=ParameterKind.POSITIONAL_ONLY,
                doc=[],
            )
        res.append(arg)

    return res


def parse_func_docs(func: Any, base_cls: type[Any] | None = None) -> DocFunction:
    """Parse the docstring of a function.

    Arguments
    ---------
    func: `Any`
        A function object to be parsed. It can be a vanilla function or a method.

    base_cls: `type[Any]`
        An optional base class. If provided, will check whether `func` is a member and
        a method of the given `base_cls`.

    Returns
    -------
    #1: `DocFunction`
        The parsed docstring of the function/method.
    """
    if isinstance(func, (classmethod, staticmethod)):
        _func = func.__func__
    else:
        _func = func
    name = str(getattr(func, "__name__", getattr(_func, "__name__"))).strip()
    _warn_supp = base_cls is not None and (not is_user_defined_method(base_cls, func))

    _doc = inspect.cleandoc(_func.__doc__) if _func.__doc__ else ""
    doc_secs = _texts.Section.from_md_text(_doc)
    descr = (
        doc_secs[0].as_md_text()
        if (len(doc_secs) > 0 and doc_secs[0].level == 0)
        else ""
    )
    _is_func_yield = is_func_yield(_func)
    _title_ret = (
        ("yields", "yield", "iterates", "iterate")
        if _is_func_yield
        else ("returns", "return", "results", "result")
    )

    doc_args: list[str] = list()
    doc_ret: list[str] = list()
    for sec in doc_secs:
        if sec.level == 0:
            continue
        title = sec.title.strip().casefold()
        if title in ("parameters", "arguments", "parameter", "argument"):
            doc_args.extend(sec.content)
            continue
        if title in _title_ret:
            doc_ret.extend(sec.content)
            continue
    f_type = FunctionType.get_method_validator(base_cls)(_func)
    if f_type is None:
        raise TypeError(
            "Attempt to parse the function docstring from an object that is not a "
            "function: {0}".format(func)
        )
    func_full_name = (
        "{0}.{1}".format(base_cls.__name__, name)
        if base_cls is not None
        and f_type
        in (FunctionType.METHOD, FunctionType.CLASSMETHOD, FunctionType.STATICMETHOD)
        else name
    )

    # Parse overloads
    overloads: list[DocFunctionOverload] = []
    for idx, func_o in enumerate(get_overloads(_func)):
        _doc = inspect.cleandoc(func_o.__doc__) if func_o.__doc__ else ""
        _doc_secs = _texts.Section.from_md_text(_doc)
        _descr = (
            _doc_secs[0].as_md_text()
            if (len(_doc_secs) > 0 and _doc_secs[0].level == 0)
            else ""
        )
        if not (_warn_supp or bool(_descr)):
            log.warning(
                "{0} {1} overload #{2} does not provide its main docstring.".format(
                    "Method" if f_type == FunctionType.METHOD else "Function",
                    func_full_name,
                    idx,
                )
            )
        _doc_args: list[str] = list()
        _doc_ret: list[str] = list()
        _is_func_yield_o = is_func_yield(func_o)
        _title_ret = (
            ("yields", "yield", "iterates", "iterate")
            if _is_func_yield_o
            else ("returns", "return", "results", "result")
        )

        for sec in _doc_secs:
            if sec.level == 0:
                continue
            title = sec.title.strip().casefold()
            if title in ("parameters", "arguments", "parameter", "argument"):
                _doc_args.extend(sec.content)
                continue
            if title in _title_ret:
                _doc_ret.extend(sec.content)
                continue
        overloads.append(
            DocFunctionOverload(
                descr=_descr,
                args=parse_argument_docs(
                    func_o, _doc_args, func_name=func_full_name, warn_supp=_warn_supp
                ),
                retval=parse_return_docs(
                    func_o, _doc_ret, func_name=func_full_name, warn_supp=_warn_supp
                ),
                is_yield=_is_func_yield_o,
            )
        )

    if not (_warn_supp or descr or overloads):
        log.warning(
            "{0} {1} does not provide its main docstring.".format(
                "Method" if f_type == FunctionType.METHOD else "Function",
                func_full_name,
            )
        )

    return DocFunction(
        name=name,
        descr=descr,
        is_yield=_is_func_yield,
        f_type=f_type,
        prefix=(
            ("self" if f_type == FunctionType.METHOD else base_cls.__name__)
            if (base_cls is not None and f_type != FunctionType.FUNCTION)
            else ""
        ),
        slang=(
            "{0}.{1}".format(get_obj_slang(base_cls), name)
            if base_cls is not None
            else get_obj_slang(func)
        ),
        args=parse_argument_docs(
            func,
            doc_args,
            func_name=func_full_name,
            warn_supp=(_warn_supp or bool(overloads)),
        ),
        retval=parse_return_docs(
            func,
            doc_ret,
            func_name=func_full_name,
            warn_supp=(_warn_supp or bool(overloads)),
        ),
        overloads=overloads,
    )
