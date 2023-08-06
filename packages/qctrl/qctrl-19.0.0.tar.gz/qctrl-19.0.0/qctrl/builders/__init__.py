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
import logging

from graphql import GraphQLField
from qctrlcommons.node.registry import (
    NODE_REGISTRY,
    TYPE_REGISTRY,
)

from qctrl import toolkit
from qctrl.utils import PackageRegistry

from .async_result import AsyncResult
from .client_builder import (
    create_client_auth,
    create_gql_client,
)
from .custom_environment import create_environment
from .doc import (
    FunctionArgument,
    FunctionDocstring,
)
from .functions import (
    build_function,
    build_signature,
)
from .namespaces import (
    BaseNamespace,
    ToolkitCategory,
    build_and_bind_toolkit,
    create_function_namespace,
    create_type_namespace,
)
from .result_mixin import ResultMixin
from .type_registry import TypeRegistry

LOGGER = logging.getLogger(__name__)


def _is_valid_function_mutation(name: str) -> bool:
    """Checks if the mutation field corresponds to a valid function which
    should be available to the user. Mutations that should be exposed have a
    single argument named `input`.

    Parameters
    ----------
    name: GraphQLField
        The mutation field to check.

    Returns
    -------
    bool
        True if field is a valid mutation to be exposed to a user.
    """
    return name.startswith("core__")


def build_and_bind_namespaces(qctrl: "Qctrl") -> None:
    """Builds features, organizes them into namespaces and binds the namespace to the
    qctrl object.

    Parameters
    ----------
    qctrl : Qctrl
        The Qctrl object.
    """
    function_namespace = create_function_namespace()
    type_namespace = create_type_namespace()

    # build namespace for functions and types for GQL
    mutation_type = qctrl.gql_api.schema.mutation_type

    for name, field in mutation_type.fields.items():
        if _is_valid_function_mutation(name):
            func = build_function(qctrl, name, field)
            function_namespace.extend_functions(func)

    type_namespace.add_registry(qctrl.gql_env.type_registry)

    setattr(qctrl, "functions", function_namespace)
    setattr(qctrl, "types", type_namespace)
    build_and_bind_toolkit(qctrl, ToolkitCategory.FUNCTIONS, toolkit)


__all__ = ["build_and_bind_namespaces"]
