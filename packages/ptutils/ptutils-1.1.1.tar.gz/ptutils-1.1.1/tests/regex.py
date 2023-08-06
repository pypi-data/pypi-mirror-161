#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.regex`.
"""
# =======================================================================================================================
# imports
# =======================================================================================================================
from typing import Any
import pytest, re
from ptutils.regex import match_one_of, regex_to_string, Pattern


# =======================================================================================================================
# Tes case data
# =======================================================================================================================
__REGEX_EMPTY__      = r"^$"
__REGEX_WHITESPACE__ = r"^\s+$"
__REGEX_NUMBER__     = r"^[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$"
__REGEX_HELLO__      = r"^hello$"
__REGEX_VARIABLE__   = r"^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*$"
__ALL_REGEXES__      = [__REGEX_EMPTY__, __REGEX_WHITESPACE__, __REGEX_NUMBER__, __REGEX_HELLO__, __REGEX_VARIABLE__]
__CASES__ = [
    ("-----",      [False, False, False, False, False]),
    ("hello",      [False, False, False, True,  True]),
    ("hello.bob",  [False, False, False, False, True]),
    ("hello.3bob", [False, False, False, False, False]),
    ("-3.4",       [False, False, True,  False, False]),
    ("+3.4",       [False, False, True,  False, False]),
    ("+3",         [False, False, True,  False, False]),
    ("7.2.6",      [False, False, False, False, False]),
    ("",           [True,  False, False, False, False]),
    ("\n \t",      [False, True,  False, False, False]),
    ("1e-16",      [False, False, True,  False, False])
]
REGEX_TO_STRING_CASES = dict(
    precompiled_pattern      = (re.compile(r".*"), False, False, ".*"),
    uncompiled_pattern       = (r".*",             False, False, ".*"),
    coerced_pattern          = (b".*",             False, True,  ".*"),
    compiled_pattern         = (r".*",             True,  False, ".*"),
    coerced_compiled_pattern = (b".*",             True,  True,  ".*"),
    bad_pattern              = (b"[){",            True,  True,  Exception),
)


# =======================================================================================================================
# helper functions
# =======================================================================================================================
def equal_patterns(r1, r2):
    if (r1 is None) and (r2 is None):
        return True

    if (r1 is None) or (r2 is None):
        return False

    return (r1 is r2) or (re.compile(r1).pattern == re.compile(r2).pattern)


def equal_matches(m1, m2):
    if (m1 is None) and (m2 is None):
        return True

    if (m1 is None) or (m2 is None):
        return False

    return (m1 is m2) or (
        (m1.group(0) == m2.group(0)) and
        (m1.groupdict() == m2.groupdict())
    )


# =======================================================================================================================
# Test cases
# =======================================================================================================================
@pytest.mark.parametrize(
    argnames  = [ "text", "matches" ],
    argvalues = __CASES__,
    ids       = [ f"case{i}" for ( i, _ ) in enumerate(__CASES__) ]
)
def test_match_one_of_re_equivalency(text, matches):
    for r in __ALL_REGEXES__:
        assert equal_matches(
            re.match(r, text),
            match_one_of([r], text)
        )


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = [ "text", "matches" ],
    argvalues = __CASES__,
    ids       = [ f"case{i}" for ( i, _ ) in enumerate(__CASES__) ]
)
def test_match_one_of(text, matches):
    patterns = __ALL_REGEXES__
    if any(matches):
        matching_regex_idx = matches.index(True)
        matching_regex_raw = patterns[matching_regex_idx]
        matching_regex     = re.compile(matching_regex_raw)
        expected_value     = re.match(matching_regex, text)

        # test with returning the regex
        (computed_regex, computed_value) = match_one_of(
            patterns          = patterns,
            text              = text,
            return_pattern    = True,
            raise_on_no_match = False
        )

        error = (
            f"Failed to match string '{text}' against pattern "
            f"'{matching_regex.pattern}' as expected."
        )
        assert equal_matches(expected_value, computed_value), error

        error = (
            f"Failed to match string '{text}' against the pattern "
            f"'{matching_regex.pattern}' as expected."
        )
        assert equal_patterns(matching_regex, computed_regex), error

        # test without returning the regex
        computed_value = match_one_of(patterns=patterns, text=text, return_pattern=False, raise_on_no_match=False)

        error = (
            f"Failed to match string '{text}' against pattern "
            f"'{matching_regex.pattern}' as expected."
        )
        assert equal_matches(expected_value, computed_value), error

    else:
        with pytest.raises(Exception) as e:
            _ = match_one_of(patterns=patterns, text=text, return_pattern=False, raise_on_no_match=True)

        error = (
            "Failed to raise exception when raise_on_no_match=True and "
            "presented with text matching none of supplied patterns."
        )
        assert isinstance(e.value, Exception), error

        # test without returning the regex
        computed_value = match_one_of(patterns=patterns, text=text, return_pattern=False, raise_on_no_match=False)
        error = (
            "Failed to return None when raise_on_no_match=False and "
            "presented with text matching none of supplied patterns."
        )
        assert computed_value is None, error

        # test with returning the regex
        computed_value = match_one_of(patterns=patterns, text=text, return_pattern=True, raise_on_no_match=False)
        error = (
            "Failed to return (None, None) when raise_on_no_match=False "
            "and presented with text matching none of supplied patterns."
        )
        assert computed_value == (None, None), error


# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = [ "pattern", "auto_compile", "coerce_string", "expected" ],
    argvalues = REGEX_TO_STRING_CASES.values(),
    ids       = REGEX_TO_STRING_CASES.keys()
)
def test_regex_to_string(
    pattern:       Pattern,
    auto_compile:  bool,
    coerce_string: bool,
    expected:      Any
) -> None:
    if isinstance(expected, type) and issubclass(Exception, expected):
        with pytest.raises(expected) as e:
            _ = regex_to_string(
                pattern       = pattern,
                auto_compile  = auto_compile,
                coerce_string = coerce_string
            )

        error = (
            f"Method regex_to_string failed to raise and exception of the right "
            f"type: {type(e.value).__qualname__} instead of {expected.__qualname__}"
        )
        assert isinstance(e.value, expected), error
    else:
        computed = regex_to_string(
            pattern       = pattern,
            auto_compile  = auto_compile,
            coerce_string = coerce_string
        )

        error = (
            f"Method regex_to_string failed to return the expected value: "
            f"'{computed}' instead of {expected}"
        )
        assert computed == expected, error
