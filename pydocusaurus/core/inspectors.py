# -*- coding: UTF-8 -*-
"""
Inspectors
==========
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
The functionalities related to inspecting and analyzing objects.
"""

import os
import re
import ast
import sys
import enum
import inspect
import types
import functools
import dataclasses
import annotationlib

from typing import Any
from typing_extensions import Annotated, is_typeddict, get_args, get_origin
from collections.abc import (
    Sequence,
    Generator,
    Iterator,
    Callable,
    AsyncGenerator,
    AsyncIterator,
    AsyncIterable,
)

import astunparse
import black
from pydantic import BaseModel
from pydantic_core import PydanticUndefined

__all___ = (
    "get_mro",
    "get_obj_slang",
    "is_user_defined_method",
    "get_members_defined_in_class",
    "get_members_defined_in_enum",
    "get_field_docstrings",
    "get_arg_default_name",
    "get_func_signature",
    "get_field_default",
    "is_multival_tuple",
    "is_member_abstract",
    "is_func_yield",
    "unwrap_annotated_annotation",
    "unpack_annotation",
    "get_short_descr",
    "get_slug",
    "relative_url_path",
)


ANNO_NAME_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_\.]*)\b")
"""The name pattern used for revising annotation items."""


def get_mro(
    cls: type[Any], stop_by: Callable[[type[Any]], bool] | None
) -> list[type[Any]]:
    """Get the mro of a class.

    Arguments
    ---------
    cls: `type[Any]`
        The class where the MRO will be picked.

    stop_by: `((type[Any]) -> bool) | None`
        An optional stop indicator. If this function returns `True`, it means that
        the class is detected to be a stopper.

    Returns
    -------
    #1: `list[type[Any]]`
        The MRO list of `cls`.
    """
    res: list[type[Any]] = []
    _res: set[type[Any]] = set()

    # The typed dictionary does not use mro, it needs to be handled specially.
    if is_typeddict(cls):
        res.append(cls)
        _res.add(cls)
        _cls_list: set[type[Any]] = set((cls,))
        while bases := getattr(_cls_list.pop(), "__orig_bases__", []):
            for base in bases:
                _origin = get_origin(base) or base
                if not isinstance(_origin, type):
                    break
                if stop_by is not None:
                    if stop_by(_origin):
                        break
                if _origin not in _res:
                    _res.add(_origin)
                    res.append(_origin)
                    _cls_list.add(_origin)
            if not _cls_list:
                break
        return res

    for base in cls.__mro__:
        if stop_by is not None:
            if stop_by(base):
                break
        else:
            if base in (type, object):
                break
        if base not in _res:
            _res.add(base)
            res.append(base)

    return res


def get_obj_slang(obj: Any, skip_root_module: bool = True) -> str:
    """Get the full slang of a function/class/variable in a module.

    > [!warning]
    > Note that the efficiency of this method is low when the inspected object is not
    a function/class. When inspecting all members in a module, it is better using
    `get_member_slangs(...)`.

    Arguments
    ---------
    obj: `Any`
        The object to be inspected.

    skip_root_module: `bool`
        A flag. If specified, will skip the root module in the slang.

    Returns
    -------
    #1: `str`
        The slang string of the inspected object.

        If the slang refers to the root of the package, return `"."`.

        If the slang cannot be analyzed, return an empty string.
    """
    if isinstance(obj, types.ModuleType):
        _module_name = obj.__name__
        if skip_root_module and isinstance(_module_name, str) and _module_name:
            _module_name = (
                _module_name.split(".", 1)[-1] if "." in _module_name else "."
            )
        return _module_name if _module_name else "."

    _module_name = getattr(obj, "__module__", None)
    if skip_root_module and isinstance(_module_name, str) and _module_name:
        _module_name = _module_name.split(".", 1)[-1] if "." in _module_name else "."
    _qual_name = getattr(obj, "__qualname__", None)
    if _module_name is not None and _qual_name is not None:
        return (
            _qual_name
            if _module_name == "."
            else "{0}.{1}".format(_module_name, _qual_name)
        )

    # Handle variables (low efficiency)
    module = inspect.getmodule(obj)
    if module is None:
        return ""
    module_name = module.__name__
    if skip_root_module and module_name:
        _module_name_segs = module_name.split(".", 1)
        module_name = _module_name_segs[-1] if len(_module_name_segs) > 1 else "."
    for name, value in vars(module).items():
        if value is obj:
            return "{0}.{1}".format(module_name, name)

    return ""


