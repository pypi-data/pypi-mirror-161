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
PWC pulse library nodes.
"""

from typing import (
    List,
    Optional,
    Union,
)

import numpy as np
from qctrlcommons.graph import Graph
from qctrlcommons.node.node_data import (
    Pwc,
    Tensor,
)
from qctrlcommons.preconditions import check_argument

from qctrltoolkit.namespace import Namespace
from qctrltoolkit.pulses.pulse_utils import validate_optimizable_parameter
from qctrltoolkit.toolkit_utils import expose


@expose(Namespace.PULSES)
def square_pulse_pwc(
    graph: Graph,
    duration: float,
    amplitude: Union[float, complex, Tensor],
    start_time: float = 0,
    end_time: Optional[float] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a square pulse.

    The entire signal lasts from time 0 to the given duration with the
    square pulse being applied from the start time to the end time.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal.
    amplitude : float or complex or Tensor
        The amplitude of the square pulse, :math:`A`.
        It must either be a scalar or contain a single element.
    start_time : float, optional
        The start time of the square pulse, :math:`t_\mathrm{start}`.
        Defaults to 0.
    end_time : float, optional
        The end time of the square pulse, :math:`t_\mathrm{end}`.
        Must be greater than the start time.
        Defaults to the value of the given duration.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The square pulse. The returned Pwc can have a maximum of three segments and a minimum
        of one, depending on the start time, end time, and duration of the pulse.

    See Also
    --------
    :func:`.pulses.cosine_pulse_pwc` : Create a `Pwc` representing a cosine pulse.
    :func:`.pulses.gaussian_pulse_pwc` : Create a `Pwc` representing a Gaussian pulse.
    :func:`.pulses.sech_pulse_pwc` : Create a `Pwc` representing a hyperbolic secant pulse.
    :func:`.pulses.square_pulse` : Function to create a `Pulse` object representing a square pulse.

    Notes
    -----
    The square pulse is defined as

    .. math:: \mathop{\mathrm{Square}}(t)
        = A \theta(t-t_\mathrm{start}) \theta(t_\mathrm{end}-t) \; ,

    where :math:`\theta(t)` is the
    `Heaviside step function <https://en.wikipedia.org/wiki/Heaviside_step_function>`_.

    Examples
    --------
    Define a square pulse with an optimizable amplitude.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
    ... )
    >>> graph.pulses.square_pulse_pwc(
    ...     duration=4.0, amplitude=amplitude, name="square"
    ... )
    <Pwc: name="square", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>

    Define a square PWC pulse.

    >>> graph.pulses.square_pulse_pwc(
    ...     duration=4.0,
    ...     amplitude=2.5,
    ...     start_time=1.0,
    ...     end_time=3.0,
    ...     name="square",
    ... )
    <Pwc: name="square", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["square"])
    >>> result.output["square"]
    [
        {'duration': 1.0, 'value': 0.0},
        {'duration': 2.0, 'value': 2.5},
        {'duration': 1.0, 'value': 0.0}
    ]
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    if end_time is None:
        end_time = duration

    check_argument(
        end_time > start_time,
        "The end time must be greater than the start time.",
        {"start_time": start_time, "end_time": end_time},
    )

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")

    if start_time >= duration or end_time <= 0:
        # In both of these cases the signal is always zero.
        return graph.pwc_signal(duration=duration, values=np.array([0.0]), name=name)

    pwcs = []

    if start_time > 0:
        # Add preceding step function.
        pwcs.append(graph.pwc_signal(duration=start_time, values=np.array([0.0])))

    pwcs.append(
        graph.pwc_signal(
            duration=min(end_time, duration) - max(start_time, 0),
            values=amplitude * np.array([1.0]),
        )
    )

    if end_time < duration:
        # Add trailing step function.
        pwcs.append(
            graph.pwc_signal(duration=duration - end_time, values=np.array([0.0]))
        )

    return graph.time_concatenate_pwc(pwcs, name=name)


@expose(Namespace.PULSES)
def sech_pulse_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    amplitude: Union[float, complex, Tensor],
    width: Optional[Union[float, Tensor]] = None,
    center_time: Optional[Union[float, Tensor]] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a hyperbolic secant pulse.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
    amplitude : float or complex or Tensor
        The amplitude of the pulse, :math:`A`.
        It must either be a scalar or contain a single element.
    width : float or Tensor, optional
        The characteristic time for the hyperbolic secant pulse, :math:`t_\mathrm{pulse}`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to :math:`T/12`,
        giving the pulse a full width at half maximum (FWHM) of :math:`0.22 T`.
    center_time : float or Tensor, optional
        The time at which the pulse peaks, :math:`t_\mathrm{peak}`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to :math:`T/2`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled hyperbolic secant pulse.

    See Also
    --------
    :func:`.pulses.cosine_pulse_pwc` : Create a `Pwc` representing a cosine pulse.
    :func:`.pulses.gaussian_pulse_pwc` : Create a `Pwc` representing a Gaussian pulse.
    :func:`.pulses.sech_pulse_stf` : Corresponding operation with `Stf` output.
    :func:`.pulses.square_pulse_pwc` : Create a `Pwc` representing a square pulse.

    Notes
    -----
    The hyperbolic secant pulse is defined as

    .. math:: \mathop{\mathrm{Sech}}(t)
        = \frac{A}{\cosh\left((t - t_\mathrm{peak}) / t_\mathrm{pulse} \right)} \;.

    The FWHM of the pulse is about :math:`2.634 t_\mathrm{pulse}`.

    Examples
    --------
    Define a simple sech PWC pulse.

    >>> graph.pulses.sech_pulse_pwc(
    ...     duration=5, segment_count=50, amplitude=1, name="sech"
    ... )
    <Pwc: name="sech", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sech"])
    >>> result.output["sech"]
    [
        {'value': -0.0056, 'duration': 0.1},
        {'value': -0.0071, 'duration': 0.1},
        ...
        {'value': 0.0071, 'duration': 0.1},
        {'value': 0.0056, 'duration': 0.1},
    ]

    Define a displaced sech PWC pulse.

    >>> graph.pulses.sech_pulse_pwc(
    ...     duration=3e-6,
    ...     segment_count=60,
    ...     amplitude=20e6,
    ...     width=0.15e-6,
    ...     center_time=1e-6,
    ...     name="sech_displaced",
    ... )
    <Pwc: name="sech_displaced", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sech_displaced"])
    >>> result.output["sech_displaced"]
    [
        {'value': 60137.43, 'duration': 5.e-08},
        {'value': 83928.37, 'duration': 5.e-08},
        ...
        {'value': 106.8105, 'duration': 5.e-08},
        {'value': 76.53310, 'duration': 5.e-08},
    ]

    Define a sech pulse with optimizable parameters.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=10e6, name="amplitude"
    ... )
    >>> width = graph.optimization_variable(
    ...     count=1, lower_bound=0.1e-6, upper_bound=0.5e-6, name="width"
    ... )
    >>> center_time = graph.optimization_variable(
    ...     count=1, lower_bound=1e-6, upper_bound=2e-6, name="center_time"
    ... )
    >>> graph.pulses.sech_pulse_pwc(
    ...     duration=3e-6,
    ...     segment_count=32,
    ...     amplitude=amplitude,
    ...     width=width,
    ...     center_time=center_time,
    ...     name="sech_pulse",
    ... )
    <Pwc: name="sech_pulse", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    if width is None:
        width = duration / 12

    if center_time is None:
        center_time = duration / 2

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")
    width = validate_optimizable_parameter(graph, width, "width")
    center_time = validate_optimizable_parameter(graph, center_time, "center time")

    stf = amplitude / graph.cosh((graph.identity_stf() - center_time) / width)
    return graph.discretize_stf(stf, duration, segment_count, name=name)


@expose(Namespace.PULSES)
def linear_ramp_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    end_value: Union[float, complex, Tensor],
    start_value: Optional[Union[float, complex, Tensor]] = None,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a linear ramp.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
    end_value : float or complex or Tensor
        The value of the ramp at :math:`t = t_\mathrm{end}`, :math:`a_\mathrm{end}`.
        It must either be a scalar or contain a single element.
    start_value : float or complex or Tensor, optional
        The value of the ramp at :math:`t = t_\mathrm{start}`, :math:`a_\mathrm{start}`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to :math:`-a_\mathrm{end}`.
    start_time : float, optional
        The time at which the linear ramp starts, :math:`t_\mathrm{start}`.
        Defaults to 0.
    end_time : float, optional
        The time at which the linear ramp ends, :math:`t_\mathrm{end}`.
        Defaults to the given duration :math:`T`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled linear ramp.

    See Also
    --------
    :func:`.pulses.linear_ramp_stf` : Corresponding operation with `Stf` output.
    :func:`.pulses.tanh_ramp_pwc` : Create a `Pwc` representing a hyperbolic tangent ramp.

    Notes
    -----
    The linear ramp is defined as

    .. math:: \mathop{\mathrm{Linear}}(t) =
        \begin{cases}
            a_\mathrm{start} &\mathrm{if} \quad t < t_\mathrm{start}\\
            a_\mathrm{start} + (a_\mathrm{end} - a_\mathrm{start})
                \frac{t - t_\mathrm{start}}{t_\mathrm{end} - t_\mathrm{start}}
                &\mathrm{if} \quad t_\mathrm{start} \le t \le t_\mathrm{end} \\
            a_\mathrm{end} &\mathrm{if} \quad t > t_\mathrm{end}
        \end{cases} \;.

    Examples
    --------
    Define a linear PWC ramp.

    >>> graph.pulses.linear_ramp_pwc(
    ...     duration=2.0, segment_count=5, end_value=1.5, start_value=0.5, name="linear_ramp"
    ... )
    <Pwc: name="linear_ramp", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["linear_ramp"])
    >>> result.output["linear_ramp"]
    [
        {'duration': 0.4, 'value': 0.6},
        {'duration': 0.4, 'value': 0.8},
        {'duration': 0.4, 'value': 1.0},
        {'duration': 0.4, 'value': 1.2},
        {'duration': 0.4, 'value': 1.4},
    ]

    Define a linear ramp with start and end times.

    >>> graph.pulses.linear_ramp_pwc(
    ...     duration=4,
    ...     segment_count=5,
    ...     end_value=2,
    ...     start_time=1,
    ...     end_time=3,
    ...     name="linear",
    ... )
    <Pwc: name="linear", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["linear"])
    >>> result.output["linear"]
    [
        {'value': -2.0, 'duration': 1.0},
        {'value': -1.5, 'duration': 0.5},
        {'value': -0.5, 'duration': 0.5},
        {'value': 0.5, 'duration': 0.5},
        {'value': 1.5, 'duration': 0.5},
        {'value': 2.0, 'duration': 1.0},
    ]

    Define a linear ramp with an optimizable slope around 0.

    >>> duration = 4.0
    >>> slope = graph.optimization_variable(
    ...     count=1, lower_bound=-30, upper_bound=30, name="slope"
    ... )
    >>> end_value = slope * duration / 2
    >>> graph.pulses.linear_ramp_pwc(
    ...     duration=duration, segment_count=64, end_value=end_value, name="linear_ramp"
    ... )
    <Pwc: name="linear_ramp", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    if start_value is None:
        start_value = -end_value

    if end_time is None:
        end_time = duration

    check_argument(
        start_time < end_time,
        "The end time of the pulse must be greater than the start time.",
        {"end_time": end_time, "start_time": start_time},
    )

    end_value = validate_optimizable_parameter(graph, end_value, "end value")
    start_value = validate_optimizable_parameter(graph, start_value, "start value")

    slope = (end_value - start_value) / (end_time - start_time)

    if start_time <= 0.0 and end_time >= duration:
        # No flat parts inside of the PWC.
        stf = start_value + slope * (graph.identity_stf() - start_time)
        return graph.discretize_stf(stf, duration, segment_count, name=name)

    if end_time <= 0.0 or start_time >= duration:
        # The whole ramp falls outside of the PWC.
        return graph.discretize_stf(
            graph.constant_stf(0.0), duration, segment_count, name=name
        )

    pre_step_pwc = None
    post_step_pwc = None

    if start_time > 0.0:
        # Preceding step function.
        pre_step_pwc = graph.constant_pwc(constant=start_value, duration=start_time)
        segment_count -= 1

    if end_time < duration:
        # Trailing step function.
        post_step_pwc = graph.constant_pwc(
            constant=end_value, duration=duration - end_time
        )
        segment_count -= 1

    # Ramp part.
    stf = start_value + slope * (graph.identity_stf() - min(start_time, 0.0))
    ramp_duration = min(end_time, duration) - max(start_time, 0.0)
    ramp_pwc = graph.discretize_stf(stf, ramp_duration, segment_count)

    pwcs = [ramp_pwc]
    if pre_step_pwc is not None:
        pwcs.insert(0, pre_step_pwc)
    if post_step_pwc is not None:
        pwcs.append(post_step_pwc)

    return graph.time_concatenate_pwc(pwcs, name=name)


@expose(Namespace.PULSES)
def tanh_ramp_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    end_value: Union[float, complex, Tensor],
    start_value: Optional[Union[float, complex, Tensor]] = None,
    ramp_duration: Optional[Union[float, Tensor]] = None,
    center_time: Optional[Union[float, Tensor]] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a hyperbolic tangent ramp.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
    end_value : float or complex or Tensor
        The asymptotic value of the ramp towards :math:`t \to +\infty`, :math:`a_+`.
        It must either be a scalar or contain a single element.
    start_value : float or complex or Tensor, optional
        The asymptotic value of the ramp towards :math:`t \to -\infty`, :math:`a_-`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to minus `end_value`.
    ramp_duration : float or Tensor, optional
        The characteristic time for the hyperbolic tangent ramp, :math:`t_\mathrm{ramp}`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to :math:`T/6`.
    center_time : float or Tensor, optional
        The time at which the ramp has its greatest slope, :math:`t_0`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to :math:`T/2`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled hyperbolic tangent ramp.

    See Also
    --------
    :func:`.pulses.linear_ramp_pwc` : Create a `Pwc` representing a linear ramp.
    :func:`.pulses.tanh_ramp_stf` : Corresponding operation with `Stf` output.
    :func:`~qctrl.graphs.Graph.tanh` : Calculate the element-wise hyperbolic tangent of an object.

    Notes
    -----
    The hyperbolic tangent ramp is defined as

    .. math:: \mathop{\mathrm{Tanh}}(t)
        = \frac{a_+ + a_-}{2}
            + \frac{a_+ - a_-}{2} \tanh\left( \frac{t - t_0}{t_\mathrm{ramp}} \right) \; ,

    where the function's asymptotic values :math:`a_\pm` are defined by:

    .. math::  a_\pm := \lim_{t\to\pm\infty} \mathop{\mathrm{Tanh}}(t) \;,

    and :math:`t_0` is related to :math:`t_\mathrm{ramp}` by:

    .. math::
        \left.\frac{{\rm d}\mathop{\mathrm{Tanh}}(t)}{{\rm d}t}\right|_{t=t_0}
            = \frac{ (a_+ - a_-)}{2 t_\mathrm{ramp}} \; .

    Note that if :math:`t_0` is close to the edges of the PWC,
    for example :math:`t_0 \lesssim 2 t_\mathrm{ramp}`,
    then the first and last values of the PWC will differ from the expected asymptotic values.

    With the default values of `start_value` (:math:`a_-`),
    `ramp_duration` (:math:`t_\mathrm{ramp}`), and `center_time` (:math:`t_0`),
    the ramp expression simplifies to

    .. math:: \mathop{\mathrm{Tanh}}(t) = A \tanh\left( \frac{t - T/2}{T/6} \right)\; ,

    where :math:`A = a_+` is the end value (the start value is then :math:`-A`).
    This defines a symmetric ramp (around :math:`(T/2, 0)`)
    between :math:`-0.995 A` (at :math:`t=0`) and :math:`0.995 A` (at :math:`t=T`).

    Examples
    --------
    Define a simple tanh PWC ramp.

    >>> graph.pulses.tanh_ramp_pwc(
    ...     duration=5.0, segment_count=50, end_value=1, name="tanh_ramp"
    ... )
    <Pwc: name="tanh_ramp", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["tanh_ramp"])
    >>> result.output["tanh_ramp"]
    [
        {'value': -0.9944, 'duration': 0.1},
        {'value': -0.9929, 'duration': 0.1},
        ...
        {'value': 0.9929, 'duration': 0.1},
        {'value': 0.9944, 'duration': 0.1},
    ]

    Define a flat-top pulse from two hyperbolic tangent ramps.

    >>> ramp = graph.pulses.tanh_ramp_pwc(
    ...     duration=3,
    ...     segment_count=60,
    ...     end_value=1,
    ...     ramp_duration=0.25,
    ...     center_time=0.5,
    ... )
    >>> flat_top_pulse = 0.5 * (ramp + graph.time_reverse_pwc(ramp))
    >>> flat_top_pulse.name="flat_top_pulse"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["flat_top_pulse"])
    >>> result.output["flat_top_pulse"]
    [
        {'value': 0.0219, 'duration': 0.05},
        {'value': 0.0323, 'duration': 0.05},
        ...
        {'value': 0.0323, 'duration': 0.05},
        {'value': 0.0219, 'duration': 0.05},
    ]

    Define a hyperbolic tangent ramp with optimizable parameters.

    >>> end_value = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=3e6, name="end_value"
    ... )
    >>> ramp_duration = graph.optimization_variable(
    ...     count=1, lower_bound=0.1e-6, upper_bound=0.3e-6, name="ramp_duration"
    ... )
    >>> center_time = graph.optimization_variable(
    ...     count=1, lower_bound=0.25e-6, upper_bound=0.75e-6, name="center_time"
    ... )
    >>> graph.pulses.tanh_ramp_pwc(
    ...     duration=1e-6,
    ...     segment_count=32,
    ...     end_value=end_value,
    ...     start_value=0.0,
    ...     ramp_duration=ramp_duration,
    ...     center_time=center_time,
    ...     name="tanh_ramp",
    ... )
    <Pwc: name="tanh_ramp", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    if start_value is None:
        start_value = -end_value

    if ramp_duration is None:
        ramp_duration = duration / 6

    if center_time is None:
        center_time = duration / 2

    end_value = validate_optimizable_parameter(graph, end_value, "end value")
    start_value = validate_optimizable_parameter(graph, start_value, "start value")
    ramp_duration = validate_optimizable_parameter(
        graph, ramp_duration, "ramp duration"
    )
    center_time = validate_optimizable_parameter(graph, center_time, "center time")

    stf = start_value + 0.5 * (end_value - start_value) * (
        1 + graph.tanh((graph.identity_stf() - center_time) / ramp_duration)
    )
    return graph.discretize_stf(stf, duration, segment_count, name=name)


def _allocate_segment_counts(
    durations: Union[List, np.ndarray], segment_count: int
) -> List:
    """
    Allocate the number of segments between two non-flat segments and one flat segment.
    The flat segment is assumed to lie in the middle of the other two.
    The number of segments each non-flat part has is in proportion to their duration of time.
    The non-flat durations are at indexes 0 and 2 of durations, durations[0] and durations[2].
    durations[1] can only be zero if one of durations[0] or durations[2] are also zero
    (e.g. [2,0,3] and [0,0,0] are not valid inputs).
    """
    # In the symmetric case (durations[0] = durations[2]), the flat part gets two segments
    # if segment_count is even and one otherwise.
    if np.isclose(durations[0], durations[2]):
        pulse_counts = [(segment_count - 1) // 2] * 2
        pulse_counts.insert(1, segment_count - 2 * pulse_counts[0])
        return pulse_counts

    flat_segments = int(durations[1] > 0.0)  # Number of flat segments.
    # Note that if flat_segments is 0, either durations[0] or durations[2] must be 0.
    if np.isclose(durations[0], 0.0):
        return [0, flat_segments, segment_count - flat_segments]
    if np.isclose(durations[2], 0.0):
        return [segment_count - flat_segments, flat_segments, 0]

    # In this case we know flat_segments=1 and all pulse_counts should be at least 1.
    non_flat_duration = durations[0] + durations[2]
    pulse_counts = [
        int((segment_count - 1) * durations[index] / non_flat_duration)
        for index in [0, 2]
    ]
    # Make sure the pulses each get at least one segment even if the duration is very small.
    pulse_counts = [max(pulse_count, 1) for pulse_count in pulse_counts]
    pulse_counts.insert(1, 1)

    # If there are too many or few segments, we update the largest segment count.
    pulse_counts[np.argmax(pulse_counts)] += segment_count - sum(pulse_counts)

    return pulse_counts


@expose(Namespace.PULSES)
def gaussian_pulse_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    amplitude: Union[float, complex, Tensor],
    width: Optional[Union[float, Tensor]] = None,
    center_time: Optional[float] = None,
    drag: Optional[Union[float, Tensor]] = None,
    flat_duration: Optional[float] = None,
    name: Optional[str] = None,
) -> Pwc:
    # pylint: disable=line-too-long
    r"""
    Create a `Pwc` representing a Gaussian pulse.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
        Must be at least four.
    amplitude : float or complex or Tensor
        The amplitude of the Gaussian pulse, :math:`A`.
        It must either be a scalar or contain a single element.
    width : float or Tensor, optional
        The standard deviation of the Gaussian pulse, :math:`\sigma`.
        It must either be a scalar or contain a single element.
        Defaults to :math:`T/10` or :math:`(T-t_\mathrm{flat})/10` if `flat_duration` is passed.
    center_time : float, optional
        The center of the Gaussian pulse, :math:`t_0`.
        Defaults to half of the given value of the duration, :math:`T/2`.
    drag : float or Tensor, optional
        The DRAG parameter, :math:`\beta`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to no DRAG correction.
    flat_duration : float, optional
        The amount of time to remain constant after the peak of the Gaussian,
        :math:`t_\mathrm{flat}`.
        If passed, it must be positive and less than the duration.
        Defaults to None, in which case no constant part is added to the Gaussian pulse.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled Gaussian pulse.
        If no flat duration is passed then the pulse is evenly sampled between :math:`0` and
        :math:`T`. If one is passed, the flat part of the pulse is described by one or two segments
        (depending on the values of `center_time` and `segment_count`), and the rest of the pulse is
        sampled with the remaining segments.

    See Also
    --------
    :func:`.pulses.cosine_pulse_pwc` : Create a `Pwc` representing a cosine pulse.
    :func:`.pulses.gaussian_pulse_stf` : Corresponding operation with `Stf` output.
    :func:`.pulses.sech_pulse_pwc` : Create a `Pwc` representing a hyperbolic secant pulse.
    :func:`.pulses.square_pulse_pwc` : Create a `Pwc` representing a square pulse.

    Notes
    -----
    The Gaussian pulse is defined as

    .. math:: \mathop{\mathrm{Gaussian}}(t) =
        \begin{cases}
            A \left(1-\frac{i\beta (t-t_1)}{\sigma^2}\right)
            \exp \left(- \frac{(t-t_1)^2}{2\sigma^2} \right)
                &\mathrm{if} \quad t < t_1=t_0- t_\mathrm{flat}/2\\
            A
                &\mathrm{if} \quad t_0-t_\mathrm{flat}/2 \le t < t_0+t_\mathrm{flat}/2 \\
            A \left(1-\frac{i\beta (t-t_2)}{\sigma^2}\right)
            \exp \left(- \frac{(t-t_2)^2}{2\sigma^2} \right)
                &\mathrm{if} \quad t > t_2=t_0+t_\mathrm{flat}/2
        \end{cases} \;.

    If the flat duration is zero (the default setting), this reduces to

    .. math:: \mathop{\mathrm{Gaussian}}(t) =
        A \left(1-\frac{i\beta (t-t_0)}{\sigma^2}\right)
        \exp \left(- \frac{(t-t_0)^2}{2\sigma^2} \right) \; .

    Examples
    --------
    Define a Gaussian PWC pulse.

    >>> graph.pulses.gaussian_pulse_pwc(
    ...     duration=3.0,
    ...     segment_count=100,
    ...     amplitude=1.0,
    ...     name="gaussian",
    ... )
    <Pwc: name="gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["gaussian"])
    >>> result.output["gaussian"]
    [
        {'duration': 0.03, 'value': 4.7791e-06},
        {'duration': 0.03, 'value': 7.8010e-06},
        ...
        {'duration': 0.03, 'value': 7.8010e-06},
        {'duration': 0.03, 'value': 4.7791e-06}
    ]

    Define a flat-top Gaussian PWC pulse with a DRAG correction.

    >>> graph.pulses.gaussian_pulse_pwc(
    ...     duration=3.0,
    ...     segment_count=100,
    ...     amplitude=1.0,
    ...     width=0.2,
    ...     center_time=1.5,
    ...     drag=0.1,
    ...     flat_duration=0.2,
    ...     name="gaussian_drag",
    ... )
    <Pwc: name="gaussian_drag", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["gaussian_drag"])
    >>> result.output["gaussian_drag"]
    [
        {'duration': 0.0285, 'value': (3.7655e-11+1.3044e-10j)},
        {'duration': 0.0285, 'value': (1.0028e-10+3.4026e-10j)},
        ...
        {'duration': 0.0285, 'value': (1.0028e-10-3.4026e-10j)},
        {'duration': 0.0285, 'value': (3.7655e-11-1.3044e-10j)}
    ]

    Define a Gaussian pulse with optimizable parameters.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
    ... )
    >>> width = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=2., name="width"
    ... )
    >>> drag = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=1., name="drag"
    ... )
    >>> graph.pulses.gaussian_pulse_pwc(
    ...     duration=3.0,
    ...     segment_count=100,
    ...     amplitude=amplitude,
    ...     width=width,
    ...     drag=drag,
    ...     name="gaussian",
    ... )
    <Pwc: name="gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    """
    # pylint:enable=line-too-long

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    if center_time is None:
        center_time = 0.5 * duration

    if width is None:
        if flat_duration is None:
            width = duration / 10
        else:
            width = (duration - flat_duration) / 10

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")
    width = validate_optimizable_parameter(graph, width, "width")

    def create_gaussian(center_parameter):
        assert width is not None
        return graph.exp(
            -((graph.identity_stf() - center_parameter) ** 2) / (2 * width**2)
        )

    def create_amplitude(center_parameter):
        assert width is not None
        if drag is None:
            return amplitude
        return amplitude * (
            1.0 - 1j * drag * (graph.identity_stf() - center_parameter) / (width**2)
        )

    if drag is not None:
        drag = validate_optimizable_parameter(graph, drag, "drag")

    if flat_duration is None:
        return graph.discretize_stf(
            create_amplitude(center_time) * create_gaussian(center_time),
            duration,
            segment_count,
            name=name,
        )

    check_argument(
        0.0 < flat_duration < duration,
        "The flat duration must be positive and less than the duration.",
        {"flat_duration": flat_duration},
        extras={"duration": duration},
    )

    check_argument(
        segment_count > 3,
        "The number of segments must be at least 4.",
        {"segment_count": segment_count},
    )

    # Time at which first Gaussian ends.
    flat_duration_start = center_time - 0.5 * flat_duration
    # Time at which second Gaussian starts.
    flat_duration_end = center_time + 0.5 * flat_duration

    if flat_duration_start >= duration:
        # In this case since the flat segment starts after the duration, it is not part of
        # the signal.
        return graph.discretize_stf(
            create_amplitude(flat_duration_start)
            * create_gaussian(flat_duration_start),
            duration,
            segment_count,
            name=name,
        )

    if flat_duration_end <= 0:
        # In this case since the flat segment finishes before time zero, it is not part of
        # the signal.
        return graph.discretize_stf(
            create_amplitude(flat_duration_end) * create_gaussian(flat_duration_end),
            duration,
            segment_count,
            name=name,
        )

    if flat_duration_end >= duration:
        # In this case since the flat segment finishes after the duration, the second Gaussian
        # is not part of the signal.
        durations = [flat_duration_start, duration - flat_duration_start]
        segment_counts = [segment_count - 1, 1]
        stfs = [
            create_amplitude(flat_duration_start)
            * create_gaussian(flat_duration_start),
            graph.constant_stf(amplitude),
        ]

    elif flat_duration_start <= 0:
        # In this case since the flat segment begins before time zero, the first Gaussian
        # is not part of the signal.
        durations = [flat_duration_end, duration - flat_duration_end]
        segment_counts = [1, segment_count - 1]
        stfs = [
            graph.constant_stf(amplitude),
            create_amplitude(0.0) * create_gaussian(0.0),
        ]

    else:
        durations = [flat_duration_start, flat_duration, duration - flat_duration_end]
        segment_counts = _allocate_segment_counts(durations, segment_count)
        stfs = [
            create_amplitude(flat_duration_start)
            * create_gaussian(flat_duration_start),
            graph.constant_stf(amplitude),
            create_amplitude(0.0) * create_gaussian(0.0),
        ]

    pwcs = [
        graph.discretize_stf(*args) for args in zip(stfs, durations, segment_counts)
    ]
    return graph.time_concatenate_pwc(pwcs, name=name)


