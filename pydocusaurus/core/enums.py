# -*- coding: UTF-8 -*-
"""
Enums
======
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
The documentation extraction of enum class objects.
"""

import enum
import logging

from typing import Any
from typing_extensions import Literal
from collections.abc import Callable

from pydantic import BaseModel, Field

import black
import mdformat

from . import texts as _texts
from . import classes as _classes
from .inspectors import (
    get_field_docstrings,
    get_arg_default_name,
    strip_annotation_name,
)
from ..components.comprotocol import ProtocolComponent

__all__ = ("DocEnumItem", "DocEnum", "parse_enum_docs")
log = logging.getLogger("pydocusaurus")


class DocEnumItem(BaseModel):
    """The docstring of an enum item."""

    name: str = Field(min_length=1)
    """The name of the enum item."""

    type: str
    """The type of the enum item. It is usually the typehint (annotation)."""

    value: str = ""
    """The formatted value of the enum item."""

    descr: str = ""
    """The docstring of the enum item, it is defined in codes."""


class DocEnum(_classes._DocClassPrototype):
    """The docstring and basic information of an enum class.

    This serializable data type contains the parsed docstrings of the enum class.
    It is a specialized class. When rendering the documentation, the initialization
    function is replaced by the enum item details.
    """

    type: Literal["enum"] = "enum"
    """The identifier of this documentation item."""

    enum_items: list[DocEnumItem] = Field(default_factory=list)
    """The items of the enum class."""

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
        for eitem in self.enum_items:
            field_str = "{0}.{1} = {2}".format(cls_prefix, eitem.name, eitem.value)
            segments.append(field_str)
        if not segments:
            return "{0}()".format(cls_prefix)
        return "\n".join(segments)

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        names = [eitem.name for eitem in self.enum_items]
        return black.format_str(
            "{0}({1})".format(self.name, ", ".join(names)),
            mode=black.Mode(),
        ).strip()

    def table_enums(
        self,
        has_type: bool = True,
        has_value: bool = True,
        has_doc: bool = False,
    ) -> str:
        """Format the fields as a table.

        Arguments
        ---------
        has_type: `bool`
            A flag. If specified, will display the enum item type.

        has_value: `bool`
            A flag. If specified, will display the value of the enum item.

        has_doc: `bool`
            A flag. If specified, will display the docstring of the enum item.

        Returns
        -------
        #1: `str`
            The Markdown table of the enum items.
        """
        cols: list[str] = (
            ["Name"]
            + (["Type"] if has_type else [])
            + (["Value"] if has_value else [])
            + (["Description"] if has_doc else [])
        )
        idx_type: int | None = cols.index("Type") if "Type" in cols else None
        idx_value: int | None = cols.index("Value") if "Value" in cols else None
        idx_doc: int | None = (
            cols.index("Description") if "Description" in cols else None
        )
        col_styles: dict[int, Literal["l", "c", "r", "n"]] = {0: "c"}
        for idx, style in zip((idx_type, idx_value, idx_doc), ("c", "c", "l")):
            if idx:
                col_styles[idx] = style
        table = _texts.Table(
            n_rows=len(self.enum_items) + 1,
            n_cols=len(cols),
            col_styles=col_styles,
            cells={(0, 0): cols[0]},
        )
        for idx in (idx_type, idx_value):
            if idx is not None:
                table.cells[(0, idx)] = cols[idx]
        if idx_doc is not None:
            table.cells[(0, idx_doc)] = "<center>{0}</center>".format(cols[idx_doc])
        fields = self.enum_items
        for idx, field in enumerate(fields, start=1):
            name = field.name
            table.cells[(idx, 0)] = "`{0}`".format(name) if name else ""
            if idx_type is not None:
                table.cells[(idx, idx_type)] = (
                    "`{0}`".format(field.type.replace("|", R"\|")) if field.type else ""
                )
            if idx_value is not None:
                table.cells[(idx, idx_value)] = (
                    "`{0}`".format(field.value.replace("|", R"\|"))
                    if field.value
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
        return table.as_md_text()

    def _as_md_title(self, renderer: ProtocolComponent) -> str:
        """(Private) Render the Markdown title bar texts, including (1) navbar, (2)
        class signature, (3) description, (4) enums."""
        texts: list[str] = []
        texts.append(str(renderer.apibar(type="class", is_enum=True, slang=self.slang)))
        texts.append("```python\n{0}\n```".format(self.str_v2))
        if self.descr:
            texts.append(self.descr)
        if len(self.enum_items) > 0:
            texts.append("## Enums")
            texts.append(self.table_enums())
        else:
            texts.extend(["## Enums", "No enum item is defined."])
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
            The Markdown text rendered from the enum object.
        """
        texts: list[str] = []
        texts.append(self._as_md_title(renderer=renderer))
        if self.methods:
            texts.append("## Methods")
            for idx, method in enumerate(self.methods):
                if idx > 0:
                    texts.append("---")
                texts.append(method.as_md_text(renderer=renderer))
        if self.properties:
            texts.append("## Properties")
            for idx, prop in enumerate(self.properties):
                if idx > 0:
                    texts.append("---")
                texts.append(prop.as_md_text(renderer=renderer))
        if self.operators:
            texts.append("## Operators")
            for idx, op in enumerate(self.operators):
                if idx > 0:
                    texts.append("---")
                texts.append(op.as_md_text(renderer=renderer))
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
    field_docs = get_field_docstrings(cls, include_dyn_assign=True)

    def descr_fetcher(name: str) -> str | None:
        if name not in field_docs:
            log.warning("Enum field {0}.{1} is not documented.".format(cls_name, name))
            return None
        descr = field_docs[name]
        if not descr:
            log.warning(
                "Enum field {0}.{1} is documented with empty "
                "string.".format(cls_name, name)
            )
        return descr if descr else ""

    return descr_fetcher


def parse_enum_docs(cls: type[Any]) -> DocEnum:
    """Parse the docstring of an enum class.

    Arguments
    ---------
    cls: `type[Any]`
        A class object to be parsed.

    Returns
    -------
    #1: `DocClass`
        The parsed docstring of the enum class.
    """
    doc_class = _classes.parse_class_docs(cls)

    f_enum_descr = _get_field_descr_fetcher(cls)
    enum_items: list[DocEnumItem] = []

    if isinstance(cls, type) and issubclass(cls, enum.Enum):
        for name in cls._member_names_:
            descr = f_enum_descr(name)
            if descr is None:
                continue
            enum_item = cls._member_map_[name]
            enum_items.append(
                DocEnumItem(
                    name=name,
                    type=strip_annotation_name(type(enum_item.value)),
                    value=get_arg_default_name(enum_item.value),
                    descr=descr,
                )
            )

    return DocEnum(
        name=doc_class.name,
        descr=doc_class.descr,
        enum_items=enum_items,
        init_func=doc_class.init_func,
        init_func_specified=doc_class.init_func_specified,
        methods=doc_class.methods,
        properties=doc_class.properties,
        operators=doc_class.operators,
        abstract_attrs=doc_class.abstract_attrs,
        lineno=doc_class.lineno,
        slang=doc_class.slang,
    )
