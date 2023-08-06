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
System-agnostic convenient functions.
"""
import warnings
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import numpy as np
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_iterable,
    check_argument_positive_integer,
)
from scipy.linalg import fractional_matrix_power
from scipy.special import betaincinv

from qctrltoolkit.namespace import Namespace
from qctrltoolkit.toolkit_utils import expose


@expose(Namespace.UTILS)
def confidence_ellipse_matrix(
    hessian: np.ndarray,
    cost: float,
    measurement_count: int,
    confidence_fraction: float = 0.95,
):
    r"""
    Calculate a matrix that you can use to represent the confidence region
    of parameters that you estimated. Pass to this function the Hessian of
    the residual sum of squares with respect to the parameters, and use the
    output matrix to transform a hypersphere into a hyperellipse representing
    the confidence region. You can then plot this hyperellipse to visualize the
    confidence region using the `plot_confidence_ellipses` function from the
    Q-CTRL Visualizer package.

    Alternatively, you can apply a (2,2)-slice of the transformation matrix to
    a unit circle to visualize the confidence ellipse for a pair of estimated
    parameters.

    Parameters
    ----------
    hessian : np.ndarray
        The Hessian of the residual sum of squares cost with respect to the estimated parameters,
        :math:`H`.
        Must be a square matrix.
    cost : float
        The residual sum of squares of the measurements with respect to the actual measurements,
        :math:`C_\mathrm{RSS}`.
        Must be positive.
    measurement_count : int
        The number of measured data points, :math:`n`.
        Must be positive.
    confidence_fraction : float, optional
        The confidence fraction for the ellipse, :math:`\alpha`.
        If provided, must be between 0 and 1.
        Defaults to 0.95.

    Returns
    -------
    np.ndarray
        A :math:`(p, p)`-matrix which transforms a unit hypersphere in a p-dimensional
        space into a hyperellipse representing the confidence region for the
        confidence fraction :math:`\alpha`. Here :math:`p` is the dimension of the Hessian matrix.

    Notes
    -----
    From the Hessian matrix of the residual sum of squares with respect
    to the estimated parameters :math:`\{\lambda_i\}`,

    .. math::
        H_{ij} = \frac{\partial^2 C_\mathrm{RSS}}{\partial \lambda_i \partial \lambda_j} \; ,

    we can estimate the covariance matrix for the estimated parameters

    .. math::
        \Sigma = \left( \frac{n-p}{2 C_\mathrm{RSS}} H \right)^{-1}  \; .

    Finally, we can find a scaling factor :math:`z`, such that the matrix :math:`z \Sigma^{1/2}`
    transforms the coordinates of a unit hypersphere in a p-dimensional space into a
    hyperellipse representing the confidence region

    .. math::
        z = \sqrt{p F_{1-\alpha} \left( \frac{n-p}{2}, \frac{p}{2} \right)} \; ,

    where :math:`F_{1-\alpha}(a,b)` is the point of the `F-distribution
    <https://en.wikipedia.org/wiki/F-distribution>`_ where the probability in
    the tail is equal to :math:`F_{1-\alpha}(a,b)`.

    For more details, see the topic
    `Characterizing your hardware using system identification in Boulder Opal
    <https://docs.q-ctrl.com/boulder-opal/topics/characterizing-your-hardware-using-system-identification-in-boulder-opal>`_
    and `N. R. Draper and I. Guttman, The Statistician 44, 399 (1995)
    <https://doi.org/10.2307/2348711>`_.
    """

    parameter_count = hessian.shape[0]

    check_argument(
        hessian.shape == (parameter_count, parameter_count),
        "Hessian must be a square matrix.",
        {"hessian": hessian},
    )

    check_argument(cost > 0, "The cost must be positive.", {"cost": cost})

    check_argument_positive_integer(measurement_count, "measurement_count")

    check_argument(
        0 < confidence_fraction < 1,
        "The confidence fraction must be between 0 and 1.",
        {"confidence_fraction": confidence_fraction},
    )

    # Estimate covariance matrix from the Hessian.
    covariance_matrix = np.linalg.inv(
        0.5 * hessian * (measurement_count - parameter_count) / cost
    )

    # Calculate scaling factor for the confidence region.
    iibeta = betaincinv(
        (measurement_count - parameter_count) / 2,
        parameter_count / 2,
        1 - confidence_fraction,
    )
    inverse_cdf = (
        (measurement_count - parameter_count) / parameter_count * (1 / iibeta - 1)
    )
    scaling_factor = np.sqrt(parameter_count * inverse_cdf)

    # Calculate confidence region for the confidence fraction.
    return scaling_factor * fractional_matrix_power(covariance_matrix, 0.5)


@expose(Namespace.UTILS)
def pwc_arrays_to_pairs(
    durations: Union[float, np.ndarray], values: np.ndarray
) -> List[Dict[str, np.ndarray]]:
    r"""
    Create a list of dictionaries with "value" and "duration" keys representing
    a piecewise-constant function from arrays containing the durations and values.

    You can use this function to prepare a control to be plotted with the
    `plot_controls` function from the Q-CTRL Visualizer package.

    Parameters
    ----------
    durations : np.ndarray or float
        The durations of the PWC segments as a 1D array or as a float.
        If a single (float) value is passed, it is taken as the total duration of the PWC and
        all segments are assumed to have the same duration.
    values : np.ndarray
        The values of the PWC.

    Returns
    -------
    list[dict]
        A list of dictionaries (with "value" and "duration" keys) defining a PWC.

    See Also
    --------
    :func:`.utils.pwc_pairs_to_arrays` : Perform the inverse conversion.

    Examples
    --------
    >>> qctrl.utils.pwc_arrays_to_pairs(1.0, np.array([3,-2,4,1]))
    [
        {'duration': 0.25, 'value': 3},
        {'duration': 0.25, 'value': -2},
        {'duration': 0.25, 'value': 4},
        {'duration': 0.25, 'value': 1}
    ]

    Plot a control using the function plot_controls from the Q-CTRL Visualizer package.

    >>> plot_controls(
    ...     plt.figure(),
    ...     {"control": qctrl.utils.pwc_arrays_to_pairs(np.array([1,3,2]), np.array([-1,1,2]))},
    ... )
    """
    check_argument(
        np.all(durations > 0.0), "Durations must be positive.", {"durations": durations}
    )

    if isinstance(durations, np.ndarray):
        check_argument(
            np.ndim(durations) == 1,
            "Durations must be a float or 1D array.",
            {"durations": durations},
        )
        check_argument(
            values.shape[0] == len(durations),
            "Durations must be a float or a 1D array with the same length as values.",
            {"durations": durations, "values": values},
        )
    else:
        durations = np.repeat(durations / values.shape[0], values.shape[0])

    return [{"duration": d, "value": v} for d, v in zip(durations, values)]


@expose(Namespace.UTILS)
def pwc_pairs_to_arrays(pwc: List) -> Tuple[np.ndarray, np.ndarray, int]:
    r"""
    Extract arrays with the durations and values representing a piecewise-constant function
    from a list of dictionaries with "value" and "duration" keys.

    You can use this function to retrieve the durations and values of a PWC extracted from
    a Boulder Opal graph calculation.

    Parameters
    ----------
    pwc : list[...list[list[dict]]]
        A nested list of lists of ... of list of dictionaries.
        The outer lists represent batches.
        The dictionaries in the innermost list must have "value" and "duration" keys, defining a
        PWC.

    Returns
    -------
    np.ndarray
        The durations of the PWC.
    np.ndarray
        The values of the PWC.
    int
        The number of batch dimensions.

    See Also
    --------
    :func:`.utils.pwc_arrays_to_pairs` : Perform the inverse conversion.

    Examples
    --------
    >>> pwc_example = [
                 {'duration': 1.0, 'value': 3},
                 {'duration': 0.5, 'value': -2},
                 {'duration': 0.5, 'value': 4},
                 ]
    >>> qctrl.utils.pwc_pairs_to_arrays(pwc_example)
        (array([1., 0.5, 0.5]), array([3, -2, 4]), 0)

    >>> pwc_example = [
                [{'duration': 1.0, 'value': 3},
                 {'duration': 0.5, 'value': -2},
                 {'duration': 0.5, 'value': 4}],
                [{'duration': 1.0, 'value': 2},
                 {'duration': 0.5, 'value': 3},
                 {'duration': 0.5, 'value': -1}]
                 ]
    >>> qctrl.utils.pwc_pairs_to_arrays(pwc_example)
        (array([1., 0.5, 0.5]),
         array([[3, -2, 4],
                [2,  3, -1]]),
         1)

    Define a PWC from a graph calculation.

    >>> graph.pwc(*qctrl.utils.pwc_pairs_to_arrays(result.output['signal']))
        <Pwc: name="pwc_#1", operation_name="pwc", value_shape=(), batch_shape=(4, 3)>
    """

    def extract_batch(pwc_list):
        check_argument(
            isinstance(pwc_list, list),
            "Item in outer lists is not a list.",
            {"pwc": pwc},
        )

        _type = type(pwc_list[0])

        check_argument(
            all(isinstance(e, _type) for e in pwc_list),
            "Items in same batch dimension not of same type.",
            {"pwc": pwc},
        )

        if isinstance(pwc_list[0], list):
            _len = len(pwc_list[0])
            check_argument(
                all(len(e) == _len for e in pwc_list),
                "Lists in same batch dimension not of same length.",
                {"pwc": pwc},
            )

            # The batching goes one level deeper.
            res = [extract_batch(k) for k in pwc_list]
            return [d for d, _ in res], [v for _, v in res]

        # We've reached the PWC list of dictionaries.
        for pwc_dict in pwc_list:
            check_argument(
                isinstance(pwc_dict, dict),
                "Item in innermost list not a dictionary.",
                {"pwc": pwc},
            )
            check_argument(
                "duration" in pwc_dict.keys() and "value" in pwc_dict.keys(),
                "`duration` or `value` key missing in given PWC.",
                {"pwc": pwc},
            )

        return [s["duration"] for s in pwc_list], [s["value"] for s in pwc_list]

    durations, values = extract_batch(pwc)

    # Durations and values have the same shape due to the input structure.
    # Check that the number of segments for all the PWCs are the same and all batches in
    # the same batch dimension must have the same number of elements.
    # If either of these conditions is not the case the data type (np.dtype) of
    # durations and values will be an object.
    # Note that this test is still necessary as the argument (where pwc is some dictionary with
    # duration and value keys)
    #    [[pwc], [[pwc, pwc]]]
    # will pass the checks in extract_batch.
    with warnings.catch_warnings(record=True) as warning_records:
        durations = np.array(durations)

    check_argument(
        len(warning_records) == 0,
        "The number of segments of each batch element must be the same, "
        "and all batches in the same batch dimension must have the same number of elements.",
        {"pwc": pwc},
    )
    values = np.array(values)
    time_dimension = durations.ndim - 1

    durations = np.reshape(durations, [-1, durations.shape[-1]])

    check_argument(
        np.all(np.diff(durations, axis=0) == 0),
        "The durations of all batch elements must be the same.",
        {"pwc": pwc},
        extras={"durations": durations},
    )

    durations = durations[0]

    check_argument(
        np.all(durations > 0.0),
        "Durations must be positive.",
        {"pwc": pwc},
        extras={"durations": durations},
    )

    return durations, values, time_dimension


@expose(Namespace.UTILS)
def extract_filter_function_arrays(samples: List) -> Tuple[Optional[np.ndarray], ...]:
    """
    Convert the output samples of a filter function calculation into NumPy arrays.

    Each sample contains a frequency value and the corresponding inverse power,
    inverse power uncertainty, and frequency domain noise operator. The four returned
    NumPy arrays are the frequencies, inverse powers, inverse power uncertainties,
    and the frequency domain noise operators. If any of the values is None this function
    returns None rather than the corresponding NumPy array.

    Parameters
    ----------
    samples : list[qctrl.types.filter_function.Sample]
        The samples of a ``qctrl.functions.calculate_filter_function`` result.

    Returns
    -------
    np.ndarray or None
        The 1D NumPy array of frequencies.
        Returns None if any of the frequencies are None.
    np.ndarray or None
        The 1D NumPy array of inverse powers.
        Returns None if any of the inverse powers are None.
    np.ndarray or None
        The 1D NumPy array of inverse power uncertainties.
        Returns None if any of the inverse power uncertainties are None.
    np.ndarray or None
        The 3D NumPy array of frequency domain noise operators.
        Returns None if any of the frequency domain noise operators are None.

    See Also
    --------
    :func:`~qctrl.dynamic.namespaces.FunctionNamespace.calculate_filter_function` :
        Calculate a heuristic for robustness of the controls against noise.

    Examples
    --------
    >>> samples = [
            Sample(
                frequency=0.06283185307179587,
                inverse_power=2.469046857168369,
                inverse_power_uncertainty=0.0016463055859327047,
                frequency_domain_noise_operator=None,
            ),
            ...,
            Sample(
                frequency=6283185.307179586,
                inverse_power=0.004755084538721049,
                inverse_power_uncertainty=6.537825035071768e-05,
                frequency_domain_noise_operator=None,
            )
        ]

    >>> qctrl.utils.extract_filter_function_arrays(samples)
        (
            array([6.28318531e-02, ..., 6.28318531e+06]),
            array([2.46904686e+00, ..., 4.75508454e-03]),
            array([1.64630559e-03, ..., 6.53782504e-05]),
            None,
        )
    """
    check_argument_iterable(samples, "samples")
    check_argument(
        all(hasattr(sample, "frequency") for sample in samples),
        "Not every sample contains a frequency.",
        {"samples": samples},
    )
    check_argument(
        all(hasattr(sample, "inverse_power") for sample in samples),
        "Not every sample contains an inverse power.",
        {"samples": samples},
    )
    check_argument(
        all(hasattr(sample, "inverse_power_uncertainty") for sample in samples),
        "Not every sample contains an inverse power uncertainty.",
        {"samples": samples},
    )
    check_argument(
        all(hasattr(sample, "frequency_domain_noise_operator") for sample in samples),
        "Not every sample contains a frequency domain noise operator.",
        {"samples": samples},
    )

    frequencies = [sample.frequency for sample in samples]
    inverse_powers = [sample.inverse_power for sample in samples]
    inverse_power_uncertainties = [
        sample.inverse_power_uncertainty for sample in samples
    ]
    frequency_domain_noise_operators = [
        sample.frequency_domain_noise_operator for sample in samples
    ]

    def _array_or_none(output: List) -> Optional[np.ndarray]:
        return None if None in output else np.array(output)

    return (
        _array_or_none(frequencies),
        _array_or_none(inverse_powers),
        _array_or_none(inverse_power_uncertainties),
        _array_or_none(frequency_domain_noise_operators),
    )