@expose(Namespace.PULSES)
def cosine_pulse_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    amplitude: Union[float, complex, Tensor],
    drag: Optional[Union[float, Tensor]] = None,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    flat_duration: Optional[float] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a cosine pulse.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
        Must be at least six.
    amplitude : float or complex or Tensor
        The amplitude of the pulse, :math:`A`.
        It must either be a scalar or contain a single element.
    drag : float or Tensor, optional
        The DRAG parameter, :math:`\beta`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to no DRAG correction.
    start_time : float, optional
        The time at which the cosine pulse starts, :math:`t_\mathrm{start}`.
        Defaults to 0.
    end_time : float, optional
        The time at which the cosine pulse ends, :math:`t_\mathrm{end}`.
        Defaults to the given duration :math:`T`.
    flat_duration : float, optional
        The amount of time to remain constant after the peak of the cosine,
        :math:`t_\mathrm{flat}`.
        If passed, it must be positive and less than the difference between `end_time` and
        `start_time`.
        Defaults to None, in which case no constant part is added to the cosine pulse.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled cosine pulse.
        If no flat duration is passed then the pulse is evenly sampled between :math:`0` and
        :math:`T`. If one is passed, the flat part of the pulse is described by one or two segments
        (depending on the value of `segment_count`), and the rest of the pulse is sampled with the
        remaining segments.

    See Also
    --------
    :func:`.pulses.cosine_pulse` : Function to create a `Pulse` object representing a cosine pulse.
    :func:`.pulses.gaussian_pulse_pwc` : Create a `Pwc` representing a Gaussian pulse.
    :func:`.pulses.hann_series_pwc` : Create a `Pwc` representing a sum of Hann window functions.
    :func:`.pulses.sech_pulse_pwc` : Create a `Pwc` representing a hyperbolic secant pulse.
    :func:`.pulses.sinusoid_pwc` : Create a `Pwc` representing a sinusoidal oscillation.
    :func:`.pulses.square_pulse_pwc` : Create a `Pwc` representing a square pulse.
    :func:`~qctrl.graphs.Graph.cos` : Calculate the element-wise cosine of an object.

    Notes
    -----
    The cosine pulse is defined as

    .. math:: \mathop{\mathrm{Cos}}(t) =
        \begin{cases}
        0
        &\mathrm{if} \quad t < t_\mathrm{start} \\
        \frac{A}{2} \left[1+\cos \left(\omega \{t-\tau_-\} \right)
        + i\omega\beta \sin \left(\omega \{t-\tau_-\}\right)\right]
        &\mathrm{if} \quad t_\mathrm{start} \le t < \tau_- \\
        A
        &\mathrm{if} \quad \tau_- \le t \le \tau_+ \\
        \frac{A}{2} \left[1+\cos \left(\omega\{t-\tau_+\}\right)
        + i\omega \beta\sin \left(\omega \{t-\tau_+\}\right)\right]
        &\mathrm{if} \quad \tau_+ < t \le t_\mathrm{end} \\
        0
        &\mathrm{if} \quad t > t_\mathrm{end} \\
        \end{cases}\; ,

    where :math:`\omega=2\pi /(t_\mathrm{end}-t_\mathrm{start} - t_\mathrm{flat})`,
    :math:`\tau_\mp` are the start/end times of the flat segment,
    with :math:`\tau_\mp=(t_\mathrm{start}+t_\mathrm{end} \mp t_\mathrm{flat})/2`.

    If the flat duration is zero (the default setting), this reduces to

    .. math:: \mathop{\mathrm{Cos}}(t) =
        \frac{A}{2} \left[1+\cos \left(\omega \{t-\tau\} \right)
        + i\omega\beta \sin \left(\omega \{t-\tau\}\right)\right]
        \theta(t-t_\mathrm{start}) \theta(t_\mathrm{end}-t)\; ,

    where now :math:`\omega=2\pi /(t_\mathrm{end}-t_\mathrm{start})`,
    :math:`\tau=(t_\mathrm{start}+t_\mathrm{end})/2`
    and :math:`\theta(t)` is the
    `Heaviside step function <https://en.wikipedia.org/wiki/Heaviside_step_function>`_.

    Examples
    --------
    Define a cosine PWC pulse.

    >>> graph.pulses.cosine_pulse_pwc(
    ...     duration=3.0, segment_count=100, amplitude=1.0, name="cos_pulse"
    ... )
    <Pwc: name="cos_pulse", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["cos_pulse"])
    >>> result.output["cos_pulse"]
    [
        {'duration': 0.03, 'value': 0.00024},
        {'duration': 0.03, 'value': 0.00221},
        ...
        {'duration': 0.03, 'value': 0.00221},
        {'duration': 0.03, 'value': 0.00024}
    ]

    Define a flat-top cosine PWC pulse with a DRAG correction.

    >>> graph.pulses.cosine_pulse_pwc(
    ...     duration=3.0,
    ...     segment_count=100,
    ...     amplitude=1.0,
    ...     drag=0.1,
    ...     start_time=1.0,
    ...     end_time=2.0,
    ...     flat_duration=0.3,
    ...     name="cos_flat",
    ... )
    <Pwc: name="cos_flat", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["cos_flat"])
    >>> result.output["cos_flat"]
    [
        {'duration': 1.0, 'value': 0j},
        {'duration': 0.0072, 'value': (0.0002-0.0146j)}
        ...
        {'duration': 0.0072, 'value': (0.0002+0.0146j)},
        {'duration': 1.0, 'value': 0j}
    ]

    Define a cosine pulse with optimizable parameters.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
    ... )
    >>> drag = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=1., name="drag"
    ... )
    >>> graph.pulses.cosine_pulse_pwc(
    ...     duration=3.0,
    ...     segment_count=100,
    ...     amplitude=amplitude,
    ...     drag=drag,
    ...     name="cos_pulse",
    ... )
    <Pwc: name="cos_pulse", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    if end_time is None:
        end_time = duration

    check_argument(
        start_time < end_time,
        "The end time of the pulse must be greater than the start time.",
        {"end_time": end_time, "start_time": start_time},
    )

    if start_time >= duration or end_time <= 0:
        # In both of these cases the signal is always zero.
        return graph.pwc_signal(
            duration=duration, values=np.zeros(segment_count), name=name
        )

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")

    if drag is not None:
        drag = validate_optimizable_parameter(graph, drag, "drag")

    def create_pulse(
        peak_parameter, omega_parameter, duration_parameter, segment_count_parameter
    ):
        # Samples the function
        #   A/2[1 + \cos(\omega\{t-t_p\}) + i\omega \beta \sin(\omega\{t - t_p\})]
        # between 0 and duration_parameter,
        # where A is the amplitude, \omega the omega_parameter, t_p the peak_parameter
        # and \beta the DRAG parameter.
        # segment_count_parameter is the number of the returned PWC.

        times, time_step = np.linspace(
            0, duration_parameter, segment_count_parameter, endpoint=False, retstep=True
        )

        shifted_times = (times + time_step / 2) - peak_parameter

        pulse = 1 + np.cos(omega_parameter * shifted_times)
        if drag is not None:
            pulse = pulse + omega_parameter * drag * 1j * np.sin(
                omega_parameter * shifted_times
            )

        return graph.pwc_signal(
            duration=duration_parameter, values=0.5 * amplitude * pulse
        )

    pwcs = []

    pulse_segment_count = (
        segment_count - (start_time > 0.0) - (end_time < duration)
    )  # The number of segments for the cosine pulse.
    pulse_period = end_time - start_time  # The period of the cosine pulse.

    if start_time > 0.0:
        # Add preceding step function.
        pwcs.append(graph.pwc_signal(duration=start_time, values=np.array([0.0])))

    if flat_duration is None:
        angular_freq = 2 * np.pi / pulse_period
        # The peak is 0.5 * pulse_period after the
        # start of the pulse plus start_time if start_time < 0.
        pwcs.append(
            create_pulse(
                0.5 * pulse_period + min(start_time, 0),
                angular_freq,
                min(duration, end_time) - max(start_time, 0),
                pulse_segment_count,
            )
        )
    else:
        check_argument(
            0 < flat_duration < pulse_period,
            "The flat duration must be positive and less than the end time of the pulse minus the "
            "start time.",
            {
                "flat_duration": flat_duration,
                "start_time": start_time,
                "end_time": end_time,
            },
            extras={"end_time - start_time": end_time - start_time},
        )
        check_argument(
            segment_count > 5,
            "The number of segments must be at least 6.",
            {"segment_count": segment_count},
        )

        pulse_period -= flat_duration
        angular_freq = 2 * np.pi / pulse_period
        pulse_center = 0.5 * (start_time + end_time)
        flat_segment_start = pulse_center - flat_duration * 0.5
        flat_segment_end = pulse_center + flat_duration * 0.5

        durations = np.array(
            [
                min(flat_segment_start, duration) - max(start_time, 0),
                min(flat_segment_end, duration) - max(flat_segment_start, 0),
                min(end_time, duration) - max(flat_segment_end, 0),
            ]
        )
        durations = durations * (durations > 0.0)

        if flat_segment_start <= 0.0 and flat_segment_end >= duration:
            # In this case the flat segment is the entire signal.
            segment_counts = [0, pulse_segment_count, 0]
        else:
            segment_counts = _allocate_segment_counts(durations, pulse_segment_count)

        if flat_segment_start > 0.0:
            pwcs.append(
                create_pulse(
                    0.5 * pulse_period + min(start_time, 0),
                    angular_freq,
                    durations[0],
                    segment_counts[0],
                )
            )

        if flat_segment_start < duration and flat_segment_end > 0.0:
            pwcs.append(
                graph.discretize_stf(
                    graph.constant_stf(amplitude), durations[1], segment_counts[1]
                )
            )

        if flat_segment_end < duration:
            # The peak is at the start of the pulse, unless flat_segment_end < 0 in which case it's
            # flat_segment_end.
            pwcs.append(
                create_pulse(
                    min(flat_segment_end, 0),
                    angular_freq,
                    durations[2],
                    segment_counts[2],
                )
            )

    if end_time < duration:
        # Add trailing step function.
        pwcs.append(
            graph.pwc_signal(duration=duration - end_time, values=np.array([0.0]))
        )

    return graph.time_concatenate_pwc(pwcs, name=name)


