# -*- coding: UTF-8 -*-
"""
Attribute Tree
==============
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
Build an attribute tree that reconstructs the structure of a package.
"""

from typing import Any
from collections.abc import Sequence, Mapping, Callable
from pydantic import BaseModel, Field

__all__ = ("AttributeTreeNode", "ModuleAttributeTree", "build_sidebar")


class AttributeTreeNode(BaseModel):
    """The node in the attribute tree."""

    name: str
    """The partial name of the current node."""

    attrs: dict[str, Any] = Field(default_factory=dict)
    """The extra attributes of the current node."""

    children: dict[str, "AttributeTreeNode"] = Field(default_factory=dict)
    """The members/children of the current node."""

    def add(
        self, segments: Sequence[str], attrs: Mapping[str, Any] | None = None
    ) -> None:
        """Recursively add segments into the tree.

        Arguments
        ---------
        segments: `list[str]`
            A sequence of name segments. Each segment represents a partial node name
            in the route. If an empty list such as `[]` is provided, it means update
            the information of the current (this) node.

        attrs: `dict[str, Any]`
            The attributes to be added to the target node. The node is routed by
            `segments` related to the current node.
        """
        if not segments:
            # Merge attributes
            if attrs:
                self.attrs.update(attrs)
            return

        head, *tail = segments

        if head not in self.children:
            self.children[head] = AttributeTreeNode(name=head)

        self.children[head].add(tail, attrs)


class ModuleAttributeTree[T]:
    """The attribute tree of a module/package.

    This tree reconstructs the member structure of a full package. It can be converted
    to a serialized dictionary/list.
    """

    def __init__(
        self,
        walk_method: Callable[[str, dict[str, Any], list[T]], T],
        root_name: str = ".",
    ) -> None:
        """Initialization.

        Arguments
        ---------
        walk_method: `(str, dict[str, Any], list[T]) -> T`
            A method used to serialize tree nodes. The input arguments are:

            1. The partial name of the node.
            2. The attributes of the current node.
            3. The serialized members of the current node.

            The method will returns a serialized object representing the current node.

        root_name: `str`
            The name of the root node.
        """
        self.root = AttributeTreeNode(name=root_name)
        self.walk_method = walk_method

    def add(
        self, node_full_name: str, node_attrs: Mapping[str, Any] | None = None
    ) -> None:
        """Add a node to the attribute tree.

        Arguments
        ---------
        node_full_name: `str`
            The full name like `"package.module.member"`.

        node_attrs: `dict[str, Any] | None`
            An optional dictionary of attributes attached to the current added node.
        """
        segments = [seg.strip() for seg in node_full_name.split(".") if seg.strip()]
        self.root.add(segments, node_attrs)

    def _dfs(self, node: AttributeTreeNode) -> T:
        """Depth-first traversal of the tree.

        Arguments
        ---------
        node: `AttributeTreeNode`
            The node to be serialized with depth-first search.

        Returns
        -------
        #1: `T`
            The serialized object for this node.
        """
        members: list[T] = []
        for child in node.children.values():
            members.append(self._dfs(child))
        return self.walk_method(node.name, node.attrs, members)

    def serialize(self) -> T:
        """Serialize the entire tree starting from root.

        Returns
        -------
        #1: `T`
            The serialized object of the root node, including all nested members.
        """
        return self._dfs(self.root)

    def serialize_unpacked(self) -> list[T]:
        """Serialize the entire tree starting from root, with the root node unpacked.

        Different from `self.serialize()`, this method will treat the root node as
        a leaf node without members, and put all members of the root as siblings.
        Therefore, the returned value is always a list.

        Returns
        -------
        #1: `list[T]`
            The list of serialized nodes.
        """
        children = self.root.children
        root_attrs = self.root.attrs.copy()
        if "type" in root_attrs:
            root_attrs["type"] = "leaf"
        members: list[T] = [
            self._dfs(AttributeTreeNode(name=self.root.name, attrs=root_attrs))
        ]
        for node in children.values():
            members.append(self._dfs(node))
        return members


def build_sidebar() -> ModuleAttributeTree[str | dict[str, Any]]:
    """Create an empty sidebar tree.

    Returns
    -------
    #1: `ModuleAttributeTree[str | dict[str, Any]]`
        An attribute tree with a customized serialization method for rendering the
        sidebar of the documentation. The returned tree is empty.
    """

    def walk_member(
        name: str, attrs: dict[str, Any], members: list[str | dict[str, Any]]
    ) -> str | dict[str, Any]:
        """(Private) The node serialization method used to build the sidebar."""
        n_type = attrs.get("type", "leaf")
        if (n_type == "leaf") or (not members):
            return str(attrs.get("path", name)).lstrip("/")
        return {
            "type": "category",
            "label": name,
            "collapsed": True,
            "link": {
                "type": "doc",
                "id": str(attrs.get("path", name)).lstrip("/"),
            },
            "items": members,
        }

    return ModuleAttributeTree(walk_method=walk_member, root_name="apis")
