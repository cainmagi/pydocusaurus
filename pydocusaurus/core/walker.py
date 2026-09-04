# -*- coding: UTF-8 -*-
"""
Walker
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
The inspector and analyzer that walks through and processes the nested package and
module members. Both the run-time object and the corresponding code will be analyzed.
"""

import abc
import ast
import inspect
import importlib
import pkgutil
import sys
import logging
from types import ModuleType

from typing import Any
from typing_extensions import Literal, is_typeddict, is_protocol, final
from collections.abc import Iterator

from dataclasses import is_dataclass
from enum import Enum
from pydantic import BaseModel

from .typealiases import parse_type_aliases_doc
from . import functions as _funcs
from . import classes as _classes
from . import datacls as _datacls
from . import enums as _enums
from . import typeddicts as _tdicts
from . import protocols as _protocols
from . import typealiases as _taliases
from . import modules as _modules

__all__ = (
    "analyze_module_ast",
    "get_direct_submodules",
    "is_direct_nonmodule",
    "is_direct_module",
    "is_direct_member",
    "is_main_module",
    "fast_import",
    "ParserAbstract",
    "PackageWalker",
)
log = logging.getLogger("pydocusaurus")


def analyze_module_ast(module: ModuleType) -> dict[str, tuple[int, bool]]:
    """Analyze the coding structure (AST) of a module, and return the entity
    information detected in the code.

    Arguments
    ---------
    module: `ModuleType`
        The module to be analyzed.

    Returns
    -------
    #1: `dict[str, tuple[int, bool]]`
        The mapping of `name -> (lineno, is_alias)`.

        The `name` is the entity name detected in the module.

        An entity can be a class, function, variable, and imported aliases such as
            - class Foo
            - def bar
            - baz = ...
            - import x as y
            - from .sub import name
            - from external import name

        `lineno` is the line number where the entity is specified in the code.

        `is_alias` is a flag showing whether the entity is an alias. When it is `True`,
        it means that the name is imported/re-exported, but not defined directly in
        this module.
    """
    try:
        source = inspect.getsource(module)
    except OSError:
        return {}

    tree = ast.parse(source)
    result: dict[str, tuple[int, bool]] = {}

    for node in tree.body:
        match node:
            case ast.ClassDef() | ast.FunctionDef() | ast.AsyncFunctionDef():
                result[node.name] = (node.lineno, False)
            case ast.Assign():
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        result[target.id] = (node.lineno, False)
            case ast.Import():
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    result[name] = (node.lineno, True)
            case ast.ImportFrom():
                level = node.level
                module_name = node.module  # may be None
                for alias in node.names:
                    name = alias.asname or alias.name
                    lineno = node.lineno
                    result[name] = (lineno, (level > 0) or (module_name is not None))
    return result


def get_direct_submodules(
    module: ModuleType, filtered_by_all: bool = True
) -> list[ModuleType]:
    """Get the submodules/subpackages directly defined in a package.

    Arguments
    ---------
    module: `ModuleType`
        The package to be analyzed. The submodules/subpackages are detected in it.

    filtered_by_all: `bool`
        A flag. If specified, will prefer the `__all__` value defined in the module
        when searching members. In this case, any value not in the `__all__` list
        will be ignored.

    Returns
    -------
    #1: `list[ModuleType]`
        A list of module objects that are direct submodules/subpackages of the given
        module. If the module is imported from somewhere else, it will not be included.
    """
    if not hasattr(module, "__path__"):
        # Not a package → no subpackages/submodules
        return []

    prefix = module.__name__ + "."
    results: list[ModuleType] = []
    _all_raw = getattr(module, "__all__", None) if filtered_by_all else None
    _all: set[str] | None = (
        set(str(val) for val in _all_raw) if _all_raw is not None else None
    )

    for _, name, _ in pkgutil.iter_modules(module.__path__, prefix):
        try:
            submod = importlib.import_module(name)
            subnames = name.split(".")
            if (_all is None) or (subnames and (subnames[-1] in _all)):
                results.append(submod)
        except Exception as e:
            raise e

    return results


