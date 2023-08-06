#!/bin/false
# -*- coding: utf-8 -*-


""" Numerical utilities. """

import datetime
from typing import Any, Callable, Union, Optional, Iterable


# =======================================================================================================================
# Globals: Numerical constants
# =======================================================================================================================
__NAN__ = float('nan')

# =======================================================================================================================
# Typehints
# =======================================================================================================================
Numeric            = Union[int, float, datetime.datetime, datetime.timedelta]
SequenceOfNumerics = Union[Iterable[int], Iterable[float], Iterable[datetime.datetime], Iterable[datetime.timedelta]]


# =======================================================================================================================
# Helper functions: math
# =======================================================================================================================
def mean_time( times: Iterable[datetime.datetime] ) -> datetime.datetime:
    """
    Compute the mean timepoint of a sequence of timepoints.

    Parameters
    ----------
    times : Iterable[datetime.datetime]
        An iterable sequence of timepoints.

    Returns
    -------
    datetime.datetime
        The mean value of all provided timepoints in `times`.

    Raises
    ------
    Exception
        When no timepoints are provided or provided values are not compatible with `datetime.datetime` compare and
        subtract.
    """

    N = len(times)
    if N == 0:
        raise Exception("Can't compute mean time when no times are provided.")
    if N == 1:
        return times[0]
    earliest = min(times)
    elapsed  = [
        ( time - earliest ).total_seconds()
        for time
        in  times
    ]
    mean_elapsed = sum(elapsed) / N
    mean_start   = earliest + datetime.timedelta( seconds = mean_elapsed )
    return mean_start


# -----------------------------------------------------------------------------------------------------------------------
def mean_duration( durations: Iterable[datetime.timedelta] ) -> datetime.timedelta:
    """
    Compute the mean duration of a sequence of durations.

    Parameters
    ----------
    durations : Iterable[datetime.datetime]
        An iterable sequence of durations.

    Returns
    -------
    datetime.datetime
        The mean value of all provided durations in `durations`.

    Raises
    ------
    Exception
        When no timepoints are provided, when any of the provided durations do not behave as `datetime.timedelta` would.
    """

    mu = mean([x.total_seconds() for x in durations])
    if mu is None:
        return mu
    return datetime.timedelta(
        seconds = mu
    )


# -----------------------------------------------------------------------------------------------------------------------
def mean(values: SequenceOfNumerics ) -> Numeric:
    """
    Compute the mean value of a list of values.

    Parameters
    ----------
    values : SequenceOfNumerics
        A list of values, all of the same numeric type.

    Returns
    -------
    Numeric
        The mean value.

    Raises
    ------
    Exception
        When no values are provided. For `datetime.datetime` and `datetime.timedelta`, the same conditions apply
        as with `mean_time` and `mean_duration`, respectively.
    """

    N = len(values)
    if N == 0:
        raise Exception("Can't compute mean when no values are provided.")
    if N == 1:
        return values[0]
    if isinstance(values[0], datetime.datetime):
        return mean_time(values)
    elif isinstance(values[0], datetime.timedelta):
        return mean_duration(values)
    else:
        return sum(values) / N


# -----------------------------------------------------------------------------------------------------------------------
def median_time( times: Iterable[datetime.datetime] ) -> datetime.datetime:
    """
    Compute the median timepoint of a sequence of timepoints.

    Parameters
    ----------
    times : Iterable[datetime.datetime]
        An iterable sequence of timepoints.

    Returns
    -------
    datetime.datetime
        The median value of all provided timepoints in `times`.

    Raises
    ------
    Exception
        When no timepoints are provided or provided values are not compatible with `datetime.datetime` compare and
        subtract.
    """

    N = len(times)
    if N == 0:
        raise Exception("Can't compute median time when no times are provided.")
    if N == 1:
        return times[0]
    earliest = min(times)
    elapsed  = [
        ( time - earliest ).total_seconds()
        for time
        in  times
    ]
    median_elapsed = median(elapsed)
    median_start   = earliest + datetime.timedelta( seconds = median_elapsed )
    return median_start


