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
Utilities for the pulse library nodes.
"""

from typing import Union

import numpy as np
from qctrlcommons.graph import Graph
from qctrlcommons.node.node_data import Tensor
from qctrlcommons.preconditions import check_argument


def validate_optimizable_parameter(
    graph: Graph, parameter: Union[float, Tensor], name: str
) -> Tensor:
    """
    Convert parameter into a Tensor, checks that it contains a single element
    and returns a Tensor containing that element.
    """

    parameter = graph.tensor(parameter)
    check_argument(
        np.prod(parameter.shape) == 1,
        f"If passed as a Tensor, the {name} must either "
        "be a scalar or contain a single element.",
        {name: parameter},
        extras={f"{name}.shape": parameter.shape},
    )

    return graph.reshape(parameter, [1])[0]