def is_direct_nonmodule(obj: Any, module: ModuleType) -> bool:
    """Check whether a non-module object is directly defined in a module/package.

    Arguments
    ---------
    obj: `Any`
        An object to be checked.

    module: `ModuleType`
        The module/package where `obj` is potentially defined. The detection is
        related to this module.

    Returns
    -------
    #1: `bool`
        A flag. If it is `True`, it means the `obj` is directly defined in `module`.
    """
    return getattr(obj, "__module__", None) == module.__name__


def is_direct_module(value: ModuleType, module: ModuleType) -> bool:
    """Check whether a module/package is a direct member of another module/package.

    Arguments
    ---------
    value: `ModuleType`
        The module to be checked.

    module: `ModuleType`
        The module/package where `value` is potentially imported. The detection
        is related to this module.

    Returns
    -------
    #1: `bool`
        A flag. It is `True` only if `value` is a direct member imported via
        `from . import name`. That means exactly one level deeper.
    """
    parent = module.__name__
    child = value.__name__

    if not child.startswith(parent + "."):
        return False

    return child.count(".") == parent.count(".") + 1


def is_direct_member(value: Any, module: ModuleType) -> bool:
    """Check whether a value is a direct member of another module/package.

    Arguments
    ---------
    value: `Any`
        The value to be checked. It can be a module/package or just a plain value.

    module: `ModuleType`
        The module/package where `value` potentially exists. The detection
        is related to this module.

    Returns
    -------
    #1: `bool`
        A flag. It is `True` only if `value` is a direct member defined or imported
        in `module`.
    """
    if isinstance(value, ModuleType):
        return is_direct_module(value, module)
    return is_direct_nonmodule(value, module)


def is_main_module(module: ModuleType) -> bool:
    """Check whether a module is a `__main__` module.

    A `__main__` module is the entrypoint of a package.

    Arguments
    ---------
    module: `ModuleType`
        The module to be checked.

    Returns
    -------
    #1: `bool`
        A flag that is `True` if `module` is the `__main__` module.
    """
    mod_file = getattr(module, "__file__", None)
    if not isinstance(mod_file, str):
        return False
    mod_name = module.__name__
    return mod_file.endswith("__main__.py") and mod_name.endswith(".__main__")


def fast_import(module: ModuleType | str) -> ModuleType:
    """Import a package by its name.

    Arguments
    ---------
    module: `ModuleType | str`
        The package to be imported. It can be an already imported package.

    Returns
    -------
    #1: `ModuleType`
        The imported package. It is the input value if the input value is already
        imported.
    """
    if isinstance(module, ModuleType):
        return module
    if module in sys.modules:
        return sys.modules[module]
    return importlib.import_module(module)


