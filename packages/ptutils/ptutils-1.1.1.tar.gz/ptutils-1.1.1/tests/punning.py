#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.punning`.
"""
# =======================================================================================================================
# imports
# =======================================================================================================================
from typing import Any
import pytest
import math
from ptutils.encoding import HAVE_YAML
from ptutils.punning import (
    to_string,
    boolify,
    listify,
    as_numeric,
    as_encoded,
    as_literal,
    canonize,
    maybe_coerce_none,
    maybe_canonize,
    canonize_dict
)
from ptutils.undefined import UNDEFINED


# =======================================================================================================================
# Class: C
# =======================================================================================================================
class C:
    pass


c = C()


# =======================================================================================================================
# Test case data
# =======================================================================================================================
TO_STRING_TEST_CASES = [
    (b"hello", "hello"),
    ("hello", "hello"),
    (5, "5"),
    (None, "None"),
    (False, "False"),
    (True, "True"),
    ([True, 1], "[True, 1]"),
    (list(), "[]"),
    ({"a": True, "b": 1}, "{'a': True, 'b': 1}"),
    (dict(), "{}"),
    (c, str(c))
]

# -----------------------------------------------------------------------------------------------------------------------
BOOLIFY_TEST_CASES = [
    # normal cases
    (False, False),
    (True, True),
    (None, False),
    (UNDEFINED, False),
    ("yes", True),
    ("on", True),
    ("enabled", True),
    ("true", True),
    ("YES", True),
    ("ON", True),
    ("EnAbLeD", True),
    ("trUE", True),
    ("1", True),
    ("no", False),
    ("disabled", False),
    ("off", False),
    ("false", False),
    ("0", False),
    # error cases
    (b"hello", TypeError),
    ("hello", TypeError),
    (5, TypeError),
    ([True, 1], TypeError),
    (list(), TypeError),
    ({"a": True, "b": 1}, TypeError),
    (dict(), TypeError),
]

# -----------------------------------------------------------------------------------------------------------------------
LISTIFY_TEST_CASES = [
    (None,               False, [None]),
    ("a",                False, ["a"]),
    (1,                  False, [1]),
    (1.5,                False, [1.5]),
    (False,              False, [False]),
    (c,                  False, [c]),
    ({'a': 1, 'b': 'B'}, False, [{'a': 1, 'b': 'B'}]),
    ([1, 2, 3],          False, [1, 2, 3]),
    (set([1, 2, 3]),     False, set([1, 2, 3])),
    (tuple([1, 2, 3]),   False, tuple([1, 2, 3])),
    (None,               True, [None]),
    ("a",                True, ["a"]),
    (1,                  True, [1]),
    (1.5,                True, [1.5]),
    (False,              True, [False]),
    (c,                  True, [c]),
    ({'a': 1, 'b': 'B'}, True, [{'a': 1, 'b': 'B'}]),
    ([1, 2, 3],          True, [1, 2, 3]),
    (set([1, 2, 3]),     True, [1, 2, 3]),
    (tuple([1, 2, 3]),   True, [1, 2, 3])
]

# -----------------------------------------------------------------------------------------------------------------------
CANONIZE_TEST_CASES = [
    (None,                    False, None),
    ("a",                     False, "a"),
    (1,                       False, 1),
    (1.5,                     False, 1.5),
    (False,                   False, False),
    (c,                       False, c),
    ({'a': 1, 'b': 'B'},      False, {'a': 1, 'b': 'B'}),
    ([1, 2, 3],               False, [1, 2, 3]),
    (set([1, 2, 3]),          False, {1, 2, 3}),
    (tuple([1, 2, 3]),        False, tuple([1, 2, 3])),
    ("None",                  False, None),
    ("null",                  False, None),
    ("'None'",                False, None),
    ("'null'",                False, None),
    ('"a"',                   False, "a"),
    ("1",                     False, 1),
    ("1.5",                   False, 1.5),
    ("False",                 False, False),
    ('{"a": 1, "b": "B"}',    False, {'a': 1, 'b': 'B'}),
    ("[1, 2, 3]",             False, [1, 2, 3]),
    ("---\n",                 True, None),
    ("---\n- 1\n- 2\n- 3",    True, [1, 2, 3]),
    ("---\na: 1\nb: 2\nc: 3", True, {'a': 1, 'b': 2, 'c': 3}),
    ("this shouldn't parse",  False, "this shouldn't parse"),
    (b'{"a": 1, "b": "B"}',   False, {'a': 1, 'b': 'B'}),
    (b'true',                 False, True),
    (b'fAlsE',                False, False),
    ("---\ninvalid yaml: : :- ::", True, "---\ninvalid yaml: : :- ::"),
]

# -----------------------------------------------------------------------------------------------------------------------
AS_NUMERIC_TEST_CASES = [
    (None,                    TypeError),
    ("a",                     ValueError),
    ("+inf",                  float("+inf")),
    ("-inf",                  float("-inf")),
    ("nan",                   float("nan")),
    (1,                       1),
    (1.5,                     1.5),
    ("1",                     1),
    ("1.5",                   1.5),
]


# =======================================================================================================================
# Test cases
# =======================================================================================================================
@pytest.mark.parametrize(
    argnames  = ["obj", "expected"],
    argvalues = TO_STRING_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in TO_STRING_TEST_CASES]
)
def test_to_string(obj, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            to_string(obj)
    else:
        assert to_string(obj) == expected


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "expected"],
    argvalues = BOOLIFY_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in BOOLIFY_TEST_CASES]
)
def test_boolify(obj, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            boolify(obj)
    else:
        assert boolify(obj) == expected


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "strict", "expected"],
    argvalues = LISTIFY_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in LISTIFY_TEST_CASES]
)
def test_listify(obj, strict, expected):
    assert listify(obj, strict=strict) == expected


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "expect_yaml", "expected"],
    argvalues = CANONIZE_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[2])}" for x in CANONIZE_TEST_CASES]
)
def test_canonize(obj, expect_yaml, expected):
    if expect_yaml and not HAVE_YAML:
        pytest.skip("YAML support unavailable on this platform")

    assert canonize(obj) == expected


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "expected"],
    argvalues = AS_NUMERIC_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in AS_NUMERIC_TEST_CASES]
)
def test_as_numeric(obj, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as _:
            as_numeric(obj)
    else:
        v = as_numeric(obj)
        if math.isnan(v):
            assert math.isnan(expected)

        elif math.isinf(v):
            assert math.isinf(expected)

        else:
            assert v == expected


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "expect_yaml", "expected"],
    argvalues = CANONIZE_TEST_CASES,
    ids       = [f"identity:{repr(x[0])}" for x in CANONIZE_TEST_CASES]
)
def test_maybe_canonize_returns_original_when_it_should(obj: Any, expect_yaml: bool, expected: Any) -> None:
    if expect_yaml and not HAVE_YAML:
        pytest.skip("YAML support unavailable on this platform")
    computed = maybe_canonize(obj, False)
    assert computed is obj, f"Method maybe_canonize produced {computed} instead of original value {obj}."


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "expect_yaml", "expected"],
    argvalues = CANONIZE_TEST_CASES,

)
def test_maybe_canonize_returns_canonized_value(obj: Any, expect_yaml: bool, expected: Any) -> None:
    if expect_yaml and not HAVE_YAML:
        pytest.skip("YAML support unavailable on this platform")
    computed = maybe_canonize(obj, True)
    assert expected == computed, f"Method maybe_canonize produced {computed} instead of expected value {expected}."


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["obj", "expect_yaml", "expected"],
    argvalues = CANONIZE_TEST_CASES,

)
def test_maybe_canonize_returns_original_value(obj: Any, expect_yaml: bool, expected: Any) -> None:
    if expect_yaml and not HAVE_YAML:
        pytest.skip("YAML support unavailable on this platform")
    computed = maybe_canonize(obj, False)
    error = f"Method maybe_canonize failed to return input when should_canonize was False for value {obj}."
    assert computed is obj, error


# -----------------------------------------------------------------------------------------------------------------------
def test_maybe_coerce_none_does_nothing_if_should_not():
    computed = maybe_coerce_none(v = False, should_coerce = False)
    assert computed is False, "Failed to return the original falsey value when should_coerce is False."


# -----------------------------------------------------------------------------------------------------------------------
def test_maybe_coerce_none_returns_none_when_it_should() -> None:
    for v in [0, None, False, "", [], {}]:
        computed = maybe_coerce_none(v = v, should_coerce = True)
        assert computed is None, f"Failed to return the None for falsey value ({v}) when should_coerce is False."


# -----------------------------------------------------------------------------------------------------------------------
def test_maybe_coerce_none_returns_original_when_not_falsey() -> None:
    for v in [1, object(), True, "sdafdsa", [ 1, 2, 3 ], { 'a': 1 }]:
        computed = maybe_coerce_none(v = v, should_coerce = True)
        assert computed is v, f"Failed to return original non-falsey value ({v}) when should_coerce is True."


# -----------------------------------------------------------------------------------------------------------------------
__CANONIZE_DICT_TEST_CASES__ = [
    (
        f"{case[0]}->{case[2]}",
        {  "val": case[0] },
        {  "val": case[2] },
    )
    for (index, case)
    in  enumerate( CANONIZE_TEST_CASES )
    if  ( ( not case[1] ) or HAVE_YAML )
]


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["value", "expected"],
    argvalues = map(lambda x: (x[1], x[2]), __CANONIZE_DICT_TEST_CASES__),
    ids       = map(lambda x: x[0], __CANONIZE_DICT_TEST_CASES__)
)
def test_canonize_dict( value: Any, expected: Any) -> None:
    assert canonize_dict(value) == expected, f"Failed to canonize dictionary {value} -> {expected}."
