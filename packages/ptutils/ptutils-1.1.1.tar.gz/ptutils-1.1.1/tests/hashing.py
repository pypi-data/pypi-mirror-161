#!/bin/false
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.globbing`."""

# =======================================================================================================================
# imports
# =======================================================================================================================
from typing import Any
import pytest
from ptutils.hashing import md5hash


# =======================================================================================================================
# Test case data
# =======================================================================================================================
MD5_TEST_CASES = [
    ( "1", "c4ca4238a0b923820dcc509a6f75849b" ),
    ( "2", "c81e728d9d4c2f636f067f89cc14862c" ),
    ( "3", "eccbc87e4b5ce2fe28308fd9f2a7baf3" ),
    ( "4", "a87ff679a2f3e71d9181a67b7542122c" ),
    ( "5", "e4da3b7fbbce2345d7772b0674a318d5" ),
    ( "6", "1679091c5a880faf6fb5e6087eb1b2dc" ),
    ( "7", "8f14e45fceea167a5a36dedd4bea2543" ),
    ( "8", "c9f0f895fb98ab9159f51fd0297e236d" ),
    ( "9", "45c48cce2e2d7fbdea1afc51c7c6ad26" ),
    ( "10", "d3d9446802a44259755d38e6d163e820" ),
    ( "11", "6512bd43d9caa6e02c990b0a82652dca" ),
    ( "12", "c20ad4d76fe97759aa27a0c99bff6710" ),
    ( "13", "c51ce410c124a10e0db5e4b97fc2af39" ),
    ( "14", "aab3238922bcc25a6f606eb525ffdc56" ),
    ( "15", "9bf31c7ff062936a96d3c8bd1f8f2ff3" ),
    ( "16", "c74d97b01eae257e44aa9d5bade97baf" ),
    ( "17", "70efdf2ec9b086079795c442636b55fb" ),
    ( "18", "6f4922f45568161a8cdf4ad2299f6d23" ),
    ( "19", "1f0e3dad99908345f7439f8ffabdffc4" ),
    ( "20", "98f13708210194c475687be6106a3b84" ),
    ( "21", "3c59dc048e8850243be8079a5c74d079" ),
    ( "22", "b6d767d2f8ed5d21a44b0e5886680cb9" ),
    ( "23", "37693cfc748049e45d87b8c7d8b9aacd" ),
    ( "24", "1ff1de774005f8da13f42943881c655f" ),
    ( "25", "8e296a067a37563370ded05f5a3bf3ec" ),
    ( "26", "4e732ced3463d06de0ca9a15b6153677" ),
    ( "27", "02e74f10e0327ad868d138f2b4fdd6f0" ),
    ( "28", "33e75ff09dd601bbe69f351039152189" ),
    ( "29", "6ea9ab1baa0efb9e19094440c317e21b" ),
    ( "30", "34173cb38f07f89ddbebc2ac9128303f" ),
    ( None, "6adf97f83acf6453d4a6a4b1070f3754" )
]


# =======================================================================================================================
# Tests
# =======================================================================================================================
# -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = [ "value", "expected" ],
    argvalues = MD5_TEST_CASES,
    ids       = [ f"test_case_{i}" for i in range( len( MD5_TEST_CASES ) ) ]
)
def test_md5hash(
    value:    Any,
    expected: str
) -> None:
    if isinstance(expected, type) and issubclass(Exception, expected):
        with pytest.raises(expected) as e:
            _ = md5hash(value)

        error = (
            f"Method md5hash failed to raise and exception of the right "
            f"type: {type(e.value).__qualname__} instead of {expected.__qualname__}"
        )
        assert isinstance(e.value, expected), error
    else:
        computed = md5hash(value)

        error = (
            f"Method md5hash failed to return the expected value for input '{value}': "
            f"'{computed}' instead of '{expected}'"
        )
        assert computed == expected, error
