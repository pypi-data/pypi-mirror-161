#!/bin/false
# -*- coding: utf-8 -*-

""" Lazy-evaluation helpers. """


# =======================================================================================================================
# Main imports
# =======================================================================================================================
import functools
from typing import Callable


# =======================================================================================================================
# Utility decorators
# =======================================================================================================================
def lazy_property(method: Callable) -> property:
    """
    Decorator that makes a property lazy-evaluated.

    Parameters
    ----------
    method : Callable
        A method of a class to be decorated as a lazy property.

    Returns
    -------
    property
        A `property` object that is evaluated once on first access, and
        thereafter returns that value.

    Notes
    -----
        To modify the attributes value in a corresponding setter, set the object's hidden
        attribute with name `f"__{method.__name__}"`.
    """

    key = f'__{method.__name__}'

    @property
    @functools.wraps(method)
    def _(self):
        if not hasattr(self, key):
            setattr(self, key, method(self))
        return getattr(self, key)

    return _