@expose(Namespace.PULSES)
def sinusoid_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    amplitude: Union[float, complex, Tensor],
    angular_frequency: Union[float, Tensor],
    phase: Union[float, Tensor] = 0.0,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a sinusoidal oscillation.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
    amplitude : float or complex or Tensor
        The amplitude of the oscillation, :math:`A`.
        It must either be a scalar or contain a single element.
    angular_frequency : float or Tensor
        The angular frequency of the oscillation, :math:`\omega`.
        It must either be a scalar or contain a single element.
    phase : float or Tensor, optional
        The phase of the oscillation, :math:`\phi`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to 0.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled sinusoid.

    See Also
    --------
    :func:`.pulses.cosine_pulse_pwc` : Create a `Pwc` representing a cosine pulse.
    :func:`.pulses.hann_series_pwc` : Create a `Pwc` representing a sum of Hann window functions.
    :func:`.pulses.sinusoid` :
        Function to create a `Pulse` object representing a sinusoidal oscillation.
    :func:`.pulses.sinusoid_stf` : Corresponding operation with `Stf` output.
    :func:`~qctrl.graphs.Graph.sin` : Calculate the element-wise sine of an object.

    Notes
    -----
    The sinusoid is defined as

    .. math:: \mathop{\mathrm{Sinusoid}}(t) = A \sin \left( \omega t + \phi \right) \;.

    Examples
    --------
    Define a PWC oscillation.

    >>> graph.pulses.sinusoid_pwc(
    ...     duration=5.0,
    ...     segment_count=100,
    ...     amplitude=1.0,
    ...     angular_frequency=np.pi,
    ...     phase=np.pi/2.0,
    ...     name="oscillation"
    ... )
    <Pwc: name="oscillation", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["oscillation"])
    >>> result.output["oscillation"]
    [
        {'value': 0.997, 'duration': 0.05},
        {'value': 0.972, 'duration': 0.05},
        ...
        {'value': -0.972, 'duration': 0.05},
        {'value': -0.996, 'duration': 0.05},
    ]

    Define a sinusoid with optimizable parameters.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=4e3, name="amplitude"
    ... )
    >>> angular_frequency = graph.optimization_variable(
    ...     count=1, lower_bound=5e6, upper_bound=20e6, name="angular_frequency"
    ... )
    >>> phase = graph.optimization_variable(
    ...     count=1,
    ...     lower_bound=0,
    ...     upper_bound=2*np.pi,
    ...     is_lower_unbounded=True,
    ...     is_upper_unbounded=True,
    ...     name="phase",
    ... )
    >>> graph.pulses.sinusoid_pwc(
    ...     duration=3e-6,
    ...     segment_count=100,
    ...     amplitude=amplitude,
    ...     angular_frequency=angular_frequency,
    ...     phase=phase,
    ...     name="oscillation"
    ... )
    <Pwc: name="oscillation", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")
    angular_frequency = validate_optimizable_parameter(
        graph, angular_frequency, "angular frequency"
    )
    phase = validate_optimizable_parameter(graph, phase, "phase")

    stf = amplitude * graph.sin(angular_frequency * graph.identity_stf() + phase)
    return graph.discretize_stf(stf, duration, segment_count, name=name)


