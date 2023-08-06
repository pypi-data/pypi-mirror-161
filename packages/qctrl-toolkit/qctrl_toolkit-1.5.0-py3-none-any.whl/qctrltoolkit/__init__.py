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

"""qctrltoolkit - a toolkit library for the Q-CTRL Python package."""

__version__ = "1.5.0"
__author__ = "Q-CTRL <support@q-ctrl.com>"

from qctrltoolkit.namespace import (
    TOOLKIT_MAIN_DOC,
    Namespace,
)
from qctrltoolkit.registry import (
    FUNCTIONS,
    NODES,
    TOOLKIT_DOC_CONFIG,
)
from qctrltoolkit.toolkit_utils import (
    TOOLKIT_ATTR,
    forge_toolkit,
)

__all__ = [
    "FUNCTIONS",
    "NODES",
    "TOOLKIT_ATTR",
    "TOOLKIT_DOC_CONFIG",
    "TOOLKIT_MAIN_DOC",
    "Namespace",
    "forge_toolkit",
]