# -----------------------------------------------------------------------------------------------------------------------
def median_duration( durations: Iterable[datetime.timedelta] ) -> datetime.timedelta:
    """
    Compute the median duration of a sequence of durations.

    Parameters
    ----------
    durations : Iterable[datetime.datetime]
        An iterable sequence of durations.

    Returns
    -------
    datetime.datetime
        The median value of all provided durations in `durations`.

    Raises
    ------
    Exception
        When no timepoints are provided, when any of the provided durations do not behave as `datetime.timedelta` would.
    """

    mu = median([x.total_seconds() for x in durations])
    if mu is None:
        return mu
    return datetime.timedelta(
        seconds = mu
    )


# -----------------------------------------------------------------------------------------------------------------------
def median( values: SequenceOfNumerics ) -> Numeric:
    """
    Compute the median value of a list of values.

    Parameters
    ----------
    values : SequenceOfNumerics
        A list of values, all of the same numeric type.

    Returns
    -------
    Numeric
        The median value.

    Raises
    ------
    Exception
        When no values are provided. For `datetime.datetime` and `datetime.timedelta`, the same conditions apply
        as with `median_time` and `median_duration`, respectively.
    """
    N = len(values)
    if N == 0:
        raise Exception("Can't compute median when no values are provided.")
    if N == 1:
        return values[0]
    if isinstance(values[0], datetime.datetime):
        return median_time(values)
    elif isinstance(values[0], datetime.timedelta):
        return median_duration(values)
    else:
        values_ = list(sorted(values))
        if ( N % 2 ) == 0:
            return ( values_[ ( N // 2 ) - 1] + values_[ N // 2 ] ) / 2
        else:
            return values_[ ( N // 2 ) ]


# -----------------------------------------------------------------------------------------------------------------------
def closest(
    value:    Any,
    values:   Iterable[Any],
    distance: Optional[ Callable[ [ Any, Any ], float ] ] = None
) -> int:
    """
    Find the index of the closest-matching value in a list.
    Note: if multiple elements in the sequence have the same distance, the first such element's index will be returned.


    Parameters
    ----------
    value : Any
        The reference value
    values : Iterable[Any]
        An iterable sequence of values.
    distance : Optional[Callable[[Any,Any],float]], optional
        A function which computes the distance between a value in `values` and `value`, by default None. When omitted,
        subtraction will be used to compute the distance, and this must return a float or integer.

    Returns
    -------
    int
        The index of the closest-matching element.
    """

    distance = distance if distance is not None else lambda a, b: a - b
    return min( enumerate(values), key=lambda x: abs( distance( x[1], value ) ) )[ 0 ]


# -----------------------------------------------------------------------------------------------------------------------
def median_closest(
    values:   Iterable[ Any ],
    distance: Optional[ Callable[ [ Any, Any ], float ] ] = None
) -> int:
    """
    Find the index of the elemnt which closest-matching value to the median of all elements.

    Parameters
    ----------
    values : Iterable[Any]
        A list of numeric values
    distance : Optional[Callable[[Any,Any],float]], optional
        A function which computes the distance between two values in `values`, by default None. When omitted,
        subtraction will be used to compute the distance, and this must return a float or integer.

    Returns
    -------
    int
        The index of the closest-matching element.
    """

    return closest(median(values), values, distance=distance)


# -----------------------------------------------------------------------------------------------------------------------
def mean_closest(
    values:   Iterable[ Any ],
    distance: Optional[ Callable[ [ Any, Any ], float ] ] = None
) -> int:
    """
    Find the index of the elemnt which closest-matching value to the mean of all elements.

    Parameters
    ----------
    values : Iterable[Any]
        A list of numeric values
    distance : Optional[Callable[[Any,Any],float]], optional
        A function which computes the distance between two values in `values`, by default None. When omitted,
        subtraction will be used to compute the distance, and this must return a float or integer.

    Returns
    -------
    int
        The index of the closest-matching element.
    """

    return closest(mean(values), values, distance=distance)
