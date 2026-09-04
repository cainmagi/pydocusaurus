# -*- coding: UTF-8 -*-
"""
Classes
=======
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
The documentation extraction of class objects.
"""

import abc
import inspect
import types
import annotationlib
import enum
import dataclasses
import logging
from functools import cached_property

from typing import Any
from collections.abc import Sequence
from typing_extensions import Self, Literal

from pydantic import BaseModel, Field

import mdformat

from . import texts as _texts
from . import functions as _funcs
from . import ops as _ops
from .inspectors import (
    get_obj_slang,
    get_members_defined_in_class,
    get_members_defined_in_enum,
    is_member_abstract,
    strip_annotation_name,
)
from ..components.comprotocol import ProtocolComponent

__all__ = (
    "AbstractAttrs",
    "ClassProfile",
    "DocProp",
    "DocClass",
    "parse_prop_docs",
    "parse_class_docs",
)
log = logging.getLogger("pydocusaurus")


def _add_md_section(
    texts: list[str],
    renderer: ProtocolComponent,
    title: str,
    contents: Sequence[_funcs.DocFunction | DocProp | _ops.DocOpTemplate],
) -> None:
    """(Private) Add a Markdown section.

    Arguments
    ---------
    texts: `list[str]`
        The markdown text body to be extended.

    renderer: `ProtocolComponent`
        The renderer providing component rendering.

    title: `str`
        The title of the current section.

    contents: `list[DocFunction | DocProp | DocOpTemplate]`
        The contents to be rendered.
    """
    if not contents:
        return
    texts.append(title)
    for idx, part in enumerate(contents):
        if idx > 0:
            texts.append("---")
        texts.append(part.as_md_text(renderer=renderer))


@dataclasses.dataclass
class AbstractAttrs:
    """The temporary abstract attributes of a class.

    This collection will be available when a temporary class profile is abstract.
    """

    properties: list[property | cached_property] = dataclasses.field(
        default_factory=list
    )
    """All abstract properties of this class."""

    methods: list[types.FunctionType | classmethod | staticmethod] = dataclasses.field(
        default_factory=list
    )
    """All abstract instance/class/static methods of this class."""

    operators: dict[str, types.FunctionType] = dataclasses.field(default_factory=dict)
    """All overloaded abstract operators of this class."""


@dataclasses.dataclass
class ClassProfile:
    """A temporary profile extracted from the class.

    This profile is used only to aggregate a class's attributes. The information will
    be persisted by the following docstring conversion.
    """

    properties: list[property | cached_property] = dataclasses.field(
        default_factory=list
    )
    """All properties of this class."""

    methods: list[types.FunctionType | classmethod | staticmethod] = dataclasses.field(
        default_factory=list
    )
    """All instance/class/static methods of this class."""

    operators: dict[str, types.FunctionType] = dataclasses.field(default_factory=dict)
    """All overloaded operators of this class."""

    abstract_attrs: AbstractAttrs | None = None
    """Optional abstract attributes. It is `None` when the class is not abstract."""

    def _add_property(self, member: Any) -> bool:
        """(Private) Add the member as a property. If `member` is not a property, do
        nothing. Return `True` if the member is added."""
        if not isinstance(member, (property, cached_property)):
            return False
        if self.abstract_attrs is not None and is_member_abstract(member):
            self.abstract_attrs.properties.append(member)
        else:
            self.properties.append(member)
        return True

    def _add_method(self, member: Any, allow_func: bool = True) -> bool:
        """(Private) Add the member as a method. If `member` is not a method, do
        nothing. Return `True` if the member is added."""
        if allow_func:
            if not inspect.isfunction(member):
                return False
        elif not isinstance(member, (classmethod, staticmethod)):
            return False
        if self.abstract_attrs is not None and is_member_abstract(member):
            self.abstract_attrs.methods.append(member)
        else:
            self.methods.append(member)
        return True

    def _add_op(self, member: Any, name: str) -> bool:
        """(Private) Add the member as an operator. If `member` is not an operator,
        do nothing. Return `True` if the member is added."""
        if not inspect.isfunction(member):
            return False
        if not (name.startswith("__") and name.endswith("__")):
            return False
        if self.abstract_attrs is not None and is_member_abstract(member):
            self.abstract_attrs.operators[name] = member
        else:
            self.operators[name] = member
        return True

    @classmethod
    def from_class(cls: type[Self], base_cls: type[Any]) -> Self:
        """Get the profile of a class.

        Arguments
        ---------
        base_cls: `type[Any]`
            The class where the profile will be analyzed.


        Returns
        -------
        #1: `ClassProfile`
            The analyzed class profile.
        """
        res = cls(
            abstract_attrs=(
                AbstractAttrs()
                if (isinstance(base_cls, type) and issubclass(base_cls, abc.ABC))
                or (isinstance(base_cls, abc.ABCMeta))
                else None
            )
        )
        get_members = (
            get_members_defined_in_enum
            if (isinstance(base_cls, type) and issubclass(base_cls, enum.Enum))
            else get_members_defined_in_class
        )
        for name, member in get_members(base_cls):
            if res._add_property(member):
                continue
            if res._add_method(member, allow_func=False):
                continue
            f_type = (
                _funcs.FunctionType.get_method_validator(base_cls)(member)
                if inspect.isfunction(member)
                else None
            )
            if (
                name not in ("__init__", "__str__", "__repr__")
                and f_type is not None
                and f_type == _funcs.FunctionType.METHOD
            ):
                if res._add_op(member, name=name):
                    continue
                res._add_method(member, allow_func=True)
        return res