@expose(Namespace.PULSES)
def hann_series_pwc(
    graph: Graph,
    duration: float,
    segment_count: int,
    coefficients: Union[np.ndarray, Tensor],
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Create a `Pwc` representing a sum of Hann window functions.

    The piecewise-constant function is sampled from Hann functions that start and end at zero.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    duration : float
        The duration of the signal, :math:`T`.
    segment_count : int
        The number of segments in the PWC.
    coefficients : np.ndarray or Tensor
        The coefficients for the different Hann window functions, :math:`c_n`.
        It must be a 1D array or Tensor and it can't contain more than `segment_count` elements.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The sampled Hann window functions series.

    See Also
    --------
    :func:`.pulses.cosine_pulse_pwc` : Create a `Pwc` representing a cosine pulse.
    :func:`.pulses.sinusoid_pwc` : Create a `Pwc` representing a sinusoidal oscillation.
    :func:`.pulses.hann_series` :
        Function to create a `Pulse` object representing a sum of Hann window functions.
    :func:`.pulses.hann_series_stf` : Corresponding operation with `Stf` output.

    Notes
    -----
    The series is defined as

    .. math:: \mathop{\mathrm{Hann}}(t)
        = \sum_{n=1}^N c_n \sin^2 \left( \frac{\pi n t}{T} \right) \;,

    where :math:`N` is the number of coefficients.

    Examples
    --------
    Define a simple Hann series.

    >>> graph.pulses.hann_series_pwc(
    ...     duration=5.0,
    ...     segment_count=50,
    ...     coefficients=np.array([0.5, 1, 0.25]),
    ...     name="hann_series",
    ... )
    <Pwc: name="hann_series", operation_name="pwc_signal", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["hann_series"]
    ... )
    >>> result.output["hann_series"]
    [
        {'value': 0.0067, 'duration': 0.1},
        {'value': 0.0590, 'duration': 0.1},
        ...
        {'value': 0.0590, 'duration': 0.1},
        {'value': 0.0067, 'duration': 0.1},
    ]

    Define a Hann series with optimizable coefficients.

    >>> coefficients = graph.optimization_variable(
    ...     count=8, lower_bound=-3.5e6, upper_bound=3.5e6, name="coefficients"
    ... )
    >>> graph.pulses.hann_series_pwc(
    ...     duration=2.0e-6,
    ...     segment_count=128,
    ...     coefficients=coefficients,
    ...     name="hann_series",
    ... )
    <Pwc: name="hann_series", operation_name="pwc_signal", value_shape=(), batch_shape=()>
    """

    check_argument(
        duration > 0.0, "The duration must be positive.", {"duration": duration}
    )

    check_argument(
        len(coefficients.shape) == 1,
        "The coefficients must be in a 1D array or Tensor.",
        {"coefficients": coefficients},
        extras={"coefficients.shape": coefficients.shape},
    )

    check_argument(
        coefficients.shape[0] <= segment_count,
        "There can't be more coefficients than segments.",
        {"coefficients": coefficients, "segment_count": segment_count},
        extras={"coefficients.shape": coefficients.shape},
    )

    # Define scaled times π t / T to sample the function.
    times, time_step = np.linspace(
        0, duration, segment_count, endpoint=False, retstep=True
    )
    scaled_times = (times + time_step / 2) * np.pi / duration

    # Calculate function values.
    nss = np.arange(1, coefficients.shape[0] + 1)
    values = graph.sum(coefficients * np.sin(nss * scaled_times[:, None]) ** 2, axis=1)

    return graph.pwc_signal(duration=duration, values=values, name=name)
