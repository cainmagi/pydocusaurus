# -*- coding: UTF-8 -*-
"""
Page
============
@ pyDocusaurus - Renderer

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The synthesis of an API documentation page.
"""

import os
import types

from typing import Any

from pydantic import BaseModel, Field
import yaml

from ..core import functions as _funcs
from ..core import classes as _classes
from ..core import datacls as _datacls
from ..core import enums as _enums
from ..core import typeddicts as _tdicts
from ..core import protocols as _protocols
from ..core import typealiases as _taliases
from ..core import modules as _modules
from ..core import inspectors as _inspectors
from ..core import walker as _walker

from .components import Components

__all__ = ("RendererPage", "render_obj")


class RendererPage(BaseModel):
    """The renderer of the an API page."""

    data: (
        _modules.DocModule
        | _funcs.DocFunction
        | _classes.DocClass
        | _datacls.DocDataClass
        | _enums.DocEnum
        | _tdicts.DocTypedDict
        | _protocols.DocProtocol
        | _taliases.DocTypeAlias
    ) = Field(discriminator="type")
    """The data used for rendering the page."""

    @property
    def slug(self) -> str:
        """The documentation address slug."""
        return _inspectors.get_slug(self.data.slang)

    @property
    def short_descr(self) -> str:
        """The short description of the data extracted from the first sentence."""
        descr = self.data.descr
        if isinstance(self.data, _funcs.DocFunction):
            _overloads = self.data.overloads
            if (not descr) and _overloads:
                for _overload in _overloads:
                    if _overload.descr:
                        descr = _overload.descr
                        break
        return _inspectors.get_short_descr(descr)

    @property
    def id(self) -> str:
        """Get the ID of this page."""
        if self.data.type == "module":
            return "index"
        return self.data.name

    @property
    def file_path(self) -> str:
        """Get the path of the output file where the page conent supposes to be
        saved."""
        slug = _inspectors.get_slug(self.data.slang)
        slug = os.path.normpath(slug.strip("/"))
        if self.data.type == "module":
            return os.path.join(slug, "index.mdx")
        return slug + ".mdx"

    @property
    def metadata(self) -> dict[str, str]:
        """The YAML heading containing the docusaurus metadata."""
        name = self.data.name
        if name == ".":
            title = "Overview of APIs"
            sidebar_label = "Overview"
        else:
            title = self.data.name
            sidebar_label = title
        return {
            "id": self.id,
            "title": title,
            "sidebar_label": sidebar_label,
            "slug": self.slug,
            "description": self.short_descr,
        }

    def render(self) -> str:
        """Render the page as an MDX file.

        Returns
        -------
        #1: `str`
            The rendered page text in the MDX format.
        """
        texts: list[str] = []
        renderer = Components()
        texts.append(
            "---\n{0}\n---".format(
                yaml.safe_dump(
                    self.metadata, stream=None, indent=2, sort_keys=False
                ).strip()
            )
        )
        content = self.data.as_md_text(renderer=renderer)
        headers = renderer.get_headers()
        if headers:
            texts.append(renderer.get_headers())
        texts.append(content)
        return "\n\n".join(texts)


def render_obj(obj: Any) -> RendererPage | None:
    """Render an arbitrary object as a documentation page.

    Arguments
    ---------
    obj: `Any`
        The object to be rendered, it can be a class, function, or a module.

        If this argument is a method, the method will be interpreted as a function.

    Returns
    -------
    #1: `RendererPage | None`
        The rendered page object. Will be `None` if the given obj cannot be rendered
        as a documentation page.
    """
    otype = _walker.PackageWalker.get_member_type(obj)
    doc_obj = _walker.PackageWalker.parse_module_member(obj, value_type=otype)
    if isinstance(obj, types.ModuleType) and isinstance(doc_obj, _modules.DocModule):
        for member, is_alias in _walker.PackageWalker.iter_module_members(obj):
            doc_obj.add_member(member, is_alias)
    return RendererPage(data=doc_obj) if doc_obj is not None else None