class ParserAbstract(abc.ABC):
    """The abstract class of a module parser.

    The parser is called when a member is detected in the module structure.
    """

    @abc.abstractmethod
    def parse_module(self, obj: _modules.DocModule) -> None:
        """Parse a member object when it is a module.

        Arguments
        ---------
        obj: `DocModule`
            The module information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_class(self, obj: _classes.DocClass) -> None:
        """Parse a member object when it is a class.

        Arguments
        ---------
        obj: `DocClass`
            The class information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_dataclass(self, obj: _datacls.DocDataClass) -> None:
        """Parse a member object when it is a data class.

        Arguments
        ---------
        obj: `DocDataClass`
            The data class information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_enum(self, obj: _enums.DocEnum) -> None:
        """Parse a member object when it is an enum class.

        Arguments
        ---------
        obj: `DocEnum`
            The enum class information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_typeddict(self, obj: _tdicts.DocTypedDict) -> None:
        """Parse a member object when it is a typed dictionary class.

        Arguments
        ---------
        obj: `DocTypedDict`
            The typed dictionary information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_protocol(self, obj: _protocols.DocProtocol) -> None:
        """Parse a member object when it is a protocol class.

        Arguments
        ---------
        obj: `DocProtocol`
            The protocol information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_typealias(self, obj: _taliases.DocTypeAlias) -> None:
        """Parse a member object when it is a type alias.

        Arguments
        ---------
        obj: `DocTypeAlias`
            The alias information to be parsed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_function(self, obj: _funcs.DocFunction) -> None:
        """Parse a member object when it is a function.

        Arguments
        ---------
        obj: `DocFunction`
            The function information to be parsed.
        """
        raise NotImplementedError

    @final
    def parse(self, obj: Any) -> None:
        """Parse a member.

        Arguments
        ---------
        obj: `Any`
            The member touched during the module walk. It will be parsed according
            to the member data type. For example, a function will be parsed by
            `parse_function(obj)`.
        """
        if not isinstance(
            obj,
            (
                _modules.DocModule,
                _classes.DocClass,
                _datacls.DocDataClass,
                _enums.DocEnum,
                _tdicts.DocTypedDict,
                _protocols.DocProtocol,
                _taliases.DocTypeAlias,
                _funcs.DocFunction,
            ),
        ):
            return
        match (obj.type):
            case "module":
                self.parse_module(obj)
            case "class":
                self.parse_class(obj)
            case "dataclass":
                self.parse_dataclass(obj)
            case "enum":
                self.parse_enum(obj)
            case "typeddict":
                self.parse_typeddict(obj)
            case "protocol":
                self.parse_protocol(obj)
            case "alias":
                self.parse_typealias(obj)
            case "function":
                self.parse_function(obj)


class PackageWalker:
    """The package iterative walker.

    Specifying a package, this walker will go through the package structure, touch
    each member and nested module, and analyze the docstring as structured texts.

    By providing a customized parser, users can determine how to process the extracted
    information.
    """

    @staticmethod
    def get_member_type(
        member: Any,
    ) -> Literal[
        "module",
        "class",
        "dataclass",
        "enum",
        "typeddict",
        "protocol",
        "function",
        "others",
    ]:
        """Detect the type (class) of a member.

        Arguments
        ---------
        member: `Any`
            The member to be detected.

        Returns
        -------
        #1: `"module" | "class" | "dataclass" | "enum" | "typeddict" | ... | "others"`
            The detected type code of the object. This value can be "others" when
            the member type is unknown.
        """
        if isinstance(member, ModuleType):
            return "module"
        elif inspect.isfunction(member):
            return "function"
        elif isinstance(member, type):
            if issubclass(member, BaseModel) or is_dataclass(member):
                return "dataclass"
            elif issubclass(member, Enum):
                return "enum"
            elif is_typeddict(member):
                return "typeddict"
            elif is_protocol(member):
                return "protocol"
            else:
                return "class"
        return "others"

    @classmethod
    def parse_module_member(
        cls,
        value: Any,
        value_type: (
            Literal[
                "module",
                "class",
                "dataclass",
                "enum",
                "typeddict",
                "protocol",
                "function",
                "others",
            ]
            | None
        ),
    ) -> (
        _modules.DocModule
        | _classes.DocClass
        | _datacls.DocDataClass
        | _enums.DocEnum
        | _tdicts.DocTypedDict
        | _protocols.DocProtocol
        | _funcs.DocFunction
        | None
    ):
        """Parse the module member as structured texts.

        Arguments
        ---------
        value: `Any`
            The member value to be parsed.

        value_type: `"module" | "class" | "dataclass" | "enum" | ... | "others"`
            The type code of the value. This type code is provided by
            `get_member_type(...)` but does not include `"typealias"`. The type aliases
            are not parsed by this method.

        Returns
        -------
        #1: `DocModule | DocClass | DocDataClass | DocEnum | ... | None`
            The structred information parsed from `value`. When the value type is
            unknown, will return `None`.
        """
        match value_type:
            case "module":
                return _modules.parse_module_doc(value)
            case "class":
                return _classes.parse_class_docs(value)
            case "dataclass":
                return _datacls.parse_dataclass_docs(value)
            case "enum":
                return _enums.parse_enum_docs(value)
            case "typeddict":
                return _tdicts.parse_typeddict_doc(value)
            case "protocol":
                return _protocols.parse_protocol_docs(value)
            case "function":
                return _funcs.parse_func_docs(value)
            case _:
                return None

    @classmethod
    def iter_module_members(cls, module: ModuleType) -> Iterator[
        tuple[
            _modules.DocModule
            | _classes.DocClass
            | _datacls.DocDataClass
            | _enums.DocEnum
            | _tdicts.DocTypedDict
            | _taliases.DocTypeAlias
            | _protocols.DocProtocol
            | _funcs.DocFunction,
            bool,
        ]
    ]:
        """Iterate direct members of a module/package.

        Note that this method will not deeply iterate the nested members.

        Arguments
        ---------
        module: `ModuleType`
            The module to be iterated.

        Yields
        -------
        #1: `DocModule | DocClass | DocDataClass | DocEnum | ...`
            The extracted structured member information.

        #2: `bool`
            A flag specifying whether the current member is imported/exported alias.
        """
        ast_info = analyze_module_ast(module)

        if hasattr(module, "__all__"):
            names = module.__all__
        else:
            names = [
                name
                for name, value in module.__dict__.items()
                if not name.startswith("_") and is_direct_member(value, module)
            ]

        # Get the potential candidates of type aliases.
        ta_candidates = parse_type_aliases_doc(module)
        ta_names: dict[str, int] = {
            ta.name: idx for idx, ta in enumerate(ta_candidates)
        }

        _missing = object()

        for name in names:
            if name.startswith("_"):
                continue
            value = getattr(module, name, _missing)
            if value is _missing:
                continue

            direct = is_direct_member(value, module)
            alias = not direct
            lineno = ast_info.get(name, (None, alias))[0]  # AST line number
            v_type = "typealias" if name in ta_names else cls.get_member_type(value)
            data = (
                ta_candidates[ta_names[name]]
                if v_type == "typealias"
                else cls.parse_module_member(value, v_type)
            )
            if data is None:
                continue

            if (
                (not isinstance(data, _modules.DocModule))
                and direct
                and (data.lineno == 0 if lineno is None else True)
            ):
                data.lineno = lineno if lineno is not None else 0

            yield data, alias

    def walk_package(self, root_pkg: str | ModuleType, handler: ParserAbstract) -> None:
        """Walk through a package.

        This method will start from the root of a package, iterate nested members, and
        call the parser for each touched member.

        Users can customizing the processing by providing the implementation of
        `handler` (the information parser).

        Arguments
        ---------
        root_pkg: `str | ModuleType`
            The name or the module object of a package.

        handler: `ParserAbstract`
            The parser that will be called on each nested member of the package.
        """
        root_module = fast_import(root_pkg)

        modules_to_visit = [root_module]

        if hasattr(root_module, "__path__"):
            for _, name, _ in pkgutil.walk_packages(
                root_module.__path__, root_module.__name__ + "."
            ):
                try:
                    module = importlib.import_module(name)
                except Exception as exc:
                    log.warning("Failed to import {0}: {1}".format(name, exc))
                else:
                    if is_main_module(module):
                        continue
                    modules_to_visit.append(module)

        _module_cache: dict[str, _modules.DocModule] = dict()

        for module in modules_to_visit:
            _module = _module_cache.get(module.__name__, None)
            if _module is None:
                _module = _modules.parse_module_doc(module)
                _module_cache[module.__name__] = _module
            for member, is_alias in self.iter_module_members(module):
                if member.type != "module":
                    handler.parse(member)
                _module.add_member(member, is_alias)
            handler.parse_module(_module)
