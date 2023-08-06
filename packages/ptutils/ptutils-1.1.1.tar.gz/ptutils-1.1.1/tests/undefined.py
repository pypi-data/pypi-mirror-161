#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.undefined`.
"""

from ptutils.undefined import is_defined, is_undefined, default_if_undefined, UNDEFINED, Undefined


def test_is_undefined():
    assert is_undefined(UNDEFINED)
    assert is_undefined(Undefined)
    assert is_undefined(Undefined())
    assert not is_undefined(None)


def test_is_defined():
    assert is_defined(None)
    assert not is_defined(UNDEFINED)
    assert not is_defined(Undefined)
    assert not is_defined(Undefined())


def test_default_if_undefined():
    assert default_if_undefined(UNDEFINED, 123) == 123
    assert default_if_undefined(None, 123) is None


def test_undefined_evaluates_as_false():
    assert bool(UNDEFINED) is False
    assert bool(Undefined) is False
    assert bool(Undefined()) is False
