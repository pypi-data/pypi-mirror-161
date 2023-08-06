#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides functions and classes for reflection and introspection.
"""

# -----------------------------------------------------------------------------------------------------------------------
# Main imports
# -----------------------------------------------------------------------------------------------------------------------
import inspect
import re
import sys
from typing import Optional, Callable, Dict


# -----------------------------------------------------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------------------------------------------------
def get_function(name: str, module: str = '__main__') -> Optional[Callable]:
    """ Get the function named `name` from module names `module`.

    Parameters
    ----------
    name: str
        The name of the function.
    module: str, optional
        The name of the module in which to find the function `name`.

    Returns
    -------
    func: Callable, optional
        The function object if present, None otherwise.
    """
    for name_, function in inspect.getmembers(sys.modules[module]):
        if inspect.isfunction(function):
            if name_ == name:
                return function
    return None


# -----------------------------------------------------------------------------------------------------------------------
def get_functions(regex: str, expander: Optional[str] = None, module: str = '__main__') -> Dict[str, Callable]:
    """ Find all functions in a module with names matching the specified regular expression.
    Additionally, the dictionary keys may be modified by supplying an expander.

    Parameters
    ----------
    regex: str
        The regular expression with which to match function names.
    expander: str, optional
        A regular expression expansion string. When supplied, the function's key in the returned dictionary
        will be computed from the match object's expand() method.
    module: str, optional
        The name of the module in which to find the functions matching `regex`.

    Returns
    -------
    func: Callable, optional
        The function object if present, None otherwise.
    """
    rv = {}
    for name, function in inspect.getmembers(sys.modules[module]):
        if inspect.isfunction(function):
            m = re.match(regex, name)
            if m:
                if expander:
                    rv[m.expand(expander)] = function
                else:
                    rv[name] = function
    return rv
