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
Registry for toolkits.
"""
import inspect
from dataclasses import dataclass
from typing import List

import qctrltoolkit.pulses.functions
import qctrltoolkit.pulses.pwc_nodes
import qctrltoolkit.pulses.stf_nodes
import qctrltoolkit.superconducting.functions
import qctrltoolkit.superconducting.nodes
import qctrltoolkit.utils.functions
import qctrltoolkit.utils.nodes
from qctrltoolkit.namespace import Namespace
from qctrltoolkit.toolkit_utils import TOOLKIT_ATTR


def _register(modules):
    """
    Collect exposed toolkits from modules.
    """
    registered = []
    for module in modules:
        for _, member in inspect.getmembers(module):
            if hasattr(member, TOOLKIT_ATTR):
                registered.append(member)
    return registered


NODES = _register(
    [
        qctrltoolkit.superconducting.nodes,
        qctrltoolkit.utils.nodes,
        qctrltoolkit.pulses.pwc_nodes,
        qctrltoolkit.pulses.stf_nodes,
    ]
)
FUNCTIONS = _register(
    [
        qctrltoolkit.superconducting.functions,
        qctrltoolkit.utils.functions,
        qctrltoolkit.pulses.functions,
    ]
)


def _get_empty_namespaces(exposed_items):
    """
    Collect a list with the names of the namespaces that are not in
    any of the exposed_items' TOOLKIT_ATTRs.
    """
    all_namespaces = set(Namespace)
    exposed_namespaces = set()
    for item in exposed_items:
        exposed_namespaces.update(set(getattr(item, TOOLKIT_ATTR)))

    left_namespaces = all_namespaces.difference(exposed_namespaces)
    return [item.get_name() for item in left_namespaces]


@dataclass
class _DocConfig:
    """
    Class to store information for building docs for the toolkits.

    Parameters
    ----------
    namespaces_without_functions: list[str]
        A list of names for namespaces that don't have functions.
    namespaces_without_nodes : list[str]
        A list of names for namespaces that don't have nodes.
    excluded_class_methods : list[str]
        A list of names for class methods that shouldn't be documented.
    """

    namespaces_without_functions: List[str]
    namespaces_without_nodes: List[str]
    excluded_class_methods: List[str]


TOOLKIT_DOC_CONFIG = _DocConfig(
    namespaces_without_functions=_get_empty_namespaces(FUNCTIONS),
    namespaces_without_nodes=_get_empty_namespaces(NODES),
    excluded_class_methods=["get_pwc"],
)