def is_user_defined_method(cls: type[Any], method: Any) -> bool:
    """Check whether a member is defined in a class.

    Arguments
    ---------
    cls: `type[Any]`
        The class to be inspected.

    method: `Any`
        A method to be checked. It will be marked as `True` is it is detected to
        be possibly defined in the given class.

    Returns
    -------
    #1: `bool`
        A flag. If `True`, the method is thought to be a member of `cls`.
    """
    _qname = getattr(method, "__qualname__", None)
    if isinstance(_qname, str) and (not _qname.startswith(cls.__name__)):
        return False
    # The following tests can be only performed on methods.
    if not (
        inspect.isfunction(method) or isinstance(method, (classmethod, staticmethod))
    ):
        return True
    _mod = sys.modules.get(cls.__module__, None)
    if not _mod:
        return True
    module_file = getattr(_mod, "__file__", None)
    code = getattr(method, "__code__", None)
    if module_file is None or code is None:
        return True
    return os.path.abspath(code.co_filename) == os.path.abspath(module_file)


def get_members_defined_in_class(
    cls: type[Any], exclude_private: bool = True
) -> Iterator[tuple[str, Any]]:
    """Get all members (attributes) defined in a class.

    Different from `inspect.getmembers`, this method will exclude the attributes
    defined in the base class.

    Arguments
    ---------
    cls: `type[Any]`
        The class to be inspected.

    exclude_private: `bool`
        A flag. If specified, will not return the attributes that starts with the "_"
        prefix.

    Yields
    ------
    #1: `str`
        The name of the member.

    #2: `Any`
        The attribute value of the member.
    """

    for name, value in inspect.getmembers_static(cls):
        if name not in cls.__dict__:
            continue
        if (
            exclude_private
            and name.startswith("_")
            and (not (name.startswith("__") and name.endswith("__")))
        ):
            continue
        if not is_user_defined_method(cls, value):
            continue
        yield (name, value)


def get_members_defined_in_enum(
    cls: type[Any], exclude_private: bool = True
) -> Iterator[tuple[str, Any]]:
    """Get all members (attributes) defined in an enum class.

    `inspect.getmembers` does not work on `enum.Enum`. This method is a fallback
    option when the methods and properties need to be detected from enum class.

    Arguments
    ---------
    cls: `type[Any]`
        The class to be inspected.

    exclude_private: `bool`
        A flag. If specified, will not return the attributes that starts with the "_"
        prefix.

    Yields
    ------
    #1: `str`
        The name of the member.

    #2: `Any`
        The attribute value of the member.
    """

    for name, value in cls.__dict__.items():
        if (
            exclude_private
            and name.startswith("_")
            and (not (name.startswith("__") and name.endswith("__")))
        ):
            continue
        if callable(value) and (not is_user_defined_method(cls, value)):
            continue
        yield (name, value)