def _default_init() -> _funcs.DocFunction:
    """The default initialization function.

    Returns
    -------
    #1: `DocFunction`
        A placeholder used as the default initialization function without any
        arguments.
    """
    return _funcs.DocFunction(
        name="__init__",
        descr="Initialization.",
        args=[],
        retval=[],
        f_type=_funcs.FunctionType.METHOD,
        prefix="",
        slang="",
        overloads=[],
    )


class DocProp(BaseModel):
    """The docstring and basic information of a class property.

    A class property can be defined by `@property` or `@functools.cached_property`.
    """

    name: str = Field(min_length=1)
    """The name of the property."""

    descr: str
    """The description body of the property."""

    type: str
    """The type of the property. It is usually the typehint (annotation)."""

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        prop_name: type = self.prop_name
        ```
        which is more compact than the default string.
        """
        return "{name}: {type} = self.{name}".format(name=self.name, type=self.type)

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        return mdformat.text(
            "@property\ndef {name}(self) -> {type}: ...".format(
                name=self.name, type=self.type
            )
        )

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the class property.
        """
        texts: list[str] = []
        texts.append("### {0} `{1}`".format(renderer.icon_obj("param"), self.name))
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.descr:
            texts.append(self.descr)

        return mdformat.text("\n\n".join(texts))


class DocClassAbstractAttrs(BaseModel):
    """Additional abstract attributes of a class. If the class is not abstract, this
    collection will fall back to `None`."""

    methods: list[_funcs.DocFunction] = Field(default_factory=list)
    """The list of abstract methods of this class."""

    properties: list[DocProp] = Field(default_factory=list)
    """The list of abstract properties of this class."""

    operators: list[_ops.DocOpTemplate] = Field(default_factory=list)
    """The list of abstract operators of this class."""

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the section.
        """
        texts: list[str] = []
        _add_md_section(
            texts, renderer=renderer, title="## Abstract methods", contents=self.methods
        )
        _add_md_section(
            texts,
            renderer=renderer,
            title="## Abstract properties",
            contents=self.properties,
        )
        _add_md_section(
            texts,
            renderer=renderer,
            title="## Abstract operators",
            contents=self.operators,
        )
        if not texts:
            return ""
        return mdformat.text("\n\n".join(texts))


class _DocClassPrototype(BaseModel):
    """(Private) The untyped prototype of the documentation item for a class.

    This prototype is used fro defining class, dataclass, and enum.
    """

    name: str = Field(min_length=1)
    """The name of the class."""

    descr: str
    """The description body of the class."""

    init_func: _funcs.DocFunction = Field(default_factory=_default_init)
    """The initialization function of the class."""

    init_func_specified: bool = True
    """A flag. When it is on, it means that the initialization function has been
    defined by user."""

    methods: list[_funcs.DocFunction] = Field(default_factory=list)
    """The list of methods of this class."""

    properties: list[DocProp] = Field(default_factory=list)
    """The list of properties of this class."""

    operators: list[_ops.DocOpTemplate] = Field(default_factory=list)
    """The list of operators of this class."""

    abstract_attrs: DocClassAbstractAttrs | None = None
    """Additional abstract attributes. Will present only when the class is abstract.
    For the protocols, this value will be always `None`."""

    slang: str = ""
    """The internal code identifying this class."""

    lineno: int = 0
    """The line number where the class is defined. If the number is unknown, this value
    will be `0`."""

    @property
    def is_abstract(self) -> bool:
        """A flag specifying whether the class is abstract."""
        return self.abstract_attrs is not None

    @cached_property
    def is_context(self) -> bool:
        """A flag specifying whether the class is a context."""
        if self.abstract_attrs is not None:
            for op in self.abstract_attrs.operators:
                if op.name == "enter":
                    return True
        for op in self.operators:
            if op.name == "enter":
                return True
        return False

    @cached_property
    def is_private(self) -> bool:
        """A flag specifying whether the class is private."""
        valid = "(private)"
        return self.descr.strip()[: len(valid)].casefold() == valid

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        ClassName(arg1: type1, arg2: type2 = default2, ...)
        ```
        which is more compact than the default string.
        """
        init_func = self.init_func
        cls_p = _funcs.DocFunction(
            name=self.name, descr="", prefix="", f_type=_funcs.FunctionType.METHOD
        )
        if not init_func.overloads:
            _overload = _funcs.DocFunctionOverload(
                descr="", args=init_func.args, retval=[]
            )
            return _funcs.DocFunctionOverload.str_v2(_overload, parent=cls_p)
        _overloads = [
            _overload.str_v2(parent=cls_p) for _overload in init_func.overloads
        ]
        return "\n".join(_overloads)

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        init_func = self.init_func
        cls_p = _funcs.DocFunction(
            name="__init__", descr="", prefix="", f_type=_funcs.FunctionType.METHOD
        )
        if not init_func.overloads:
            _overload = _funcs.DocFunctionOverload(
                descr="", args=init_func.args, retval=[]
            )
            return _funcs.DocFunctionOverload.str_v1(_overload, parent=cls_p)
        _overloads = [
            _overload.str_v1(parent=cls_p) for _overload in init_func.overloads
        ]
        return "\n\n".join(_overloads)

    def _topbar(self, renderer: ProtocolComponent) -> str:
        """(Private) Render the class top bar."""
        return str(
            renderer.apibar(
                type="class",
                is_abstract=self.is_abstract,
                is_ctx=self.is_context,
                is_private=self.is_private,
                slang=self.slang,
            )
        )

    def _as_md_title(self, renderer: ProtocolComponent) -> str:
        """(Private) Render the Markdown title bar texts, including (1) navbar, (2)
        class signature, (3) description, (4) arguments."""
        texts: list[str] = []
        texts.append(self._topbar(renderer))
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.is_abstract:
            texts.append("This is an abstract class requiring further implementation.")
        if self.descr:
            texts.append(self.descr)

        if not self.init_func_specified:
            texts.extend(["## Arguments", "Initialization function is not specified."])
            return mdformat.text("\n\n".join(texts))

        arg_secs: list[str] = []
        init_func = self.init_func
        if not init_func.overloads:
            _overload = _funcs.DocFunctionOverload(
                descr="", args=init_func.args, retval=init_func.retval
            )
            _arg_text = _overload.as_md_text(
                renderer=renderer,
                has_descr=False,
                ignore_self=True,
                title="Arguments",
                title_level=2,
            )
            if _arg_text:
                arg_secs.append(_arg_text)
            texts.extend(
                arg_secs if arg_secs else ["## Arguments", "No argument is needed."]
            )
            return mdformat.text("\n\n".join(texts))
        if len(init_func.overloads) == 1:
            _arg_text = init_func.overloads[0].as_md_text(
                renderer=renderer,
                has_descr=True,
                ignore_self=True,
                title="Arguments",
                title_level=2,
            )
            if _arg_text:
                arg_secs.append(_arg_text)
            texts.extend(
                arg_secs if arg_secs else ["## Arguments", "No argument is needed."]
            )
            return mdformat.text("\n\n".join(texts))
        for idx, _overload in enumerate(init_func.overloads, start=1):
            _arg_text = _overload.as_md_text(
                renderer=renderer,
                has_descr=True,
                ignore_self=True,
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
            The Markdown text rendered from the class content.
        """
        texts: list[str] = []
        texts.append(self._as_md_title(renderer=renderer))
        if self.abstract_attrs is not None:
            _text = self.abstract_attrs.as_md_text(renderer=renderer)
            if _text:
                texts.append(_text)
        _add_md_section(
            texts, renderer=renderer, title="## Methods", contents=self.methods
        )
        _add_md_section(
            texts, renderer=renderer, title="## Properties", contents=self.properties
        )
        _add_md_section(
            texts, renderer=renderer, title="## Operators", contents=self.operators
        )
        return mdformat.text("\n\n".join(texts))


