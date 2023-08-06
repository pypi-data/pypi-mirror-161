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
"""
Functionality related to the Q-CTRL graph structure.

The commons objects are re-imported here to allow all access to the objects to happen directly from
the `qctrl` package.
"""

import sys

# We import Graph to expose it directly from this module.
# pylint: disable=unused-import
from qctrlcommons.graph import Graph as _BaseGraph
from qctrlcommons.node.registry import TYPE_REGISTRY as _TYPE_REGISTRY

from qctrl import toolkit as _toolkit
from qctrl.builders.namespaces import ToolkitCategory as _ToolkitCategory
from qctrl.builders.namespaces import build_and_bind_toolkit as _build_and_bind_toolkit
from qctrl.utils import PackageRegistry as _PackageRegistry

_module = sys.modules[__name__]
for _type_cls in _TYPE_REGISTRY:
    setattr(_module, _type_cls.__name__, _type_cls)

# pylint: disable=too-few-public-methods
class Graph(_BaseGraph):

    """
    Utility class for representing and building a Q-CTRL data flow graph.
    """

    def __init__(self):
        super().__init__()
        _build_and_bind_toolkit(self, _ToolkitCategory.NODES, _toolkit)