def get_field_docstrings(
    model_cls: type[Any], include_dyn_assign: bool = False
) -> dict[str, str | None]:
    """Capture the docstrings of each assignment item in a class by its source code.

    Arguments
    ---------
    model_cls: `type[Any]`
        The class to be analyzed.

    include_dyn_assign: `bool`
        By default, this method will only detect the docstrings of such items:
        ``` python
        name: type = value
        ```
        If this flag is enabled, will also detect docstrings of such items:
        ``` python
        name = value
        ```

    Returns
    -------
    #1: `dict[str, str | None]`
        The docstrings of the fields. If the value of a key is `None`, it means that
        this field does not have the docstring.
    """

    def check_mro_pyd(_cls: type[Any]) -> bool:
        if _cls is BaseModel or (not issubclass(_cls, BaseModel)):
            return True
        return False

    def check_mro_dcls(_cls: type[Any]) -> bool:
        if not dataclasses.is_dataclass(_cls):
            return True
        return False

    def check_mro_enum(_cls: type[Any]) -> bool:
        if _cls is enum.Enum or (not issubclass(_cls, enum.Enum)):
            return True
        return False

    def check_mro_tdict(_cls: type[Any]) -> bool:
        if not is_typeddict(_cls):
            return True
        return False

    stop_by = None
    if isinstance(model_cls, type):
        if issubclass(model_cls, BaseModel):
            stop_by = check_mro_pyd
        elif dataclasses.is_dataclass(model_cls):
            stop_by = check_mro_dcls
        elif issubclass(model_cls, enum.Enum):
            stop_by = check_mro_enum
        elif is_typeddict(model_cls):
            stop_by = check_mro_tdict

    cls_list = get_mro(model_cls, stop_by=stop_by)

    def _get_single_docstring(_model_cls: type[Any]) -> dict[str, str | None]:
        """Get the docstring of a single class."""
        try:
            source = inspect.getsource(_model_cls)
        except (OSError, TypeError):
            return dict()
        try:
            tree = ast.parse(source)
        except IndentationError:
            tree = ast.parse(source.strip())

        class_def = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == _model_cls.__name__
        )

        def get_doc(class_def: ast.ClassDef, idx: int) -> str | None:
            """Attempt to get the docstring of a field defined in a class.

            Arguments
            ---------
            class_def: `ClassDef`
                The class definition providing the body.

            idx: `int`
                The index locating the field.
            """
            if len(class_def.body) < idx + 2:
                return None
            body = class_def.body[idx + 1]
            if not isinstance(body, ast.Expr):
                return None
            cst = body.value
            if not isinstance(cst, ast.Constant):
                return None
            doc = cst.value
            if not isinstance(doc, str):
                return None
            return doc

        docs: dict[str, str | None] = dict()
        for i, node in enumerate(class_def.body):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                field_name = node.target.id
                docs[field_name] = get_doc(class_def, i)
            elif (
                include_dyn_assign
                and isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                field_name = node.targets[0].id
                docs[field_name] = get_doc(class_def, i)

        return docs

    _res: dict[str, str | None] = dict()
    for cls in cls_list[::-1]:
        _res.update(_get_single_docstring(cls))
    return _res


def get_arg_default_name(val: Any) -> str:
    """Format the given value as a string that can be used as the default field of a
    function argument (`DocFunction`).

    Arguments
    ---------
    val: `Any`
        The value to be checked.

    Returns
    -------
    #1: `str | None`
        The value that can be filled as the default value of a function argument.

        If it is empty, the argument does not have the default configuration.
    """
    if val is inspect.Parameter.empty:
        return ""
    if val is PydanticUndefined:
        return ""
    if val is dataclasses.MISSING:
        return ""
    if isinstance(val, type):
        name = getattr(val, "__name__", None)
    elif isinstance(val, enum.Enum):
        name = "{0}.{1}".format(val.__class__.__name__, val.name)
    elif isinstance(val, str):
        name = '"{0}"'.format(val.replace('"', R"\""))
    else:
        name = repr(val)
    if name is None:
        name = repr(val)
    if "<" in name or ">" in name:
        name = name.replace("<", "").replace(">", "").split()[0]
    if name == '""':
        return name
    return black.format_str(name, mode=black.Mode(line_length=len(name) + 5)).strip()


def get_lambda_source(func: Any) -> str:
    """Get the source definition of a lambda function expression.

    Arguments
    ---------
    func: `Any`
        A function object that is potentially a lambda function.

    Returns
    -------
    #1: `str`
        The expression. Will return `None` if the given `func` is not a lambda
        function.
    """
    _code = getattr(func, "__code__", None)
    if not _code:
        return ""
    filename = str(_code.co_filename)
    lineno = _code.co_firstlineno
    if not isinstance(lineno, int):
        return ""
    if not os.path.isfile(filename):
        return ""

    with open(filename, "r") as f:
        source = f.read()

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Lambda) and getattr(node, "lineno", None) == lineno:
            src = astunparse.unparse(node).strip()
            if src.startswith("(") and src.endswith(")"):
                src = src[1:-1].strip()
            return src

    return ""


def get_func_signature(func_candidate: Any) -> inspect.Signature:
    """Attempt to get the signature of a potential function.

    Arguments
    ---------
    func_candidate: `Any`
        An object that is callable and able to provide a function signature.

    Returns
    -------
    #1: `Signature`:
        If the `func_candidate` is already a function, get its signature directly.

        Otherwise, get its equivalent callable signature (such as init method of a
        class).
    """
    if isinstance(func_candidate, (classmethod, staticmethod)) or inspect.ismethod(
        func_candidate
    ):
        return inspect.signature(func_candidate.__func__)
    if isinstance(func_candidate, type):
        return inspect.signature(func_candidate.__init__)
    return inspect.signature(func_candidate)