class DocClass(_DocClassPrototype):
    """The docstring and basic information of a class.

    This serializable data type contains the parsed docstrings of the class body, the
    initialization function, the properties, the methods, and the overloaded operators.
    """

    type: Literal["class"] = "class"
    """The identifier of this documentation item."""


def parse_prop_docs(prop: property | cached_property, parent_name: str = "") -> DocProp:
    """Parse the docstring of a class property.

    Arguments
    ---------
    prop: `property | cached_property`
        A class property/cached_property to be parsed.

    parent_name: `str`
        The name of the parent class. This value is only used for displaying logging
        messages.

    Returns
    -------
    #1: `DocProp`
        The parsed docstring of the property.
    """
    if isinstance(prop, cached_property):
        name = prop.func.__name__
        descr = prop.func.__doc__
        annotations = annotationlib.get_annotations(
            prop.func, format=annotationlib.Format.VALUE
        )
        return_annotation = annotations.get("return", "Unknown")
        anno = strip_annotation_name(return_annotation)
    else:
        name = prop.__name__
        descr = prop.__doc__
        _getter = prop.fget
        anno = (
            strip_annotation_name(
                annotationlib.get_annotations(
                    _getter, format=annotationlib.Format.VALUE
                ).get("return", "Unknown")
            )
            if _getter is not None
            else "Unknown"
        )
    descr = inspect.cleandoc(descr) if descr else ""
    if not descr:
        log.warning(
            "Property {0}.{1} does not provide its main "
            "docstring.".format(parent_name, name)
        )
    if anno == "Unknown":
        log.warning("Property {0}.{1} is not annotated.".format(parent_name, name))
    return DocProp(name=name, descr=descr, type=anno)


