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
Pulse library functions.
"""
from typing import (
    Callable,
    Optional,
    Union,
)

import numpy as np
from qctrlcommons.preconditions import check_argument

from qctrltoolkit.namespace import Namespace
from qctrltoolkit.toolkit_utils import expose


@expose(Namespace.PULSES)
class Pulse:
    """
    A class that contains information about a pulse that can be discretized.

    You can use this class to create and store pulses that will be sent to
    third-party devices. The pulses created in this way are independent of
    Boulder Opal graphs and have a fixed time step between their segments.

    Parameters
    ----------
    function : Callable
        A function that returns the value of the pulse at each instant of time.
        It must be capable of accepting a NumPy array of times as an input
        parameters, in which case it should return the values of the function
        for all the times passed.
    duration : float
        The duration of the pulse.
    """

    def __init__(self, function: Callable, duration: float):
        check_argument(
            duration > 0, "The duration must be positive.", {"duration": duration}
        )

        self.duration = duration
        self._function = function

    def export_with_time_step(self, time_step: float) -> np.ndarray:
        """
        Return the values of the pulse sampled at a constant rate given by the
        time step provided.

        Parameters
        ----------
        time_step : float
            The interval when the pulse is to be sampled (that is, the duration
            of each segment of the discretized pulse). It must be positive and
            shorter than the total duration of the pulse.

        Warnings
        --------
        If the time step passed doesn't exactly divide the total duration of
        the pulse, this function will round the number of segments of the
        discretized output to the nearest number that is an integer multiple of
        the time step.

        Returns
        -------
        np.ndarray
            An array with the values of the pulse sampled at equal intervals.
            The value of the pulse in each segment corresponds to the value of
            the function at the center of that segment.
        """
        check_argument(
            time_step > 0, "The time step must be positive.", {"time_step": time_step}
        )
        check_argument(
            self.duration >= time_step,
            "The time step must not be longer than the duration of the pulse.",
            {"duration": self.duration, "time_step": time_step},
        )

        segment_count = int(np.round(self.duration / time_step))
        times = (np.arange(segment_count) + 0.5) * time_step

        return self._function(times)

    def export_with_sampling_rate(self, sampling_rate: float) -> np.ndarray:
        """
        Return the values of the pulse sampled at a constant rate given by the
        sampling rate provided.

        Parameters
        ----------
        sampling_rate : float
            The rate at which the pulse is sampled (that is, the inverse of the
            duration of each segment of the discretized pulse). It must be
            positive and larger than the inverse of the duration.

        Warnings
        --------
        If the inverse of the sampling rate passed doesn't exactly divide the
        total duration of the pulse, this function will round the number of
        segments of the discretized output to the nearest number that is an
        integer multiple of the inverse of the sampling rate.

        Returns
        -------
        np.ndarray
            An array with the values of the pulse sampled at equal intervals.
            The value of the pulse in each segment corresponds to the value of
            the function at the center of that segment.
        """
        check_argument(
            sampling_rate > 0,
            "The sampling rate must be positive.",
            {"sampling_rate": sampling_rate},
        )
        time_step = 1 / sampling_rate
        check_argument(
            self.duration >= time_step,
            "The inverse of the sampling rate must not be longer than the"
            " duration of the pulse.",
            {"duration": self.duration, "sampling_rate": sampling_rate},
            extras={"1/sampling_rate": time_step},
        )

        segment_count = int(np.round(self.duration / time_step))
        times = (np.arange(segment_count) + 0.5) * time_step

        return self._function(times)


@expose(Namespace.PULSES)
def square_pulse(
    duration: float,
    amplitude: Union[float, complex],
    start_time: float = 0.0,
    end_time: Optional[float] = None,
) -> Pulse:
    r"""
    Creates a Pulse object representing a square pulse.

    Parameters
    ----------
    duration : float
         The duration of the pulse.
    amplitude : float or complex
        The amplitude of the square pulse, :math:`A`.
    start_time : float, optional
        The start time of the square pulse, :math:`t_0`.
        Defaults to 0.
    end_time : float, optional
        The end time of the square pulse, :math:`t_1`.
        Must be greater than the start time.
        Defaults to the `duration`.

    Returns
    -------
    Pulse
        The square pulse.

    See Also
    --------
    :func:`.pulses.cosine_pulse` : Create a `Pulse` object representing a cosine pulse.
    :func:`.pulses.square_pulse_pwc` :
        Graph operation to create a `Pwc` representing a square pulse.

    Notes
    -----
    The square pulse is defined as

    .. math:: \mathop{\mathrm{Square}}(t) = A \theta(t-t_0) \theta(t_1-t) \; ,

    where :math:`\theta(t)` is the
    `Heaviside step function <https://en.wikipedia.org/wiki/Heaviside_step_function>`_.

    Examples
    --------
    Define a square pulse and discretize it.

    >>> pulse = qctrl.pulses.square_pulse(
    ...     duration=4.0, amplitude=2.5, start_time=1.0, end_time=3.0
    ... )
    >>> pulse.export_with_time_step(time_step=1.0)
    array([0. , 2.5, 2.5, 0. ])
    """
    if end_time is None:
        end_time = duration

    check_argument(
        end_time > start_time,
        "The end time must be greater than the start time.",
        {"start_time": start_time, "end_time": end_time},
    )

    return Pulse(
        function=lambda times: np.where(
            np.logical_and(times >= start_time, times <= end_time), amplitude, 0.0
        ),
        duration=duration,
    )


@expose(Namespace.PULSES)
def cosine_pulse(
    duration: float,
    amplitude: Union[float, complex],
    drag: Optional[float] = None,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    flat_duration: float = 0.0,
) -> Pulse:
    r"""
    Create a Pulse object representing a cosine pulse.

    Parameters
    ----------
    duration : float
         The duration of the pulse.
    amplitude : float or complex
        The amplitude of the pulse, :math:`A`.
    drag : float, optional
        The DRAG parameter, :math:`\beta`.
        Defaults to None, in which case there is no DRAG correction.
    start_time : float, optional
        The time at which the cosine pulse starts, :math:`t_\mathrm{start}`.
        Defaults to 0.
    end_time : float, optional
        The time at which the cosine pulse ends, :math:`t_\mathrm{end}`.
        Defaults to the `duration`.
    flat_duration : float, optional
        The amount of time that the pulse remains constant after the peak of
        the cosine, :math:`t_\mathrm{flat}`.
        If passed, it must be positive and less than the difference between
        `end_time` and `start_time`.
        Defaults to 0, in which case no constant part is added to the cosine pulse.

    Returns
    -------
    Pulse
        The cosine pulse.

    See Also
    --------
    :func:`.pulses.cosine_pulse_pwc` :
        Graph operation to create a `Pwc` representing a cosine pulse.
    :func:`.pulses.hann_series` :
        Create a `Pulse` object representing a sum of Hann window functions.
    :func:`.pulses.sinusoid` : Create a `Pulse` object representing a sinusoidal oscillation.
    :func:`.pulses.square_pulse` : Create a Pulse object representing a square pulse.

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
    Define a cosine pulse.

    >>> pulse = qctrl.pulses.cosine_pulse(duration=3.0, amplitude=1.0)
    >>> pulse.export_with_time_step(time_step=0.5)
    array([0.0669873+0.j, 0.5      +0.j, 0.9330127+0.j, 0.9330127+0.j,
           0.5      +0.j, 0.0669873+0.j])

    Define a flat-top cosine pulse with a DRAG correction.

    >>> pulse = qctrl.pulses.cosine_pulse(
    ...     duration=3.0, amplitude=1.0, drag=0.1, flat_duration=0.6
    ... )
    >>> pulse.export_with_sampling_rate(sampling_rate=2.0)
    array([0.10332333-0.07968668j, 0.69134172-0.12093555j,
           1.        +0.j        , 1.        +0.j        ,
           0.69134172+0.12093555j, 0.10332333+0.07968668j])
    """
    if drag is None:
        drag = 0.0

    if end_time is None:
        end_time = duration

    check_argument(
        end_time > start_time,
        "The end time must be greater than the start time.",
        {"start_time": start_time, "end_time": end_time},
    )
    check_argument(
        flat_duration <= (end_time - start_time),
        "The duration of the flat part of the pulse has to be smaller than or"
        " equal to the total duration of the pulse.",
        {
            "flat_duration": flat_duration,
            "start_time": start_time,
            "end_time": end_time,
        },
    )

    pulse_period = end_time - start_time - flat_duration

    flat_segment_start = start_time + 0.5 * pulse_period
    flat_segment_end = end_time - 0.5 * pulse_period

    angular_frequency = 2.0 * np.pi / pulse_period

    def _cosine_pulse(times: np.ndarray) -> np.ndarray:
        assert drag is not None  # make mypy happy
        shifted_times = np.where(
            times < flat_segment_start,
            times - flat_segment_start,
            times - flat_segment_end,
        )
        values = (0.5 * amplitude) * (
            1
            + np.cos(angular_frequency * shifted_times)
            + (angular_frequency * drag * 1j)
            * np.sin(angular_frequency * shifted_times)
        )

        # Make pulse flat for the duration of the "flat segment".
        flat_values = np.where(
            np.logical_and(times > flat_segment_start, times < flat_segment_end),
            amplitude,
            values,
        )

        # Make the pulse zero before its start and after its end.
        limited_values = np.where(
            np.logical_and(times > start_time, times < end_time), flat_values, 0
        )
        return limited_values

    return Pulse(function=_cosine_pulse, duration=duration)


@expose(Namespace.PULSES)
def sinusoid(
    duration: float,
    amplitude: Union[float, complex],
    angular_frequency: float,
    phase: float = 0.0,
) -> Pulse:
    r"""
    Create a Pulse object representing a sinusoidal oscillation.

    Parameters
    ----------
    duration : float
        The duration of the oscillation.
    amplitude : float or complex
        The amplitude of the oscillation, :math:`A`.
    angular_frequency : float
        The angular frequency of the oscillation, :math:`\omega`.
    phase : float, optional
        The phase of the oscillation, :math:`\phi`.
        Defaults to 0.

    Returns
    -------
    Pulse
        The sinusoidal oscillation.

    See Also
    --------
    :func:`.pulses.cosine_pulse` : Create a `Pulse` object representing a cosine pulse.
    :func:`.pulses.hann_series` :
        Create a `Pulse` object representing a sum of Hann window functions.
    :func:`.pulses.sinusoid_pwc` :
        Graph operation to create a `Pwc` representing a sinusoidal oscillation.
    :func:`.pulses.sinusoid_stf` :
        Graph operation to create a `Stf` representing a sinusoidal oscillation.

    Notes
    -----
    The sinusoid is defined as

    .. math:: \mathop{\mathrm{Sinusoid}}(t) = A \sin \left( \omega t + \phi \right) \;.

    Examples
    --------
    Define a sinusoidal oscillation.

    >>> pulse = qctrl.pulses.sinusoid(
    ...     duration=2.0,
    ...     amplitude=1.0,
    ...     angular_frequency=np.pi,
    ...     phase=np.pi/2.0,
    ... )
    >>> pulse.export_with_sampling_rate(sampling_rate=0.25)
    array([ 0.92387953,  0.38268343, -0.38268343, -0.92387953, -0.92387953,
       -0.38268343,  0.38268343,  0.92387953])
    """

    return Pulse(
        function=lambda times: amplitude * np.sin(angular_frequency * times + phase),
        duration=duration,
    )


@expose(Namespace.PULSES)
def hann_series(
    duration: float,
    coefficients: np.ndarray,
) -> Pulse:
    r"""
    Create a Pulse object representing a sum of Hann window functions.

    Parameters
    ----------
    duration : float
        The duration of the signal, :math:`T`.
    coefficients : np.ndarray
        The coefficients for the different Hann window functions, :math:`c_n`.
        It must be a 1D array.

    Returns
    -------
    Pulse
        The Hann window functions series.

    See Also
    --------
    :func:`.pulses.cosine_pulse` : Create a `Pulse` object representing a cosine pulse.
    :func:`.pulses.sinusoid` : Create a `Pulse` object representing a sinusoidal oscillation.
    :func:`.pulses.hann_series_pwc` :
        Graph operation to create a `Pwc` representing a sum of Hann window functions.
    :func:`.pulses.hann_series_stf` :
        Graph operation to create an `Stf` representing a sum of Hann window functions.

    Notes
    -----
    The series is defined as

    .. math:: \mathop{\mathrm{Hann}}(t)
        = \sum_{n=1}^N c_n \sin^2 \left( \frac{\pi n t}{T} \right) \;,

    where :math:`N` is the number of coefficients.

    Examples
    --------
    Define a simple Hann series.

    >>> pulse = graph.pulses.hann_series(
    ...     duration=5.0,
    ...     coefficients=np.array([0.5, 1, 0.25]),
    ... )
    >>> pulse.export_with_time_step(time_step=0.5)
    array([0.15925422, 1.00144425, 1.375     , 1.05757275, 0.78172879,
       0.78172879, 1.05757275, 1.375     , 1.00144425, 0.15925422])
    """

    check_argument(
        len(coefficients.shape) == 1,
        "The coefficients must be in a 1D array.",
        {"coefficients": coefficients},
        extras={"coefficients.shape": coefficients.shape},
    )

    nss = np.arange(1, coefficients.shape[0] + 1)

    return Pulse(
        function=lambda times: np.sum(
            coefficients * np.sin(np.pi * nss * times[:, None] / duration) ** 2, axis=1
        ),
        duration=duration,
    )
