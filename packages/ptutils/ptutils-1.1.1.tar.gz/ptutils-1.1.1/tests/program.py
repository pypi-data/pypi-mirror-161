#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.debug`."""

from ptutils.program import Program


def test_program():
    p = Program("echo hello")
    p.start()
    rc = p.wait()
    assert rc == 0
    assert p.stdout == "hello"
    assert p.stderr == ""