def get_field_default(val_default: Any, val_default_factory: Any) -> str:
    """Format the given value as a string that can be used as the default field of a
    field (`DocField`).

    Arguments
    ---------
    val_default: `Any`
        The candidate of the default value. It will be preferred if existing.

    val_default_factory: `Any`
        The candidate of the default factory. If the default value does not exist,
        will attempt to format the default value from it.

    Returns
    -------
    #1: `str | None`
        The value that can be filled as the default value of a field.

        If it is empty, the field does not have the default configuration.
    """
    res = get_arg_default_name(val_default)
    if res:
        return res
    if (
        val_default_factory is None
        or val_default_factory is PydanticUndefined
        or val_default_factory is dataclasses.MISSING
    ):
        return ""
    if not callable(val_default_factory):
        return ""
    name = getattr(val_default_factory, "__name__", None)
    if not name:
        return ""
    if name == "list":
        return "[]"
    if name == "<lambda>":
        return get_lambda_source(val_default_factory)
    params_required = tuple(
        (param.default is inspect.Parameter.empty)
        for param in get_func_signature(val_default_factory).parameters.values()
    )
    if params_required and any(params_required):
        return "{0}(...)".format(name)
    return "{0}()".format(name)


def is_multival_tuple(anno: Any) -> bool:
    """Check whether the given annotation is a multi-variable tuple such as

    ``` python
    tuple[int, str]
    ```

    Note that similar cases such as `tuple[int]` and `tuple[int, ...]` will be
    excluded.

    Arguments
    ---------
    anno: `Any`
        The annotation to be checked.

    Return
    ------
    #1: `bool`
        A flag. It is `True` when the given annotation is a multi-variable tuple.
    """
    if (not isinstance(anno, types.GenericAlias)) or (
        getattr(anno, "__origin__", None) is not tuple
    ):
        return False

    args = getattr(anno, "__args__", None)

    if (
        (not isinstance(args, Sequence))
        or (len(args) == 1 and args[0] is not Ellipsis)
        or (len(args) == 2 and args[1] is Ellipsis)
    ):
        return False

    return True


def is_member_abstract(attr: Any) -> bool:
    """Check whether a value is an abstract member of a class.

    Arguments
    ---------
    attr: `Any`
        The attribute of a class. It can be a value, method, property, or operator.
        Note that the attribute needs to be provided by the method
        `inspect.getmembers_static(...)`.

    Returns
    -------
    #1: `bool`
        If the attribute has been decorated by `@abstractmethod`, returns `True`. If
        the value is not a method (such as a variable), will return `False`.
    """
    if isinstance(attr, (classmethod, staticmethod)) or inspect.ismethod(attr):
        return bool(getattr(attr.__func__, "__isabstractmethod__", False))
    if isinstance(attr, functools.cached_property):
        return bool(getattr(attr.func, "__isabstractmethod__", False))
    if isinstance(attr, property):
        return any(
            bool(getattr(fdes, "__isabstractmethod__", False))
            for fdes in (attr.fget, attr.fset, attr.fdel)
            if fdes is not None
        )
    if inspect.isfunction(attr):
        return bool(getattr(attr, "__isabstractmethod__", False))
    return False


def is_func_yield(func: Any) -> bool:
    """Check whether the given object is a function returning an iterator.

    Will check the real-time implementation first. If not detected, will check the
    annotation.

    Arguments
    ---------
    func: `Any`
        The function candidate object to be checked.

    Returns
    -------
    #1: `bool`
        A flag that will be `True` if the function returns the generator/iterator.
    """
    if inspect.isgeneratorfunction(func) or inspect.isasyncgenfunction(func):
        return True
    annotations = annotationlib.get_annotations(func, format=annotationlib.Format.VALUE)
    _, _, is_yield = unpack_annotation(annotations.get("return", "Unknown"))
    return is_yield


