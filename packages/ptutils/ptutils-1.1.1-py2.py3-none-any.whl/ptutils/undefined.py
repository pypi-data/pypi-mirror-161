#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides utilities for differentiating between an explicit None, and an unspecified None.
"""

from typing import Any


class UndefinedMeta(type):
    """ A metatype for the undefined type to ensure the class itself evaluates as false in boolean contexts. """

    def __nonzero__(cls) -> bool:  # pragma: no cover
        """ Allow the Undefined class to evaluate as `False` in boolean contexts.

        Returns
        -------
        value: bool
            Always returns False

        """
        return False

    def __bool__(cls) -> bool:
        """ Allow the Undefined class to evaluate as `False` in boolean contexts.

        Returns
        -------
        value: bool
            Always returns False

        """
        return False


class Undefined(metaclass=UndefinedMeta):
    """ An object representing an unspecified or undefined value. """

    def __nonzero__(self) -> bool:  # pragma: no cover
        """ Allow the undefined object to evaluate as `False` in boolean contexts.

        Returns
        -------
        value: bool
            Always returns False

        """
        return False

    def __bool__(self) -> bool:
        """ Allow the undefined object to evaluate as `False` in boolean contexts.

        Returns
        -------
        value: bool
            Always returns False

        """
        return False


# ------------------------------------------------------------------------------------------------------------------------
""" Global constant instance of `Undefined` """
UNDEFINED = Undefined()


# ------------------------------------------------------------------------------------------------------------------------
def is_undefined(x: Any) -> bool:
    """ Test if an object is undefined.

    Parameters
    ----------
    x: Any
        The object to test for undefined-ness.

    Returns
    -------
    is_undefined: bool
        Return `True` if the supplied object is undefined, `False` otherwise.

    """
    return (x is UNDEFINED) or isinstance(x, Undefined) or (x is Undefined)


# ------------------------------------------------------------------------------------------------------------------------
def is_defined(x: Any) -> bool:
    """ Test if an object is defined.

    Parameters
    ----------
    x: Any
        The object to test for defined-ness.

    Returns
    -------
    is_defined: bool
        Return `True` if the supplied object is defined, `False` otherwise.

    """
    return not is_undefined(x)


# ------------------------------------------------------------------------------------------------------------------------
def default_if_undefined(x: Any, default: Any = None) -> Any:
    """ Return object if defined, else return default.

    Parameters
    ----------
    x: Any
        The object to test for defined-ness and return when defined.
    x: Any
        The object to return when `x` is undefined.

    Returns
    -------
    value: bool
        Return `x` as long as it is defined, otherwise return `default`.

    """
    if is_defined(x):
        return x

    return default
