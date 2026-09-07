# -*- coding: UTF-8 -*-
"""
TypedDict
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
The documentation extraction of typed dictionaries.
"""

import inspect
import logging

from typing import Any
from typing_extensions import (
    Literal,
    NotRequired,
    Required,
    is_typeddict,
    get_origin,
    get_args,
)
from functools import cached_property

from pydantic import BaseModel, Field

import black
import mdformat

from . import texts as _texts
from .inspectors import get_field_docstrings, get_obj_slang, strip_annotation_name
from ..components.comprotocol import ProtocolComponent

__all__ = ("DocTypedDictItem", "parse_typeddict_doc")
log = logging.getLogger("pydocusaurus")


class DocTypedDictItem(BaseModel):
    """The docstring of a typed dictionary item."""

    name: str = Field(min_length=1)
    """The name of the dict item."""

    type: str
    """The type of the dict item. It is usually the typehint (annotation)."""

    optional: bool = False
    """A flag specifying whether the dict item is optional. It is specified by
    `NotRequired` annotation or `total=False` subclass."""

    descr: str = ""
    """The docstring of the dict item, it is defined in codes."""


class DocTypedDict(BaseModel):
    """The docstring and basic information of a class.

    This serializable data type contains the parsed docstrings of the class body, the
    initialization function, the properties, the methods, and the overloaded operators.
    """

    type: Literal["typeddict"] = "typeddict"
    """The identifier of this documentation item."""

    name: str = Field(min_length=1)
    """The name of the class."""

    descr: str
    """The description body of the class."""

    dict_items: list[DocTypedDictItem] = Field(default_factory=list)
    """The key-val items of the typed dictionary."""

    slang: str = ""
    """The internal code identifying this function. It needs to be specified when the
    function is a vanilla function (`f_type` is `"function"`) to provide the
    identification of the source code."""

    lineno: int = 0
    """The line number where the typed dictionary is defined. If the number is unknown,
    this value will be `0`."""

    @cached_property
    def is_private(self) -> bool:
        """A flag specifying whether the type is private."""
        valid = "(private)"
        return self.descr.strip()[: len(valid)].casefold() == valid

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The v2 string is in the following format:
        ```python
        ret: type = DictName(key1: type1, key2: type2, ...)
        ```

        Note that the v2 string is longer than the default string for `TypedDict`.
        """
        res_p = black.format_str(
            "def {name}({args}): ...".format(
                name=self.name,
                args=", ".join(
                    "{name}: {type}".format(name=arg.name, type=arg.type)
                    for arg in self.dict_items
                ),
            ),
            mode=black.Mode(),
        ).strip()[4:]
        res_p = res_p[: res_p.rfind(":")]
        return res_p

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        res_p = black.format_str(
            "{name}({args})".format(
                name=self.name,
                args=", ".join(
                    "{name}".format(name=arg.name) for arg in self.dict_items
                ),
            ),
            mode=black.Mode(),
        ).strip()
        return res_p

    def table_keywords(
        self,
        renderer: ProtocolComponent,
        has_type: bool = True,
        has_required: bool = True,
        has_doc: bool = True,
    ) -> str:
        """Format the keywords as a table.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        has_type: `bool`
            A flag. If specified, will display the keyword-value type.

        has_required: `bool`
            A flag. If specified, will display whether the keyword-value is required.

        has_doc: `bool`
            A flag. If specified, will display the docstring of the keyword-value.

        Returns
        -------
        #1: `str`
            The Markdown table of the keywords.
        """
        cols: list[str] = (
            ["Name"]
            + (["Type"] if has_type else [])
            + (["Required"] if has_required else [])
            + (["Description"] if has_doc else [])
        )
        idx_type: int | None = cols.index("Type") if "Type" in cols else None
        idx_required: int | None = (
            cols.index("Required") if "Required" in cols else None
        )
        idx_doc: int | None = (
            cols.index("Description") if "Description" in cols else None
        )
        col_styles: dict[int, Literal["l", "c", "r", "n"]] = {0: "c"}
        for idx, style in zip((idx_type, idx_required, idx_doc), ("c", "c", "l")):
            if idx:
                col_styles[idx] = style
        table = _texts.Table(
            n_rows=len(self.dict_items) + 1,
            n_cols=len(cols),
            col_styles=col_styles,
            cells={(0, 0): cols[0]},
        )
        for idx in (idx_type, idx_required):
            if idx is not None:
                table.cells[(0, idx)] = cols[idx]
        if idx_doc is not None:
            table.cells[(0, idx_doc)] = "<center>{0}</center>".format(cols[idx_doc])
        keywords = self.dict_items
        for idx, keyword in enumerate(keywords, start=1):
            name = keyword.name
            table.cells[(idx, 0)] = "`{0}`".format(name) if name else ""
            if idx_type is not None:
                table.cells[(idx, idx_type)] = (
                    "`{0}`".format(_texts.santize_doc_cell(keyword.type))
                    if keyword.type
                    else ""
                )
            if idx_required is not None:
                table.cells[(idx, idx_required)] = (
                    renderer.inline_icon("check") if (not keyword.optional) else ""
                )
            if idx_doc is not None:
                table.cells[(idx, idx_doc)] = _texts.santize_doc_cell(
                    mdformat.text(
                        keyword.descr,
                        options={"wrap": "no"},
                    )
                )
        return table.as_md_text()

    def _as_md_title(self, renderer: ProtocolComponent) -> str:
        """(Private) Render the Markdown title bar texts, including (1) navbar, (2)
        dict signature, (3) description, (4) keywords."""
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
        if len(self.dict_items) > 0:
            texts.append("## Keywords")
            texts.append(self.table_keywords(renderer=renderer))
        else:
            texts.extend(["## Keywords", "No keyword is defined."])
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
            The Markdown text rendered from the typed dictionary.
        """
        texts: list[str] = []
        texts.append(self._as_md_title(renderer=renderer))
        return mdformat.text("\n\n".join(texts))


def parse_typeddict_doc(cls: type[Any]) -> DocTypedDict:
    """Parse the docstring of a typed dictionary class.

    Arguments
    ---------
    cls: `type[Any]`
        A class object to be parsed. It needs to be a typed dictionary.

    Returns
    -------
    #1: `DocTypedDict`
        The parsed docstring of the typed dictionary class.
    """
    if not is_typeddict(cls):
        raise TypeError("{0} is not a TypedDict".format(cls.__name__))

    td_items: list[DocTypedDictItem] = []
    tdict_docs = get_field_docstrings(cls)

    for key, annotation in cls.__annotations__.items():
        origin = get_origin(annotation)
        doc = tdict_docs.get(key)
        doc = doc if doc else ""
        if not doc:
            log.warning(
                'TypedDict item {0}["{1}"] is not documented.'.format(cls.__name__, key)
            )
        if origin is Required:
            required = True
            actual_type = get_args(annotation)[0]
        elif origin is NotRequired:
            required = False
            actual_type = get_args(annotation)[0]
        else:
            required = key in cls.__required_keys__
            actual_type = annotation

        td_items.append(
            DocTypedDictItem(
                name=key,
                type=strip_annotation_name(actual_type),
                optional=(not required),
                descr=doc,
            )
        )

    doc = cls.__doc__
    doc = inspect.cleandoc(doc) if doc else ""
    if not doc:
        log.warning(
            "TypedDict {0} does not provide its main docstring.".format(cls.__name__)
        )
    return DocTypedDict(
        name=cls.__name__,
        descr=doc,
        dict_items=td_items,
        slang=get_obj_slang(cls),
    )