def unwrap_annotated_annotation(anno: Any) -> Any:
    """Given an annotation, remove the `Annotated[...]` wrapper recursively if it
    appears.

    Arguments
    ---------
    anno: `Any`
        The annotation to be processed.

    Returns
    -------
    #1: `Any`
        The annotation where the `Annotated[...]` is unwrapped.
    """
    _origin = get_origin(anno)
    if _origin is None:
        return anno
    if _origin is Annotated:
        return unwrap_annotated_annotation(get_args(anno)[0])
    return _origin[*[unwrap_annotated_annotation(arg) for arg in get_args(anno)]]


def unpack_annotation(anno: Any) -> tuple[tuple[Any, ...], bool, bool]:
    """Unpack the annotation wrapper.

    This method is mainly used for extracting the arguments in the wrapped returned
    annotation such as `Generator[]`, `Iterator[]`, and `tuple[]`.

    Arguments
    ---------
    anno: `Any`
        The annotation to be analyzed.

    Returns
    -------
    #1: `tuple[Any, ...]`
        A list of extracted arguments in the annotation. If the given annotation only
        has one argument, will be `(anno,)`.

    #2: `bool`
        A flag showing whether the annotation should be interpreted as async output.

    #3: `bool`
        A flag showing whether the annotation should be interpreted as yielding values.
    """
    _origin = get_origin(anno)
    is_async: bool = False
    is_yield: bool = False

    if _origin in (AsyncGenerator, AsyncIterator, AsyncIterable):
        is_async = True

    if _origin in (Generator, Iterator, AsyncGenerator, AsyncIterator):
        anno = get_args(anno)
        anno = anno[0] if (isinstance(anno, Sequence) and len(anno) > 0) else anno
        is_yield = True

    if is_multival_tuple(anno):
        anno = get_args(anno)
        anno = tuple(anno) if anno else tuple()
    else:
        anno = (anno,)

    return anno, is_async, is_yield


def strip_annotation_name(anno: Any) -> str:
    """Convert an annotation to string, and strip its name by removing the module
    prefix.

    Arguments
    ---------
    anno: `Any`
        An annotation object or string. The string should be converted from the
        annotation object.

    Returns
    -------
    #1: `str`
        The revised string version of the giving annotation.
    """

    if not isinstance(anno, str):
        anno = annotationlib.annotations_to_string({"arg": anno})["arg"]

    def repl(match: re.Match[str]) -> str:
        name = str(match.group(1))
        if "." in name:
            last = name.split(".")[-1]
            return last
        return name

    _anno = ANNO_NAME_PATTERN.sub(repl, anno)
    return black.format_str(_anno, mode=black.Mode(line_length=len(_anno) + 5)).strip()


def get_short_descr(descr: str) -> str:
    """Get the short description from the long description.

    Extract the first sentence from the given text.

    Arguments
    ---------
    descr: `str`
        The long description that may contain multiple sentences.

    Returns
    -------
    #1: `str`
        The first sentence extracted from the given text.
    """
    _descr = descr.strip().splitlines()
    if not _descr:
        return ""
    short_descr = _descr[0].split(". ", 1)[0].strip().strip(".").strip()
    return short_descr + "."


def get_slug(slang: str) -> str:
    """Get the URL slug from the slang prototype.

    Arguments
    ---------
    slang: `str`
        The slang in the endpoint format, for example: "package.module.class".

    Returns
    -------
    #1: `str`
        The absolute URL of a page.
    """
    slug = "/".join(slang.strip(".").split("."))
    return "/apis/{0}".format(slug)


def relative_url_path(path_from: str, path_to: str) -> str:
    """Solve the relative path.

    Arguments
    ---------
    path_from: `str`
        An anchor path. The final path is solved starting from this path.

    path_to: `str`
        The target path.

    Returns
    -------
    #1: `str`
        The relative path from `path_from` to `to_ppath_toath`, always using forward
        slashes for URL compatibility.
    """
    path_from = path_from.replace("\\", "/")
    path_to = path_to.replace("\\", "/")
    base = path_from.rstrip("/")
    base = base if path_to.startswith(base) else os.path.dirname(path_from)
    rel = os.path.relpath(path_to, start=base).replace("\\", "/")
    if (
        rel.startswith("./")
        or rel.startswith("../")
        or rel.startswith("/")
        or re.match(r"^[A-Za-z]:/", rel)
    ):
        return rel

    return "./" + rel
