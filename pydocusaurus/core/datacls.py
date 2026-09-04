# -*- coding: UTF-8 -*-
"""
Data Classes
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
The documentation extraction of data class objects and PyDantic models.
"""

import dataclasses
import logging

from typing import Any
from typing_extensions import Literal
from collections.abc import Callable

from pydantic import BaseModel, Field

import mdformat

from . import texts as _texts
from . import functions as _funcs
from . import classes as _classes
from .inspectors import (
    get_field_docstrings,
    get_field_default,
    strip_annotation_name,
    unwrap_annotated_annotation,
)
from ..components.comprotocol import ProtocolComponent

__all__ = ("DocField", "DocDataClass", "parse_dataclass_docs")
log = logging.getLogger("pydocusaurus")


class DocField(BaseModel):
    """The docstring of a data model/class field."""

    name: str = Field(min_length=1)
    """The name of the field."""

    type: str
    """The type of the field. It is usually the typehint (annotation)."""

    default: str = ""
    """The formatted default value of the field."""

    init_skipped: bool = False
    """A flag. If specified, this field should be skipped in the initialization."""

    descr: str = ""
    """The docstring of the field, it is defined in codes."""

    doc: str = ""
    """The extra dynamic/run-time docstring of the field. It is not used when rendering
    the documentation."""


