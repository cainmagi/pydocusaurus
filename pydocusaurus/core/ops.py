# -*- coding: UTF-8 -*-
"""
Operators
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
The documentation extraction of class operators.
"""

import re
import string

from typing import Any
from typing_extensions import Literal, Self

from pydantic import BaseModel

import mdformat

from . import functions as _funcs
from ..components.comprotocol import ProtocolComponent

__all__ = ("unwrap_top_level_typehint", "DocOpTemplate")


def unwrap_top_level_typehint(anno: str) -> list[str]:
    """Unwrap the top-level bracket of a typehint (annotation).

    Arguments
    ---------
    anno: `str`
        The string representation of an annotation such as
        `colletions.abc.Generator[int, None, None]`

    Returns
    -------
    #1: `list[str]`
        A list of the top-level children of the given annotation.
    """
    parts: list[str] = []
    buf: list[str] = []
    depth: int = 0
    start = anno.index("[")
    end = anno.rindex("]")
    for ch in anno[start + 1 : end]:
        if ch == "[":
            depth += 1
            buf.append(ch)
        elif ch == "]":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


class DocOpTemplate(BaseModel):
    """The template of the plain operator.

    For example, the `len` operator can be implemented by:
    ``` python
    DocOpTemplate(name="len", template="{vr1}: {tr1} = len({va1})")
    ```

    Another example is the `getitem` operator which can be type-specified:
    ``` python
    DocOpTemplate(name="getitem", template="data: DataType = value[key]")
    ```
    """

    name: str
    """The name of the operator (do not include the underlines)."""

    template: str
    """The template content. Use `"{vr1}"`, `"{tr1}"`, `"{va1}"`, `"{ta1}"`, ...
    to represent the variables and types in the returned values and arguments,
    respectively."""

    func: _funcs.DocFunction
    """The function body of the docstring."""

    special: Literal["no", "yield"] = "no"
    """The special case of the string version rendering. If not specified, will use
    the `template` to render the results."""

    @staticmethod
    def _postproc_yield(ret_type: str) -> str:
        """An optional post-processing removing the wrapper of the iterator."""
        reobj = re.compile(r"^.*?Iterator\[(.*?)\]$").fullmatch(ret_type)
        if reobj is not None:
            return reobj.group(1)
        reobj = re.compile(r"^.*?Generator\[(.*?)\]$").fullmatch(ret_type)
        if reobj is not None:
            return unwrap_top_level_typehint("[{0}]".format(reobj.group(1)))[0]
        return ret_type

    def _str_v2_for_yield(self, _overload: _funcs.DocFunctionOverload) -> str:
        """(Private) Render he v2 string as an operator in the special case: yield."""
        if not _overload.is_yield:
            return self._str_v2_for_overload(_overload)
        _name = _overload.args[0].name if _overload.args else "self"
        retval = _overload.retval
        if not retval:
            return "for _ in {0}: ...".format(_name)
        v_r = (
            retval[0].name
            if len(retval) == 1
            else "({0})".format(
                ", ".join(item.name.replace("#", "v_") for item in retval)
            )
        )
        v_a = "\n".join(
            "    {0}: {1}".format(item.name.replace("#", "v_"), item.type)
            for item in retval
        )
        return "for {0} in {1}:\n{2}".format(v_r, _name, v_a)

    def _str_v2_for_overload(self, _overload: _funcs.DocFunctionOverload) -> str:
        """(Private) Render the v2 string as an operator item using a function
        overload."""
        ret_name = re.compile(r"^vr(\d+?)$")
        ret_type = re.compile(r"^tr(\d+?)$")
        arg_name = re.compile(r"^va(\d+?)$")
        arg_type = re.compile(r"^ta(\d+?)$")
        vardict: dict[str, str] = dict()
        for _, field_name, _, _ in string.Formatter().parse(self.template):
            if field_name is None:
                continue
            try:
                reobj = ret_name.fullmatch(field_name)
                if reobj is not None:
                    vardict[field_name] = _overload.retval[
                        int(reobj.group(1)) - 1
                    ].name.replace("#", "v_")
                    continue
                reobj = ret_type.fullmatch(field_name)
                if reobj is not None:
                    _ret_type = _overload.retval[int(reobj.group(1)) - 1].type
                    vardict[field_name] = _ret_type
                    continue
                reobj = arg_name.fullmatch(field_name)
                if reobj is not None:
                    vardict[field_name] = _overload.args[int(reobj.group(1)) - 1].name
                    continue
                reobj = arg_type.fullmatch(field_name)
                if reobj is not None:
                    vardict[field_name] = _overload.args[int(reobj.group(1)) - 1].type
                    continue
            except IndexError:
                vardict[field_name] = "Unknown"
            vardict[field_name] = "Unknown"
        return self.template.format(**vardict)

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        template.format(
            va1=self.func.args[0].name, a1=self.func.args[0].type,
            ...
            vr1=self.func.retval[0].name, r1=self.func.retval[0].type,
            ...
        )
        ```
        which is more compact than the default string.
        """
        func = self.func
        if self.special == "no" and not self.template:
            return func.str_v2
        match (self.special):
            case "yield":
                renderer = self._str_v2_for_yield
            case _:
                renderer = self._str_v2_for_overload
        if not func.overloads:
            _overload = _funcs.DocFunctionOverload(
                descr=func.descr,
                args=func.args,
                retval=func.retval,
                is_yield=func.is_yield,
            )
            return renderer(_overload)
        _overloads = [renderer(_overload) for _overload in func.overloads]
        return "\n".join(_overloads)

    @classmethod
    def from_func(cls: type[Self], func: Any, base_cls: type[Any]) -> Self:
        """Create the `DocOpTemplate` from an operator function.

        Arguments
        ---------
        func: `Any`
            The method function used for creating this operator template.

        base_cls: `type[Any]`
            The class where the operator is defined.

        Returns
        -------
        #1: `DocOpTemplate`
            The operator template created from the given operator method.
        """
        _func = _funcs.parse_func_docs(func, base_cls=base_cls)
        reop = re.compile(r"^__(.*)__$")
        reobj = reop.fullmatch(_func.name)
        if reobj is None:
            raise TypeError("Not an operator function: {0}".format(_func.name))
        op_ex = ""
        op_name = str(reobj.group(1))
        if op_name not in ("repr", "iter", "rshift") and (
            op_name.startswith("r") or op_name.startswith("i")
        ):
            op_ex = op_name[0]
            op_name = op_name[1:]
        math_ops: dict[str, str] = {
            "add": "+",
            "sub": "-",
            "mul": "*",
            "matmul": "@",
            "truediv": "/",
            "floordiv": "//",
            "mod": "%",
            "divmod": "divmod",
            "pow": "**",
            "lshift": "<<",
            "rshift": ">>",
            "and": "&",
            "or": "|",
            "xor": "^",
        }
        _mathop = math_ops.get(op_name)
        if _mathop is not None:
            match (op_ex):
                case "r":
                    return cls(
                        name=op_name,
                        template="{{vr1}}: {{tr1}} = {{va2}} {op} {{va1}}".format(
                            op=_mathop
                        ),
                        func=_func,
                    )
                case "i":
                    return cls(
                        name=op_name,
                        template="{{vr1}}: {{tr1}} {op}= {{va1}}".format(op=_mathop),
                        func=_func,
                    )
                case _:
                    return cls(
                        name=op_name,
                        template="{{vr1}}: {{tr1}} = {{va1}} {op} {{va2}}".format(
                            op=_mathop
                        ),
                        func=_func,
                    )
        match (op_name):
            case "len":
                return cls(
                    name=op_name, template="length: {tr1} = len({va1})", func=_func
                )
            case "eq":
                return cls(
                    name=op_name, template="flag: {tr1} = ({va1} == {va2})", func=_func
                )
            case "ne":
                return cls(
                    name=op_name, template="flag: {tr1} = ({va1} != {va2})", func=_func
                )
            case "lt":
                return cls(
                    name=op_name, template="flag: {tr1} = ({va1} < {va2})", func=_func
                )
            case "le":
                return cls(
                    name=op_name, template="flag: {tr1} = ({va1} <= {va2})", func=_func
                )
            case "gt":
                return cls(
                    name=op_name, template="flag: {tr1} = ({va1} > {va2})", func=_func
                )
            case "ge":
                return cls(
                    name=op_name, template="flag: {tr1} = ({va1} >= {va2})", func=_func
                )
            case "bool":
                return cls(
                    name=op_name, template="flag: bool = bool({va1})", func=_func
                )
            case "abs":
                return cls(
                    name=op_name, template="{vr1}: {tr1} = abs({va1})", func=_func
                )
            case "not":
                return cls(
                    name=op_name, template="{vr1}: {tr1} = not {va1}", func=_func
                )
            case "inv":
                return cls(name=op_name, template="{vr1}: {tr1} = ~{va1}", func=_func)
            case "invert":
                return cls(name=op_name, template="{vr1}: {tr1} = ~{va1}", func=_func)
            case "contains":
                return cls(
                    name=op_name, template="flag: {tr1} = {va2} in {va1}", func=_func
                )
            case "str":
                return cls(
                    name=op_name, template="{vr1}: {tr1} = str({va1})", func=_func
                )
            case "repr":
                return cls(
                    name=op_name, template="{vr1}: {tr1} = repr({va1})", func=_func
                )
            case "getitem":
                return cls(
                    name=op_name,
                    template="{va2}: {ta2}\n{vr1}: {tr1} = {va1}[{va2}]",
                    func=_func,
                )
            case "setitem":
                return cls(
                    name=op_name,
                    template="{va3}: {ta3}\n{va1}[{va2}] = {va3}",
                    func=_func,
                )
            case "delitem":
                return cls(name=op_name, template="del {va1}[{va2}]", func=_func)
            case "iter":
                return cls(
                    name=op_name,
                    template="for val in {va1}:\n    val: {tr1}",
                    func=_func,
                    special="yield",
                )
            case "enter":
                return cls(
                    name=op_name,
                    template="with self as {vr1}:\n    {vr1}: {tr1}",
                    func=_func,
                )
            case "close":
                return cls(name=op_name, template="self.__close__(...)", func=_func)
            case _:
                return cls(name=op_name, template="", func=_func)

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the operator.
        """
        texts: list[str] = []
        texts.append("### {0} `{1}`".format(renderer.icon_obj("op"), self.func.name))
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.func.descr:
            texts.append(self.func.descr)

        if not self.func.overloads:
            _overload = _funcs.DocFunctionOverload(
                descr="",
                args=self.func.args,
                retval=self.func.retval,
                is_yield=self.func.is_yield,
            )
            texts.append(
                _overload.as_md_text(
                    renderer=renderer,
                    has_descr=False,
                    ignore_self=True,
                    title="",
                    title_level=3,
                )
            )
            return mdformat.text("\n\n".join(texts))
        if len(self.func.overloads) == 1:
            texts.append(
                self.func.overloads[0].as_md_text(
                    renderer=renderer,
                    has_descr=True,
                    ignore_self=True,
                    title="",
                    title_level=3,
                )
            )
            return mdformat.text("\n\n".join(texts))
        for idx, _overload in enumerate(self.func.overloads, start=1):
            texts.append(
                _overload.as_md_text(
                    renderer=renderer,
                    has_descr=True,
                    ignore_self=True,
                    title="Arguments (ver. {0})".format(idx),
                    title_level=4,
                )
            )
        return mdformat.text("\n\n".join(texts))