def parse_class_docs(cls: type[Any]) -> DocClass:
    """Parse the docstring of a class.

    Arguments
    ---------
    cls: `type[Any]`
        A class object to be parsed.

    Returns
    -------
    #1: `DocClass`
        The parsed docstring of the class.
    """
    name = str(cls.__name__).strip()
    doc_secs = _texts.Section.from_md_text(cls.__doc__)
    descr = (
        doc_secs[0].as_md_text()
        if (len(doc_secs) > 0 and doc_secs[0].level == 0)
        else ""
    )
    if not descr:
        log.warning("Class {0} does not provide its main docstring.".format(name))

    # Parse init func
    doc_init_func = (
        _funcs.parse_func_docs(func=cls.__init__, base_cls=cls)
        if inspect.isfunction(cls.__init__)
        else _default_init()
    )

    # Parse profile
    profile = ClassProfile.from_class(cls)

    _methods: list[_funcs.DocFunction] = [
        _funcs.parse_func_docs(func, cls) for func in profile.methods
    ]
    _props: list[DocProp] = [parse_prop_docs(prop, name) for prop in profile.properties]
    _ops_val: list[_ops.DocOpTemplate] = [
        _ops.DocOpTemplate.from_func(op, base_cls=cls)
        for _, op in profile.operators.items()
    ]
    _abstract_attrs = profile.abstract_attrs

    _init = getattr(cls, "__init__", None)
    _init_code = getattr(_init, "__code__", None) if _init is not None else None
    _init_coname = (
        getattr(_init_code, "co_filename", None) if _init_code is not None else None
    )
    _init_name = getattr(_init, "__qualname__", None) if _init is not None else None
    _init_module = getattr(_init, "__module__", None) if _init is not None else None
    _this_module = getattr(cls, "__module__", None)

    return DocClass(
        name=name,
        descr=descr,
        init_func=doc_init_func,
        init_func_specified=(
            (not (_init_coname is not None and _init_coname == "<string>"))
            and (
                (not isinstance(_init_name, str))
                or _init_name.startswith(name)
                or bool(
                    _init_module
                    and _this_module
                    and str(_init_module).split(maxsplit=2)[0]
                    == str(_this_module).split(maxsplit=2)[0]
                )
            )
        ),
        methods=_methods,
        properties=_props,
        operators=_ops_val,
        abstract_attrs=(
            DocClassAbstractAttrs(
                methods=[
                    _funcs.parse_func_docs(func, cls)
                    for func in _abstract_attrs.methods
                ],
                properties=[
                    parse_prop_docs(prop, name) for prop in _abstract_attrs.properties
                ],
                operators=[
                    _ops.DocOpTemplate.from_func(op, base_cls=cls)
                    for _, op in _abstract_attrs.operators.items()
                ],
            )
            if _abstract_attrs is not None
            else None
        ),
        slang=get_obj_slang(cls),
    )
