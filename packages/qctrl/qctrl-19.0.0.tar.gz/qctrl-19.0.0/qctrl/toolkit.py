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
Functionality related to the Q-CTRL Python Toolkit.

The toolkit objects are re-imported here to allow all access to the objects to happen directly from
the `qctrl` package.
"""

# pylint: disable=unused-import

from qctrltoolkit import (
    FUNCTIONS,
    NODES,
    TOOLKIT_ATTR,
    TOOLKIT_DOC_CONFIG,
    TOOLKIT_MAIN_DOC,
    Namespace,
    forge_toolkit,
)

__doc__ = TOOLKIT_MAIN_DOC
