#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.numerical`.
"""
import datetime
from typing import Optional
import pytest

from ptutils.numerical import (
    __NAN__,
    mean,
    median,
    mean_time,
    median_time,
    mean_duration,
    median_duration,
    closest,
    median_closest,
    mean_closest
)
from math import isnan


def _float_2_timedelta( x: float ) -> datetime.timedelta:
    delta = datetime.timedelta(seconds = x)
    return delta


__BASIS__ = datetime.datetime.utcnow()


def _float_2_datetime( x: float, basis: Optional[ datetime.datetime ] = None ) -> datetime.datetime:
    basis = basis or __BASIS__
    delta = _float_2_timedelta(x)
    rv    = basis + delta
    return rv


__SCALARS__ = dict(
    datetime = datetime.datetime.utcnow(),
    none     = None,
    list     = [],
    dict     = dict(),
    float    = 0.0,
    int      = 1
)
__SCALARS__["timedelta"] = datetime.datetime.utcnow() - __SCALARS__["datetime"]
__SCALAR_VALUES__ = list( __SCALARS__.values() )
__NUMERIC_VALUES__ = [
    __SCALARS__["timedelta"],
    __SCALARS__["datetime"],
    __SCALARS__["float"],
    __SCALARS__["int"]
]
print(f"__SCALARS__ -> {__SCALARS__}")
print(f"__NUMERIC_VALUES__ -> {__NUMERIC_VALUES__}")

__SEQ_0 = [1, 2, 3]
__SEQ_1 = [1, 2]
__SEQ_2 = [31, 0, 3, 5.2, 7]
__SEQ_3 = [17, 2.3, 12, -1.4, 3]
__SEQ_4 = [14, 7.3, 8, 56.4]

__NUMERIC_SEQUENCES__ = [
    # values, mean, median, mean_closest, median_closest
    (__SEQ_0, sum( __SEQ_0 ) / len( __SEQ_0 ), __SEQ_0[1],                          1, 1 ),
    (__SEQ_1, sum( __SEQ_1 ) / len( __SEQ_1 ), ( __SEQ_1[ 0 ] + __SEQ_1[ 1 ] ) / 2, 0, 0 ),
    (__SEQ_2, sum( __SEQ_2 ) / len( __SEQ_2 ), __SEQ_2[ 3 ],                        4, 3 ),
    (__SEQ_3, sum( __SEQ_3 ) / len( __SEQ_3 ), __SEQ_3[ 4 ],                        4, 4 ),
    (__SEQ_4, sum( __SEQ_4 ) / len( __SEQ_4 ), ( __SEQ_4[ 0 ] + __SEQ_4[ 2 ] ) / 2, 0, 0 )

    # ([1, 2, 3],                   2,    2, 0, 0 ),
    # ([1, 2],                    1.5,  1.5, 0, 0 ),
    # ([31, 0, 3, 5.2, 7],       9.24,  5.2, 4, 2 ),
    # ([17, 2.3, 12, -1.4, 3],   6.58,    3, 4, 4 ),
    # ([14, 7.3, 8, 56.4],     21.425,  7.6, 0, 1 )
]
__DATETIME_SEQUENCES__ = [
    (
        [ _float_2_datetime(x) for x in values ],
        _float_2_datetime(mean_value),
        _float_2_datetime(median_value),
        mean_closest_idx,
        median_closest_idx
    )
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx)
    in __NUMERIC_SEQUENCES__
]
__TIMEDELTA_SEQUENCES__ = [
    (
        [ _float_2_timedelta( x ) for x in values ],
        _float_2_timedelta( mean_value ),
        _float_2_timedelta( median_value ),
        mean_closest_idx,
        median_closest_idx
    )
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx)
    in __NUMERIC_SEQUENCES__
]
__SEQUENCES__ = __NUMERIC_SEQUENCES__ + __DATETIME_SEQUENCES__ + __TIMEDELTA_SEQUENCES__
__CLOSEST__ = [
    ( __SEQ_0,  1,    0 ),
    ( __SEQ_0,  2,    1 ),
    ( __SEQ_0,  3,    2 ),
    ( __SEQ_1,  1.5,  0 ),
    ( __SEQ_2,  2,    2 ),
    ( __SEQ_3, 11,    2 ),
    ( __SEQ_3,  2.64, 1 ),
    ( __SEQ_3,  2.65, 1 ),
    ( __SEQ_3,  2.66, 4 )
]


def test_nan():
    assert isnan(__NAN__)


def test_closest_matches_expected_value():
    for values, value, expectation in __CLOSEST__:
        computed    = closest( value, values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = (
            f"The closest value to {value} in {values} should be "
            f"values[{expectation}]={values[expectation]}, but was "
            f"values[{computed}]={values[computed]}."
        )
        assert computed is expectation, error


def test_mean_of_empty_sequence_raises():
    with pytest.raises(Exception) as e:
        _ = mean( [] )

    error = "Attempting to compute mean of empty sequence should raise an exception but did not."
    assert isinstance(e.value, Exception), error


def test_mean_of_sequence_with_one_value_returns_that_same_value():
    for value in __SCALAR_VALUES__:
        values = [ value ]
        computed = mean( values )
        expectation = value
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Mean of {values} should be {expectation}, but was {computed}."
        assert computed is expectation, error


def test_mean_of_repeated_values_is_equal_to_that_value():
    for count in range( 2, 10 ):
        for value in __NUMERIC_VALUES__:
            values      = [ value ] * count
            expectation = value
            computed    = mean( values )
            print(f"input       -> {values}")
            print(f"expectation -> {expectation}")
            print(f"computed    -> {computed}")
            error = f"Mean of list of repeated values [{value}]*{count} should be {expectation}, but was {computed}."
            assert computed == expectation, error


def test_mean_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __SEQUENCES__:
        expectation = mean_value
        computed    = mean( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Mean of list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_mean_duration_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __TIMEDELTA_SEQUENCES__:
        expectation = mean_value
        computed    = mean_duration( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Mean of duration list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_mean_time_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __DATETIME_SEQUENCES__:
        expectation = mean_value
        computed    = mean_time( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Mean of datetime list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_mean_closest_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __SEQUENCES__:
        expectation = mean_closest_idx
        computed    = mean_closest( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Mean closest of list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_median_of_empty_sequence_raises():
    with pytest.raises(Exception) as e:
        _ = median( [] )

    error = "Attempting to compute median of empty sequence should raise an exception but did not."
    assert isinstance(e.value, Exception), error


def test_median_of_sequence_with_one_value_returns_that_same_value():
    for value in __SCALAR_VALUES__:
        values = [ value ]
        computed = median( values )
        expectation = value
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Median of {values} should be {expectation}, but was {computed}."
        assert computed is expectation, error


def test_median_of_repeated_values_is_equal_to_that_value():
    for count in range( 2, 10 ):
        for value in __NUMERIC_VALUES__:
            values      = [ value ] * count
            expectation = value
            computed    = median( values )
            print(f"input       -> {values}")
            print(f"expectation -> {expectation}")
            print(f"computed    -> {computed}")
            error = f"Median of list of repeated values [{value}]*{count} should be {expectation}, but was {computed}."
            assert computed == expectation, error


def test_median_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __SEQUENCES__:
        expectation = median_value
        computed    = median( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Median of list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_median_closest_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __SEQUENCES__:
        expectation = median_closest_idx
        computed    = median_closest( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Median closest of list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_median_duration_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __TIMEDELTA_SEQUENCES__:
        expectation = median_value
        computed    = median_duration( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Median of duration list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error


def test_median_time_matches_expected_value():
    for (values, mean_value, median_value, mean_closest_idx, median_closest_idx) in __DATETIME_SEQUENCES__:
        expectation = median_value
        computed    = median_time( values )
        print(f"input       -> {values}")
        print(f"expectation -> {expectation}")
        print(f"computed    -> {computed}")
        error = f"Median of datetime list {values}] should be {expectation}, but was {computed}."
        assert computed == expectation, error