class DocDataClass(_classes._DocClassPrototype):
    """The docstring and basic information of a data model/class.

    This serializable data type contains the parsed docstrings of the data class/model.
    It is a specialized class. When rendering the documentation, the initialization
    function is replaced by the field details.
    """

    type: Literal["dataclass"] = "dataclass"
    """The identifier of this documentation item."""

    fields: list[DocField] = Field(default_factory=list)
    """The data fields of the data class/model."""

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        ClassName(field1: type1, field2: type2 = default2, ...)
        ```
        which is more compact than the default string.
        """

        cls_prefix = self.name
        segments: list[str] = []
        for field in self.fields:
            if field.init_skipped:
                continue
            field_str = "{0}: {1}".format(field.name, field.type)
            if field.default:
                field_str = "{0} = {1}".format(field_str, field.default)
            segments.append(field_str)
        total_len = 2 * len(segments) + sum(
            (len(field_str) for field_str in segments), 0
        )
        if (total_len + len(cls_prefix)) < 86:
            return "{0}({1})".format(cls_prefix, ", ".join(segments))
        if total_len < 84:
            return "{0}(\n    {1}\n)".format(cls_prefix, ", ".join(segments))
        return "{0}(\n{1}\n)".format(
            cls_prefix, ",\n".join("    {0}".format(seg) for seg in segments)
        )

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        cls_p = _funcs.DocFunction(
            name="__init__",
            descr="",
            prefix="",
            f_type=_funcs.FunctionType.FUNCTION,
        )
        _overload = _funcs.DocFunctionOverload(
            descr="",
            args=[
                _funcs.DocArgument(
                    name=field.name,
                    type=field.type,
                    default=(field.default if field.default else "undefined"),
                )
                for field in self.fields
                if (not field.init_skipped)
            ],
            retval=[],
        )
        return _funcs.DocFunctionOverload.str_v1(_overload, parent=cls_p)

    @staticmethod
    def _add_table_field(
        table: _texts.Table,
        renderer: ProtocolComponent,
        idx: int,
        field: DocField,
        idx_type: int | None = None,
        idx_required: int | None = None,
        idx_default: int | None = None,
        idx_doc: int | None = None,
    ) -> None:
        """Format and add a field as a table row.

        Arguments
        ---------
        table: `Table`
            The table where the field will be added.

        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        idx: `int`
            The index of the current field.

        field: `DocField`
            The data of the field to be added.

        idx_type: `int | None`
            The index of the column specifying the type. If not provided, will not
            add it.

        idx_required: `int | None`
            The index of the column specifying whether the field is required. If not
            provided, will not add it.

        idx_default: `int | None`
            The index of the column specifying the default value. If not provided, will
            not add it.

        idx_doc: `int | None`
            The index of the column specifying the description text. If not provided,
            will not add it.
        """
        name = field.name
        table.cells[(idx, 0)] = "`{0}`".format(name) if name else ""
        if idx_type is not None:
            table.cells[(idx, idx_type)] = (
                "`{0}`".format(field.type.replace("|", R"\|")) if field.type else ""
            )
        if idx_required is not None:
            table.cells[(idx, idx_required)] = (
                renderer.inline_icon("check") if (not field.default) else ""
            )
        if idx_default is not None:
            table.cells[(idx, idx_default)] = (
                "`{0}`".format(field.default.replace("|", R"\|"))
                if field.default
                else ""
            )
        if idx_doc is not None:
            table.cells[(idx, idx_doc)] = (
                mdformat.text(
                    field.descr,
                    options={"wrap": "no"},
                )
                .strip()
                .replace("|", R"\|")
            )

    def table_fields(
        self,
        renderer: ProtocolComponent,
        has_type: bool = True,
        has_required: bool = True,
        has_default: bool = False,
        has_doc: bool = True,
    ) -> str:
        """Format the fields as a table.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        has_type: `bool`
            A flag. If specified, will display the field type.

        has_required: `bool`
            A flag. If specified, will display whether the field is required.

        has_default: `bool`
            A flag. If specified, will display the default value of the field.

        has_doc: `bool`
            A flag. If specified, will display the docstring of the field.

        Returns
        -------
        #1: `str`
            The Markdown table of the fields.
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
            n_rows=len(self.fields) + 1,
            n_cols=len(cols),
            col_styles=col_styles,
            cells={(0, 0): cols[0]},
        )
        for idx in (idx_type, idx_required, idx_default):
            if idx is not None:
                table.cells[(0, idx)] = cols[idx]
        if idx_doc is not None:
            table.cells[(0, idx_doc)] = "<center>{0}</center>".format(cols[idx_doc])
        fields = self.fields
        for idx, field in enumerate(fields, start=1):
            self._add_table_field(
                table,
                renderer=renderer,
                idx=idx,
                field=field,
                idx_type=idx_type,
                idx_required=idx_required,
                idx_default=idx_default,
                idx_doc=idx_doc,
            )
        return table.as_md_text()

    def _as_md_title(self, renderer: ProtocolComponent) -> str:
        """(Private) Render the Markdown title bar texts, including (1) navbar, (2)
        class signature, (3) description, (4) fields."""
        texts: list[str] = []
        texts.append(
            str(renderer.apibar(type="class", is_data_class=True, slang=self.slang))
        )
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.descr:
            texts.append(self.descr)
        if len(self.fields) > 0:
            texts.append("## Fields")
            texts.append(self.table_fields(renderer=renderer))
        else:
            texts.extend(["## Fields", "No field is defined."])
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
            The Markdown text rendered from the data class.
        """
        texts: list[str] = []
        texts.append(self._as_md_title(renderer=renderer))
        if self.abstract_attrs is not None:
            _text = self.abstract_attrs.as_md_text(renderer=renderer)
            if _text:
                texts.append(_text)
        _classes._add_md_section(
            texts, renderer=renderer, title="## Methods", contents=self.methods
        )
        _classes._add_md_section(
            texts, renderer=renderer, title="## Properties", contents=self.properties
        )
        _classes._add_md_section(
            texts, renderer=renderer, title="## Operators", contents=self.operators
        )
        return mdformat.text("\n\n".join(texts))


def _get_field_descr_fetcher(cls: type[Any]) -> Callable[[str], str | None]:
    """Get a fetcher of the field item descriptions.

    Arguments
    ---------
    cls: `type[Any]`
        A class object to be parsed.

    Returns
    -------
    #1: `(str) -> str | None`
        A function accepting the field name and returning the description.

        If the description is undefined, the function will return `None`. In this case,
        the field may be private.
    """
    cls_name = cls.__name__
    field_docs = get_field_docstrings(cls)

    def descr_fetcher(name: str) -> str | None:
        if name not in field_docs:
            log.warning(
                "DataClass field {0}.{1} is undocumented.".format(cls_name, name)
            )
            return None
        descr = field_docs[name]
        if not descr:
            log.warning(
                "DataClass field {0}.{1} is documented with empty "
                "string.".format(cls_name, name)
            )
        return descr if descr else ""

    return descr_fetcher


def _parse_fields_pydantic(cls: type[Any]) -> list[DocField]:
    """Parse the fields of a pydantic model.

    Arguments
    ---------
    cls: `type[Any]`
        A data model object to be parsed.

    Returns
    -------
    #1: `list[DocField]`
        The list of parsed model fields.
    """
    fields: list[DocField] = []
    if (not isinstance(cls, type)) or (not issubclass(cls, BaseModel)):
        raise TypeError(
            "Cannot parse the class because it is not a pydantic model: "
            "{0}".format(cls.__name__)
        )
    f_descr = _get_field_descr_fetcher(cls)
    for name, field in cls.model_fields.items():
        descr = f_descr(name)
        if descr is None:
            continue
        fields.append(
            DocField(
                name=name,
                type=strip_annotation_name(
                    unwrap_annotated_annotation(field.annotation)
                ),
                default=get_field_default(field.default, field.default_factory),
                init_skipped=(field.init is not None) and (not field.init),
                descr=descr,
                doc=field.description if field.description else "",
            )
        )
    return fields


def _parse_fields_dataclass(cls: type[Any]) -> list[DocField]:
    """Parse the fields of a dataclass.

    Arguments
    ---------
    cls: `type[Any]`
        A dataclass object to be parsed.

    Returns
    -------
    #1: `list[DocField]`
        The list of parsed dataclass fields.
    """
    fields: list[DocField] = []
    if not dataclasses.is_dataclass(cls):
        raise TypeError(
            "Cannot parse the class because it is not a dataclass: "
            "{0}".format(cls.__name__)
        )
    f_descr = _get_field_descr_fetcher(cls)
    for field in dataclasses.fields(cls):
        descr = f_descr(field.name)
        if descr is None:
            continue
        fields.append(
            DocField(
                name=field.name,
                type=strip_annotation_name(unwrap_annotated_annotation(field.type)),
                default=get_field_default(field.default, field.default_factory),
                init_skipped=(field.init is not None) and (not field.init),
                descr=descr,
                doc=field.doc if field.doc else "",
            )
        )
    return fields


def parse_dataclass_docs(cls: type[Any]) -> DocDataClass:
    """Parse the docstring of a data model/class.

    Arguments
    ---------
    cls: `type[Any]`
        A class object to be parsed.

    Returns
    -------
    #1: `DocClass`
        The parsed docstring of the data model/class.
    """
    doc_class = _classes.parse_class_docs(cls)

    fields: list[DocField] = []
    if isinstance(cls, type) and issubclass(cls, BaseModel):
        fields.extend(_parse_fields_pydantic(cls))
    elif dataclasses.is_dataclass(cls):
        fields.extend(_parse_fields_dataclass(cls))

    return DocDataClass(
        name=doc_class.name,
        descr=doc_class.descr,
        fields=fields,
        init_func=doc_class.init_func,
        init_func_specified=doc_class.init_func_specified,
        methods=doc_class.methods,
        properties=doc_class.properties,
        operators=doc_class.operators,
        abstract_attrs=doc_class.abstract_attrs,
        lineno=doc_class.lineno,
        slang=doc_class.slang,
    )
