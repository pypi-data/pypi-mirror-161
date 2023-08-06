#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.time`.
"""

import datetime
from ptutils.time import now, dt


def test_now():
    assert isinstance(now(), datetime.datetime)


def test_dt():
    t1 = now()
    t2 = now()
    d = dt(t1, t2)
    assert isinstance(d, datetime.timedelta)
    assert d.total_seconds() > 0

    d2 = dt(t1)
    assert isinstance(d2, datetime.timedelta)
    assert d2.total_seconds() > 0
