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
STF pulse library nodes.
"""

from typing import (
    Optional,
    Union,
)

import numpy as np
from qctrlcommons.graph import Graph
from qctrlcommons.node.node_data import (
    Stf,
    Tensor,
)
from qctrlcommons.preconditions import check_argument

from qctrltoolkit.namespace import Namespace
from qctrltoolkit.pulses.pulse_utils import validate_optimizable_parameter
from qctrltoolkit.toolkit_utils import expose


@expose(Namespace.PULSES)
def sech_pulse_stf(
    graph: Graph,
    amplitude: Union[float, complex, Tensor],
    width: Union[float, Tensor],
    center_time: Union[float, Tensor],
) -> Stf:
    r"""
    Create an `Stf` representing a hyperbolic secant pulse.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    amplitude : float or complex or Tensor
        The amplitude of the pulse, :math:`A`.
        It must either be a scalar or contain a single element.
    width : float or Tensor
        The characteristic time for the hyperbolic secant pulse, :math:`t_\mathrm{pulse}`.
        It must either be a scalar or contain a single element.
    center_time : float or Tensor
        The time at which the pulse peaks, :math:`t_\mathrm{peak}`.
        It must either be a scalar or contain a single element.

    Returns
    -------
    Stf
        The sampleable hyperbolic secant pulse.

    See Also
    --------
    :func:`.pulses.gaussian_pulse_stf` : Create an `Stf` representing a Gaussian pulse.
    :func:`.pulses.sech_pulse_pwc` : Corresponding operation with `Pwc` output.

    Notes
    -----
    The hyperbolic secant pulse is defined as

        .. math:: \mathop{\mathrm{Sech}}(t)
            = \frac{A}{\cosh\left((t - t_\mathrm{peak}) / t_\mathrm{pulse} \right)} \;.

    The full width at half maximum of the pulse is about :math:`2.634 t_\mathrm{pulse}`.

    Examples
    --------
    Define a sampleable sech pulse.

    >>> sech = graph.pulses.sech_pulse_stf(
    ...     amplitude=1.0, width=0.1, center_time=0.5
    ... )
    >>> sech
    <Stf: operation_name="truediv", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(stf=sech, sample_times=np.linspace(0, 1, 5), name="sech_samples")
    <Tensor: name="sech_samples", operation_name="sample_stf", shape=(5,)>
    >>> graph.discretize_stf(stf=sech, duration=1.2, segment_count=100, name="discretized_sech")
    <Pwc: name="discretized_sech", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["sech_samples", "discretized_sech"]
    ... )
    >>> result.output["sech_samples"]["value"]
    array([0.013, 0.163, 1.000, 0.163, 0.013])

    Define a sampleable sech pulse with optimizable parameters.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
    ... )
    >>> width = graph.optimization_variable(
    ...     count=1, lower_bound=0.1, upper_bound=0.5, name="width"
    ... )
    >>> center_time = graph.optimization_variable(
    ...     count=1, lower_bound=0.2, upper_bound=0.8, name="center_time"
    ... )
    >>> graph.pulses.sech_pulse_stf(
    ...     amplitude=amplitude, width=width, center_time=center_time
    ... )
    <Stf: operation_name="truediv", value_shape=(), batch_shape=()>
    """

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")
    width = validate_optimizable_parameter(graph, width, "width")
    center_time = validate_optimizable_parameter(graph, center_time, "center time")

    return amplitude / graph.cosh((graph.identity_stf() - center_time) / width)


@expose(Namespace.PULSES)
def gaussian_pulse_stf(
    graph: Graph,
    amplitude: Union[float, complex, Tensor],
    width: Union[float, Tensor],
    center_time: Union[float, Tensor],
    drag: Optional[Union[float, Tensor]] = None,
) -> Stf:
    # pylint: disable=line-too-long
    r"""
    Create an `Stf` representing a Gaussian pulse.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    amplitude : float or complex or Tensor
        The amplitude of the Gaussian pulse, :math:`A`.
        It must either be a scalar or contain a single element.
    width : float or Tensor
        The standard deviation of the Gaussian pulse, :math:`\sigma`.
        It must either be a scalar or contain a single element.
    center_time : float or Tensor
        The center of the Gaussian pulse, :math:`t_0`.
        It must either be a scalar or contain a single element.
    drag : float or Tensor, optional
        The DRAG parameter, :math:`\beta`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to no DRAG correction.

    Returns
    -------
    Stf
        The sampleable Gaussian pulse.

    See Also
    --------
    :func:`.pulses.gaussian_pulse_pwc` : Corresponding operation with `Pwc` output.
    :func:`.pulses.sech_pulse_stf` : Create an `Stf` representing a hyperbolic secant pulse.

    Notes
    -----
    The Gaussian pulse is defined as

    .. math:: \mathop{\mathrm{Gaussian}}(t) =
        A \left(1-\frac{i\beta (t-t_0)}{\sigma^2}\right)
        \exp \left(- \frac{(t-t_0)^2}{2\sigma^2} \right) \; .

    Examples
    --------
    Define a sampleable Gaussian pulse.

    >>> gaussian = graph.pulses.gaussian_pulse_stf(
    ...     amplitude=1.0, width=0.1, center_time=0.5
    ... )
    >>> gaussian
    <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(stf=gaussian, sample_times=np.linspace(0, 1, 5), name="gaussian_samples")
    <Tensor: name="gaussian_samples", operation_name="sample_stf", shape=(5,)>
    >>> graph.discretize_stf(
    ... gaussian, duration=1, segment_count=100, name="discretized_gaussian"
    ... )
    <Pwc: name="discretized_gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["gaussian_samples", "discretized_gaussian"]
    ... )
    >>> result.output["gaussian_samples"]["value"]
    array([3.727e-06, 4.394e-02, 1.000e+00, 4.394e-02, 3.727e-06])

    Define a sampleable Gaussian with a DRAG correction.

    >>> gaussian = graph.pulses.gaussian_pulse_stf(
    ...     amplitude=1.0, width=0.1, center_time=0.5, drag=0.2
    ... )
    >>> gaussian
    <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(
    ...     stf=gaussian, sample_times=np.linspace(0, 1, 5), name="drag_gaussian_samples"
    ... )
    <Tensor: name="drag_gaussian_samples", operation_name="sample_stf", shape=(5,)>
    >>> graph.discretize_stf(
    ...     gaussian, duration=1, segment_count=100, name="discretized_drag_gaussian"
    ... )
    <Pwc: name="discretized_drag_gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["drag_gaussian_samples", "discretized_drag_gaussian"]
    ... )
    >>> result.output["drag_gaussian_samples"]["value"]
    array([
        3.727e-06 + 9.317e-06j,
        4.394e-02 + 5.492e-02j,
        1.000e+00 + 0.000e+00j,
        4.394e-02 - 5.492e-02j,
        3.727e-06 - 9.317e-06j,
    ])

    Define a sampleable Gaussian pulse with optimizable parameters.

    >>> amplitude = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
    ... )
    >>> width = graph.optimization_variable(
    ...     count=1, lower_bound=0.1, upper_bound=0.5, name="width"
    ... )
    >>> center_time = graph.optimization_variable(
    ...     count=1, lower_bound=0.2, upper_bound=0.8, name="center_time"
    ... )
    >>> drag = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=0.5, name="drag"
    ... )
    >>> graph.pulses.gaussian_pulse_stf(
    ...     amplitude=amplitude, width=width, center_time=center_time, drag=drag
    ... )
    <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
    """
    # pylint: enable=line-too-long

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")
    width = validate_optimizable_parameter(graph, width, "width")
    center_time = validate_optimizable_parameter(graph, center_time, "center time")

    if drag is not None:
        drag = validate_optimizable_parameter(graph, drag, "drag")
        correction = -(1j * drag / (width**2)) * (graph.identity_stf() - center_time)
        amplitude *= 1.0 + correction

    return amplitude * graph.exp(
        -((graph.identity_stf() - center_time) ** 2) / (2 * width**2)
    )


@expose(Namespace.PULSES)
def sinusoid_stf(
    graph: Graph,
    amplitude: Union[float, complex, Tensor],
    angular_frequency: Union[float, Tensor],
    phase: Union[float, Tensor] = 0.0,
) -> Stf:
    # pylint: disable=line-too-long
    r"""
    Create an `Stf` representing a sinusoidal oscillation.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
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

    Returns
    -------
    Stf
        The sampleable sinusoid.

    See Also
    --------
    :func:`.pulses.hann_series_stf` : Create an `Stf` representing a sum of Hann window functions.
    :func:`.pulses.sinusoid` :
        Function to create a `Pulse` object representing a sinusoidal oscillation.
    :func:`.pulses.sinusoid_pwc` : Corresponding operation with `Pwc` output.
    :func:`~qctrl.graphs.Graph.sin` : Calculate the element-wise sine of an object.

    Notes
    -----
    The sinusoid is defined as

    .. math:: \mathop{\mathrm{Sinusoid}}(t) = A \sin \left( \omega t + \phi \right) \;.

    Examples
    --------
    Define an STF oscillation.

    >>> oscillation = graph.pulses.sinusoid_stf(
    ...     amplitude=1.0, angular_frequency=np.pi, phase=np.pi/2.0
    ... )
    >>> oscillation
    <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(stf=oscillation, sample_times=np.linspace(0, 1, 5), name="oscillation")
    <Tensor: name="oscillation", operation_name="sample_stf", shape=(5,)>
    >>> graph.discretize_stf(
    ...     oscillation, duration=10, segment_count=100, name="discretized_oscillation"
    ... )
    <Pwc: name="discretized_oscillation", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["oscillation", "discretized_oscillation"]
    ... )
    >>> result.output["oscillation"]["value"]
    array([ 1.000e+00,  7.071e-01,  1.225e-16, -7.071e-01, -1.000e+00])

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
    >>> graph.pulses.sinusoid_stf(
    ...     amplitude=amplitude, angular_frequency=angular_frequency, phase=phase
    ... )
    <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
    """
    # pylint: enable=line-too-long

    amplitude = validate_optimizable_parameter(graph, amplitude, "amplitude")
    angular_frequency = validate_optimizable_parameter(
        graph, angular_frequency, "angular frequency"
    )
    phase = validate_optimizable_parameter(graph, phase, "phase")

    return amplitude * graph.sin(angular_frequency * graph.identity_stf() + phase)


@expose(Namespace.PULSES)
def hann_series_stf(
    graph: Graph,
    coefficients: Union[np.ndarray, Tensor],
    end_time: float,
    start_time: float = 0.0,
) -> Stf:
    r"""
    Create an `Stf` representing a sum of Hann window functions.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    coefficients : np.ndarray or Tensor
        The coefficients for the different Hann window functions, :math:`c_n`.
        It must be a 1D array or Tensor.
    end_time : float
        The time at which the cosine pulse ends, :math:`t_\mathrm{end}`.
    start_time : float, optional
        The time at which the cosine pulse ends, :math:`t_\mathrm{start}`.
        Defaults to 0.

    Returns
    -------
    Stf
        The sampleable Hann window functions series.

    See Also
    --------
    :func:`.pulses.hann_series` :
        Function to create a `Pulse` object representing a sum of Hann window functions.
    :func:`.pulses.hann_series_pwc` : Corresponding operation with `Pwc` output.
    :func:`.pulses.sinusoid_stf` : Create an `Stf` representing a sinusoidal oscillation.

    Notes
    -----
    The series is defined as

    .. math:: \mathop{\mathrm{Hann}}(t)
        = \sum_{n=1}^N c_n \sin^2 \left(
            \frac{\pi n (t - t_\mathrm{start})}{t_\mathrm{end} - t_\mathrm{start}}
        \right) \;,

    where :math:`N` is the number of coefficients.

    Note that the function values outside the :math:`(t_\mathrm{start}, t_\mathrm{end})` range
    will not be zero.

    Examples
    --------
    Define a simple sampleable Hann series.

    >>> hann = graph.pulses.hann_series_stf(coefficients=np.array([0.5, 1, 0.25]), end_time=1.0)
    >>> hann
    <Stf: operation_name="stf_sum", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(stf=hann, sample_times=np.linspace(0, 1, 7), name="hann_samples")
    <Tensor: name="hann_samples", operation_name="hann_samples", shape=(7,)>
    >>> graph.discretize_stf(hann, duration=1, segment_count=100, name="discretized_hann")
    <Pwc: name="discretized_hann", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["hann_samples", "discretized_hann"]
    ... )
    >>> result.output["hann_samples"]["value"]
    array([0.000e+00, 1.125e+00, 1.125e+00, 7.500e-01, 1.125e+00, 1.125e+00, 5.159e-14])

    Define a sampleable Hann series with optimizable coefficients.

    >>> coefficients = graph.optimization_variable(
    ...     count=8, lower_bound=-3.5e6, upper_bound=3.5e6, name="coefficients"
    ... )
    >>> graph.pulses.hann_series_stf(coefficients=coefficients, end_time=2.0e-6)
    <Stf: operation_name="stf_sum", value_shape=(), batch_shape=()>
    """

    check_argument(
        len(coefficients.shape) == 1,
        "The coefficients must be in a 1D array or Tensor.",
        {"coefficients": coefficients},
        extras={"coefficients.shape": coefficients.shape},
    )

    check_argument(
        end_time > start_time,
        "The end time must be greater than the start time.",
        {"start_time": start_time, "end_time": end_time},
    )

    # Define scaled times π (t - t_start) / (t_end - t_start).
    scaled_time = (graph.identity_stf() - start_time) * (
        np.pi / (end_time - start_time)
    )

    # Calculate function values.
    stfs = [
        coefficients[idx] * graph.sin((idx + 1) * scaled_time) ** 2
        for idx in range(coefficients.shape[0])
    ]
    return graph.stf_sum(stfs)


@expose(Namespace.PULSES)
def linear_ramp_stf(
    graph: Graph,
    slope: Union[float, complex, Tensor],
    shift: Union[float, complex, Tensor] = 0.0,
) -> Stf:
    # pylint:disable=line-too-long
    r"""
    Create an `Stf` representing a linear ramp.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    slope : float or complex or Tensor
        The slope of the ramp, :math:`a`.
        It must either be a scalar or contain a single element.
    shift : float or complex or Tensor, optional
        The value of the ramp at :math:`t = 0`, :math:`b`.
        It must either be a scalar or contain a single element.
        Defaults to 0.

    Returns
    -------
    Stf
        The sampleable linear ramp.

    See Also
    --------
    :func:`.pulses.linear_ramp_pwc` : Corresponding operation with `Pwc` output.
    :func:`.pulses.tanh_ramp_stf` : Create an `Stf` representing a hyperbolic tangent ramp.

    Notes
    -----
    The linear ramp is defined as

    .. math:: \mathop{\mathrm{Linear}}(t) = a t + b \;.

    Examples
    --------
    Define a linear STF ramp.

    >>> linear = graph.pulses.linear_ramp_stf(slope=4.0, shift=-2.0)
    >>> linear
    <Stf: operation_name="add", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(stf=linear, sample_times=np.linspace(0, 1, 5), name="linear_ramp")
    <Tensor: name="linear_ramp", operation_name="sample_stf", shape=(5,)>
    >>> graph.discretize_stf(linear, duration=1, segment_count=100, name="discretized_linear")
    <Pwc: name="discretized_linear", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["linear_ramp", "discretized_linear"]
    ... )
    >>> result.output["linear_ramp"]["value"]
    array([-2., -1., 0., 1., 2.]

    Define a linear STF ramp with an optimizable slope and root.

    >>> slope = graph.optimization_variable(
    ...     count=1, lower_bound=-4, upper_bound=4, name="slope"
    ... )
    >>> root = graph.optimization_variable(
    ...     count=1, lower_bound=-4, upper_bound=4, name="slope"
    ... )
    >>> shift = - slope * root
    >>> graph.pulses.linear_ramp_stf(slope=slope, shift=shift)
    <Stf: operation_name="add", value_shape=(), batch_shape=()>
    """
    # pylint:enable=line-too-long

    slope = validate_optimizable_parameter(graph, slope, "slope")
    shift = validate_optimizable_parameter(graph, shift, "shift")

    return slope * graph.identity_stf() + shift


@expose(Namespace.PULSES)
def tanh_ramp_stf(
    graph: Graph,
    center_time: Union[float, Tensor],
    ramp_duration: Union[float, Tensor],
    end_value: Union[float, complex, Tensor],
    start_value: Optional[Union[float, complex, Tensor]] = None,
) -> Stf:
    r"""
    Create an `Stf` representing a hyperbolic tangent ramp.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    center_time : float or Tensor, optional
        The time at which the ramp has its greatest slope, :math:`t_0`.
        It must either be a scalar or contain a single element.
    ramp_duration : float or Tensor, optional
        The characteristic time for the hyperbolic tangent ramp, :math:`t_\mathrm{ramp}`.
        It must either be a scalar or contain a single element.
    end_value : float or complex or Tensor
        The asymptotic value of the ramp towards :math:`t \to +\infty`, :math:`a_+`.
        It must either be a scalar or contain a single element.
    start_value : float or complex or Tensor, optional
        The asymptotic value of the ramp towards :math:`t \to -\infty`, :math:`a_-`.
        If passed, it must either be a scalar or contain a single element.
        Defaults to minus `end_value`.

    Returns
    -------
    Stf
        The sampleable hyperbolic tangent ramp.

    See Also
    --------
    :func:`.pulses.linear_ramp_stf` : Create an `Stf` representing a linear ramp.
    :func:`.pulses.tanh_ramp_pwc` : Corresponding operation with `Pwc` output.
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

    With the default value of `start_value` (:math:`a_-`),
    the ramp expression simplifies to

    .. math:: \mathop{\mathrm{Tanh}}(t)
        = A \tanh\left( \frac{t - t_0}{t_\mathrm{ramp}} \right) \; ,

    where :math:`A = a_+` is the end value (the start value is then :math:`-A`).

    Examples
    --------
    Define a simple sampleable hyperbolic tangent ramp.

    >>> tanh = graph.pulses.tanh_ramp_stf(
    ...     center_time=0.4, ramp_duration=0.2, end_value=2, start_value=-1
    ... )
    >>> tanh
    <Stf: operation_name="add", value_shape=(), batch_shape=()>
    >>> graph.sample_stf(stf=tanh, sample_times=np.linspace(0, 1, 7), name="tanh_samples")
    <Tensor: name="tanh_samples", operation_name="sample_stf", shape=(7,)>
    >>> graph.discretize_stf(tanh, duration=1, segment_count=100, name="discretized_tanh")
    <Pwc: name="discretized_tanh", operation_name="discretize_stf", value_shape=(), batch_shape=()>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["tanh_samples", "discretized_tanh"]
    ... )
    >>> result.output["tanh_samples"]["value"]
    array([-0.946, -0.735,  0.018,  1.193,  1.805,  1.961,  1.993])

    Define a hyperbolic tangent ramp with optimizable parameters.

    >>> center_time = graph.optimization_variable(
    ...     count=1, lower_bound=0.25e-6, upper_bound=0.75e-6, name="center_time"
    ... )
    >>> ramp_duration = graph.optimization_variable(
    ...     count=1, lower_bound=0.1e-6, upper_bound=0.3e-6, name="ramp_duration"
    ... )
    >>> end_value = graph.optimization_variable(
    ...     count=1, lower_bound=0, upper_bound=3e6, name="end_value"
    ... )
    >>> graph.pulses.tanh_ramp_stf(
    ...     center_time=center_time, ramp_duration=ramp_duration, end_value=end_value
    ... )
     <Stf: operation_name="add", value_shape=(), batch_shape=()>
    """

    if start_value is None:
        start_value = -end_value

    center_time = validate_optimizable_parameter(graph, center_time, "center time")
    ramp_duration = validate_optimizable_parameter(
        graph, ramp_duration, "ramp duration"
    )
    end_value = validate_optimizable_parameter(graph, end_value, "end value")
    start_value = validate_optimizable_parameter(graph, start_value, "start value")

    return start_value + 0.5 * (end_value - start_value) * (
        1 + graph.tanh((graph.identity_stf() - center_time) / ramp_duration)
    )
