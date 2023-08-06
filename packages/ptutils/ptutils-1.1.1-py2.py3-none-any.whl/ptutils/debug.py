#!/bin/false
# -*- coding: utf-8 -*-

""" Debugging utility functions. """

# ------------------------------------------------------------------------------------------------------------------------
# Import and pathing setup
# ------------------------------------------------------------------------------------------------------------------------
import traceback


# ------------------------------------------------------------------------------------------------------------------------
# Utility functions: debug
# ------------------------------------------------------------------------------------------------------------------------
def stacktrace() -> str:
    """
    Return a current stacktrace formatted as a string.

    Returns
    -------
    str
        The stack trace in standard python stacktrace format.
    """
    return ''.join(traceback.format_exc())
