#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.introspection`.
"""

from ptutils.introspection import get_function, get_functions


def dummy():
    pass


def dummy_a():
    pass


def dummy_b():
    pass


def dummy_c():
    pass


def test_get_function():
    assert get_function('dummy', __name__) is dummy
    assert get_function('does_not_exist', __name__) is None


def test_get_functions():
    f = get_functions(
        regex    = r'^dummy_([a-z]+)$',
        expander = None,
        module   = __name__
    )
    assert f == {
        "dummy_a": dummy_a,
        "dummy_b": dummy_b,
        "dummy_c": dummy_c,
    }
    assert len(f) == 3
    assert set(f.keys()) == set(['dummy_a', 'dummy_b', 'dummy_c'])
    assert f['dummy_a'] is dummy_a
    assert f['dummy_b'] is dummy_b
    assert f['dummy_c'] is dummy_c


def test_get_functions_with_expander():
    f = get_functions(
        regex    = r'^dummy_([a-z]+)$',
        expander = r'\1',
        module   = __name__
    )
    assert f == {
        "a": dummy_a,
        "b": dummy_b,
        "c": dummy_c,
    }
    assert len(f) == 3
    assert set(f.keys()) == set(['a', 'b', 'c'])
    assert f['a'] is dummy_a
    assert f['b'] is dummy_b
    assert f['c'] is dummy_c
