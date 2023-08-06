#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.typing`.
"""

import pytest
from ptutils.typing import is_iterable, is_sequence, is_string, is_mapping


TEST_CASES = [
    ("a",               False, True,  True,  False),
    (b"a",              False, False, True,  True ),
    (None,              False, False, False, False),
    ([None],            False, False, True,  True),
    (set([None]),       False, False, True,  True),
    (tuple([None]),     False, False, True,  True),
    (iter([None]),      False, False, True,  True),
    (dict(a='b'),       True,  False, True,  False),
]


@pytest.mark.parametrize(
    argnames  = ["obj", "obj_is_mapping", "obj_is_string", "obj_is_iterable", "obj_is_sequence"],
    argvalues = TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in TEST_CASES]
)
def test_is_mapping(obj, obj_is_mapping, obj_is_string, obj_is_iterable, obj_is_sequence):
    expected = obj_is_mapping
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            is_mapping(obj)
    else:
        assert is_mapping(obj) == expected


@pytest.mark.parametrize(
    argnames  = ["obj", "obj_is_mapping", "obj_is_string", "obj_is_iterable", "obj_is_sequence"],
    argvalues = TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[2])}" for x in TEST_CASES]
)
def test_is_string(obj, obj_is_mapping, obj_is_string, obj_is_iterable, obj_is_sequence):
    expected = obj_is_string
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            is_string(obj)
    else:
        assert is_string(obj) == expected


@pytest.mark.parametrize(
    argnames  = ["obj", "obj_is_mapping", "obj_is_string", "obj_is_iterable", "obj_is_sequence"],
    argvalues = TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[3])}" for x in TEST_CASES]
)
def test_is_iterable(obj, obj_is_mapping, obj_is_string, obj_is_iterable, obj_is_sequence):
    expected = obj_is_iterable
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            is_iterable(obj)
    else:
        assert is_iterable(obj) == expected


@pytest.mark.parametrize(
    argnames  = ["obj", "obj_is_mapping", "obj_is_string", "obj_is_iterable", "obj_is_sequence"],
    argvalues = TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[3])}" for x in TEST_CASES]
)
def test_is_sequence(obj, obj_is_mapping, obj_is_string, obj_is_iterable, obj_is_sequence):
    expected = obj_is_sequence
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            is_sequence(obj)
    else:
        assert is_sequence(obj) == expected
