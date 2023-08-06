#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.text`.
"""
import pytest
from ptutils.text import strip_quotes, strip_brackets, strip_line_ending, elide


STRIP_QUOTES_TEST_CASES = [
    (b"'''hello'''", b"'''hello'''"),
    ("'hello'", "hello"),
    ('"hello"', "hello"),
    ('4', "4"),
    ('"4', '"4'),
    ("'4", "'4"),
]


@pytest.mark.parametrize(
    argnames  = ["obj", "expected"],
    argvalues = STRIP_QUOTES_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in STRIP_QUOTES_TEST_CASES]
)
def test_strip_quotes(obj, expected):
    assert strip_quotes(obj) == expected


SQUARE_BRACKETS = [['[', ']']]
CURLY_BRACKETS  = [['{', '}']]
PAREN_BRACKETS  = [['(', ')']]
DEFAULT_BRACKETS = SQUARE_BRACKETS + CURLY_BRACKETS + PAREN_BRACKETS

STRIP_BRACKETS_TEST_CASES = [
    (b"[[hello]]", DEFAULT_BRACKETS, b"[[hello]]"),
    ("",             DEFAULT_BRACKETS,                  ""),
    ("[]",           DEFAULT_BRACKETS,                  ""),
    ("[",            DEFAULT_BRACKETS,                  "["),
    ("[[[hello]]]",  DEFAULT_BRACKETS,                  "hello"),
    ("{([hello])}",  DEFAULT_BRACKETS,                  "hello"),
    ("({[hello]})",  DEFAULT_BRACKETS,                  "hello"),
    ("([{hello}])",  DEFAULT_BRACKETS,                  "hello"),
    ("[hello]",      DEFAULT_BRACKETS,                  "hello"),
    ("{hello}",      DEFAULT_BRACKETS,                  "hello"),
    ("(hello)",      DEFAULT_BRACKETS,                  "hello"),
    ("hello",        DEFAULT_BRACKETS,                  "hello"),
    ("{hello}",      SQUARE_BRACKETS,                   "{hello}"),
    ("{hello}",      PAREN_BRACKETS,                    "{hello}"),
    ("{hello}",      SQUARE_BRACKETS + PAREN_BRACKETS,  "{hello}"),
    ("[hello]",      CURLY_BRACKETS,                    "[hello]"),
    ("[hello]",      PAREN_BRACKETS,                    "[hello]"),
    ("[hello]",      CURLY_BRACKETS + PAREN_BRACKETS,   "[hello]"),
    ("{([",          DEFAULT_BRACKETS,                  "{(["),
    ("({[",          DEFAULT_BRACKETS,                  "({["),
    ("([{",          DEFAULT_BRACKETS,                  "([{"),
]


@pytest.mark.parametrize(
    argnames  = ["obj", "brackets", "expected"],
    argvalues = STRIP_BRACKETS_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in STRIP_BRACKETS_TEST_CASES]
)
def test_strip_brackets(obj, brackets, expected):
    assert strip_brackets(obj, brackets=brackets) == expected


STRIP_LINE_ENDING_TEST_CASES = [
    ("abc\r\n\r\ndef\r\n", "abc\r\n\r\ndef"),
    ("abc\r\n\r\ndef",     "abc\r\n\r\ndef"),
    ("abc\r\n\r\ndef\r",   "abc\r\n\r\ndef"),
    ("abc\r\n\r\ndef\n",   "abc\r\n\r\ndef"),
    ("abc\r\n\r",          "abc"),
    ("\r\n\r",             ""),
    (b"abc\r\n\r\ndef\r\n", TypeError),
    (b"abc\r\n\r\ndef",     TypeError),
    (b"abc\r\n\r\ndef\r",   TypeError),
    (b"abc\r\n\r\ndef\n",   TypeError),
    (b"abc\r\n\r",          TypeError),
    (b"\r\n\r",             TypeError),
    (None,                  AttributeError)
]


@pytest.mark.parametrize(
    argnames  = ["obj", "expected"],
    argvalues = STRIP_LINE_ENDING_TEST_CASES,
    ids       = [f"{repr(x[0])}->{repr(x[1])}" for x in STRIP_LINE_ENDING_TEST_CASES]
)
def test_strip_line_ending(obj, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as e:
            strip_line_ending(obj)

        error = "Method failed to raise an exception."
        assert isinstance(e.value, Exception), error

        error = (
            f"Method raised a '{type(e.value).__name__}', "
            f"but '{expected.__name__}' was expected."
        )
        assert isinstance(e.value, expected), error

    else:
        assert strip_line_ending(obj) == expected


__STR_1 = "How do you do?"
__STR_2 = "ABCDEFGHI " * 10

ELIDE_TEST_CASES = [
    (__STR_1, 100, __STR_1),
    (__STR_1, 10,  "How do ..."),
    (__STR_1, 4,   " ..."),
    (__STR_1, 3,   Exception),
    (__STR_2, 100, __STR_2),
    (__STR_2, 10,  "ABCDEF ..."),
    (__STR_2, 4,   " ..."),
    (__STR_2, 3,   Exception)
]


@pytest.mark.parametrize(
    argnames  = [ "text", "width", "expected" ],
    argvalues = ELIDE_TEST_CASES,
    ids       = [ f"case-{i}" for i in range( len( ELIDE_TEST_CASES ) ) ]
)
def test_elide(text, width, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected) as e:
            _ = elide(text=text, width=width)

        error = "Method failed to raise an exception."
        assert isinstance(e.value, Exception), error

        error = (
            f"Method raised a '{type(e.value).__name__}', "
            f"but '{expected.__name__}' was expected."
        )
        assert isinstance(e.value, expected), error

    else:
        value = elide(text=text, width=width)
        error = (
            f"Eliding string '{text}' to width {width} should "
            f"produce '{expected}', but produced '{value}'."
        )
        assert value == expected, error
