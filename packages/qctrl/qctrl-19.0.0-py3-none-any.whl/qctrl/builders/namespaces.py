# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import inspect
import logging
from enum import Enum
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

import inflection

from qctrl.dynamic import (
    BoulderModule,
    dynamic_class,
)

LOGGER = logging.getLogger(__name__)


FUNCTION_NAMESPACE_DOCSTRING = """
    Namespace for functions. Functions are computations using objects
    created from the `types` namespace.

    Boulder Opal also provides toolkits to simplify the workflow for common computation tasks.
    Some toolkits host functions that you can access from their namespaces of
    the :py:obj:`~qctrl.Qctrl` object.
    See the `reference <https://docs.q-ctrl.com/boulder-opal/references/qctrl/Toolkits.html>`_
    for details.
"""


TYPE_NAMESPACE_DOCSTRING = """
    Namespace for types. Objects created from these types are used
    when performing computations defined in the `functions` namespace.
"""


class BaseNamespace(SimpleNamespace):
    """Base namespace class for Qctrl components."""

    @classmethod
    def extend(cls, attrs: Dict[str, Any]) -> None:
        """Extends the namespace class by adding attributes.

        Parameters
        ----------
        attrs : Dict[str, Any]
            Dict of attributes to add to the namespace.

        Raises
        ------
        AttributeError
            Existing attribute found.
        """
        for attr, value in attrs.items():
            if hasattr(cls, attr):
                raise AttributeError(f"existing attr ({attr}) on namespace: {cls}")

            LOGGER.debug("adding attr %s to namespace: %s", attr, cls)
            setattr(cls, attr, value)

    @classmethod
    def extend_functions(cls, *funcs: Callable) -> None:
        """Extends the namespace class by adding functions as attributes. The
        function will be added as a staticmethod.

        Parameters
        ----------
        *funcs : Callable
            Functions to be added to the namespace.
        """
        for func in funcs:
            cls.extend({func.__name__: staticmethod(func)})


class TypeNamespaceMixin:
    """
    Mixin to handle namespaced types.
    """

    @classmethod
    def add_registry(cls, type_registry: "TypeRegistry"):
        """
        Adds the registered types as attributes of the namespace.
        """
        for name, type_cls in type_registry.get_type_map().items():
            attr, namespace = type_registry.parse_name(name)
            cls._namespace_extend(namespace or [], attr, type_cls)

        cls.registry = type_registry

    @classmethod
    def _namespace_extend(cls, namespace: List[str], attr: str, obj: Any):
        """
        Recursively create nested namespaces, then use extend
        to set the attribute.
        """
        current = cls
        prefix = ""  # name prefix for nested namespaces

        for item in namespace:
            nested_attr = inflection.underscore(item)
            prefix += inflection.camelize(nested_attr)

            # nested namespace already exists
            if hasattr(current, nested_attr):
                current = getattr(current, nested_attr)

            # created nested namespace
            else:
                nested_namespace_cls = _create_namespace_cls(prefix + "Type")
                nested_namespace = nested_namespace_cls()
                current.extend({nested_attr: nested_namespace})

                # update current for any further nesting
                current = nested_namespace_cls

        current.extend({attr: obj})


@dynamic_class("namespaces")
def _create_namespace_cls(
    prefix: str,
    docstring: Optional[str] = None,
    base: SimpleNamespace = BaseNamespace,
    mixins: Optional[List[type]] = None,
    module: BoulderModule = BoulderModule.QCTRL,
) -> SimpleNamespace:
    """Creates a new namespace class and returns an instance of it.

    Parameters
    ----------
    prefix : str
        A prefix for the all core namespace. (i.e core__ )
    docstring : str, optional
        Namespace docstring. Defaults to `None`.
    base : SimpleNamespace, optional
        Namespace base. Defaults to `BaseNamespace`.
    mixins : List[type], optional
        Nested mixins. Defaults to `None`.
    module : BoulderModule, optional
        The module to which the namespace belongs. Defaults to `BoulderModule.QCTRL`.

    Returns
    -------
    SimpleNamespace
        Formatted namespace.
    """
    name = f"{inflection.camelize(prefix)}Namespace"
    parents = [base]

    if mixins:
        parents += mixins

    attrs = {"__module__": module.value}

    if docstring:
        attrs.update({"__doc__": docstring})

    new_cls = type(name, tuple(parents), attrs)
    return new_cls


def create_function_namespace():
    """Creates the function namespace."""
    cls = _create_namespace_cls("Function", FUNCTION_NAMESPACE_DOCSTRING)
    return cls()


def create_type_namespace():
    """Creates the type namespace."""
    cls = _create_namespace_cls(
        "Type", TYPE_NAMESPACE_DOCSTRING, mixins=[TypeNamespaceMixin]
    )
    return cls()


class ToolkitCategory(Enum):
    """
    Defines the categories for toolkits.
    """

    FUNCTIONS = 1
    NODES = 2


def build_and_bind_toolkit(
    obj: Union["Qctrl", "Graph"], category: ToolkitCategory, toolkit: "qctrltoolkit"
) -> None:
    """
    Builds namespace for toolkit, add corresponding methods to
    the namespace, and bind the namespace to the object.

    Note that a given method could belong to multiple namespaces.

    Parameters
    ----------
    obj : Union["Qctrl", "Graph"]
        The object (either a qctrl or graph object) to which the toolkit is bound.
    category : ToolkitCategory
        The type of toolkit.
    toolkit : Any
        The toolkit module.
    """

    # ensure that attributes we need are correctly exposed
    _check_attrs(toolkit, ["TOOLKIT_ATTR", category.name, "forge_toolkit"])

    # create a set of labels for namespaces from toolkit
    namespace_labels = set()
    for method in getattr(toolkit, category.name):
        namespace_labels.update(
            (attr for attr in getattr(method, toolkit.TOOLKIT_ATTR))
        )

    # create namespace and bind it to the object
    for label in namespace_labels:
        _name = label.get_name()
        _namespace_cls = _create_namespace_cls(
            prefix=_name,
            docstring=label.get_doc(),
            module=BoulderModule.get_module(obj.__class__.__name__.lower()),
        )
        setattr(_namespace_cls, toolkit.TOOLKIT_ATTR, _name)

        _namespace = _namespace_cls()
        assert not hasattr(obj, _name), f"Namespace {_name} is already defined!"
        LOGGER.debug("adding attr to namespace %s to object %s", _namespace, obj)
        setattr(obj, _name, _namespace)

    # binds methods to namespaces
    for method in getattr(toolkit, category.name):
        forged = toolkit.forge_toolkit(method, obj)
        for namespace in getattr(method, toolkit.TOOLKIT_ATTR):
            _ns = getattr(obj, namespace.get_name())
            if inspect.isfunction(forged):
                _ns.extend_functions(forged)
            else:
                assert not hasattr(
                    _ns, method.__name__
                ), f"existing attr ({method}) on namespace: {_ns}"
                LOGGER.debug("adding attr %s to namespace: %s", method, _ns)
                setattr(_ns, method.__name__, forged)


def _check_attrs(package, attr_names: List[str]):
    for name in attr_names:
        assert hasattr(package, name), f"No module/attribute {name} found in {package}."


__all__ = [
    "BaseNamespace",
    "BoulderModule",
    "ToolkitCategory",
    "create_function_namespace",
    "create_type_namespace",
    "build_and_bind_toolkit",
]
