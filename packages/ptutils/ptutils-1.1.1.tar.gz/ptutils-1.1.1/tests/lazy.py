#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.lazy`.
"""

from ptutils.lazy import lazy_property


def test_lazy_property():
    marker = []

    def _inner():
        marker.append(0)
        return True

    assert len(marker) == 0

    class Klass:
        @lazy_property
        def prop(self):
            return _inner()

    c = Klass()
    assert isinstance(c, Klass)
    assert len(marker) == 0
    p = c.prop
    assert len(marker) == 1
    assert p is True
    assert marker == [0]
    p = c.prop
    assert len(marker) == 1
    assert p is True
    assert marker == [0]
