#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.debug`."""

import re


def test_stacktrace():
    """ Test that the debug stacktrace function produces a proper stacktrace. """
    from ptutils.debug import stacktrace
    try:
        raise Exception("intentional exception")
    except:  # noqa: E722
        st = stacktrace()

    assert isinstance(st, str)

    st_lines = st.split('\n')
    assert len(st_lines) == 5
    assert st_lines[0]  == "Traceback (most recent call last):"
    assert re.match(r'^ +File "[^"]+", line \d+, in test_stacktrace$', st_lines[-4])
    assert re.match(r'^ +raise Exception\("intentional exception\"\)', st_lines[-3])
    assert st_lines[-2] == "Exception: intentional exception"
    assert st_lines[-1] == ""
