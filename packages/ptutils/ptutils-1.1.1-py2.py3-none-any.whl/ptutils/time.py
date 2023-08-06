#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides functions and classes for dealing with time and timing.
"""

import datetime
from typing import Optional


def now() -> datetime.datetime:
    """ Get current time as UTC datetime.

    Returns
    -------
    now: datetime.datetime:
        The current UTC date and time.

    """
    return datetime.datetime.utcnow()


def dt(start: datetime.datetime, end: Optional[datetime.datetime] = None) -> datetime.timedelta:
    """ Compute the elapsed time between a given start time and end time.

    Parameters
    ----------
    start: datetime.datetime
        The starting point in time.
    end: datetime.datetime, optional
        The ending point in time. If omitted, the current time will be used.


    Returns
    -------
    elapsed_time: datetime.timedelta:
        The elapsed time.

    """
    end = end if (end is not None) else now()
    return end - start


# Import protection
if __name__ == '__main__':
    raise Exception(
        "This module is not executable. To use it, add "
        "'from ptutils.time import ...' to your python "
        "source code. Refer to the API documentation for more "
        "information."
    )
