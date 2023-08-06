#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides boilerplate hashing functionality based on python hashlib functions.
"""
from typing import Any
import hashlib
from ptutils.punning import to_string


def md5hash( x: Any ) -> str:
    """
    Return the MD5 hash of a string (or an object converted to a string).

    Parameters
    ----------
    obj : Any
        A string or bytes object, or a string-convertible object.

    Returns
    -------
    str
        The computed MD5 hash.
    """
    return hashlib.md5(to_string(x).encode('utf-8')).hexdigest()
