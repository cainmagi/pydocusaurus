# -*- coding: UTF-8 -*-
"""
API Bar
============
@ pyDocusaurus - Components

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The synthesis of the API top bar.
"""

from typing_extensions import Literal

from pydantic import BaseModel, Field

__all__ = ("ComponentAPIBar",)


class ComponentAPIBar(BaseModel):
    """The renderer of the top API bar."""

    name: str = Field(min_length=1, default="APITopBar")
    """The name of the top bar."""

    type: Literal["func", "class", "module", "package", "type"]
    """The type of the API. It is usually the first icon."""

    slang: str = ""
    """The unique code used for identifying the top bar. It is usually the full
    route-name of the object to be described.
    """

    is_data_class: bool = False
    """A flag. If specified, will render the dataclass icon."""

    is_enum: bool = False
    """A flag. If specified, will render the enum icon."""

    is_ctx: bool = False
    """A flag. If specified, will render the context icon."""

    is_decorator: bool = False
    """A flag. If specified, will render the decorator icon."""

    is_mixin: bool = False
    """A flag. If specified, will render the mixin icon."""

    is_component: bool = False
    """A flag. If specified, will render the component icon."""

    is_private: bool = False
    """A flag. If specified, will render the private icon."""

    is_abstract: bool = False
    """A flag. If specified, will render the abstract icon."""

    def __str__(self) -> str:
        optional: list[str] = [""]
        if self.is_data_class:
            optional.append("isDataClass={true}")
        if self.is_enum:
            optional.append("isEnum={true}")
        if self.is_ctx:
            optional.append("isContext={true}")
        if self.is_decorator:
            optional.append("isDecorator={true}")
        if self.is_mixin:
            optional.append("isMixin={true}")
        if self.is_component:
            optional.append("isComponent={true}")
        if self.is_private:
            optional.append("isPrivate={true}")
        if self.is_abstract:
            optional.append("isAbstract={true}")
        if self.slang:
            optional.append('source="{0}"'.format(self.slang))
        return R'<{name} type="{type}"{optional} />'.format(
            name=self.name, type=self.type, optional=" ".join(optional)
        )
