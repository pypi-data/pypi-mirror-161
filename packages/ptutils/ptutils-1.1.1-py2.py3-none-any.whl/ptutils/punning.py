#!/bin/false
# -*- coding: utf-8 -*-

"""
A collection of functions for text manipulation.
"""


# =======================================================================================================================
# Main imports
# =======================================================================================================================
from typing import Dict, List, Any, Union
from ptutils.encoding import decode_json, decode_yaml
from ptutils.undefined import is_undefined
from ptutils.typing import is_string, is_sequence
from ptutils.text import strip_quotes


# =======================================================================================================================
# Utility functions: Type conversion
# =======================================================================================================================
# ------------------------------------------------------------------------------------------------------------------------
def to_string(obj: Any) -> str:
    """
    Attempt to convert object to string.
    * If `obj` is already a `str` return `obj` unmodified.
    * If `obj` is `bytes`, attempt to decode using utf-8.
    * If `obj` is any other type, return `str(obj)`.

    Parameters
    ----------
    obj : Any
        The object to convert.

    Returns
    -------
    str
        The object converted to a string.
    """
    if is_string(obj):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        return str(obj)


# ------------------------------------------------------------------------------------------------------------------------
def boolify(x: Any) -> bool:
    """
    Convert object to boolean.
    * If `x` is already a `bool` return `x` unmodified.
    * If `x` is `UNDEFINED` or `None`, return False.
    * If `x` is a string, return true when `x.lower()` is one of 'yes', 'on', 'true', 'enabled', or '1'.

    Parameters
    ----------
    x : Any
        The object to inspect.

    Returns
    -------
    bool
        `True` or `False` based on best interpretation of `x`

    Raises
    ------
    TypeError
        When `x` can not be converted to a boolean.
    """
    # if the object is already a boolean, return it.
    if isinstance(x, bool):
        return x

    # if the object is None, return False
    if x is None:
        return False

    # if the object is undefined, return False
    if is_undefined(x):
        return False

    # if the object is a string, return True if it is any of the true boolean words
    if isinstance(x, str):
        x_ = x.lower()
        if x_ in ['yes', 'on', 'true', 'enabled', '1']:
            return True
        if x_ in ['no', 'off', 'false', 'disabled', '0']:
            return False

    raise TypeError("Can't convert '%s'  to boolean" % type(x).__name__)


# ------------------------------------------------------------------------------------------------------------------------
def listify(obj: Any, strict: bool = False) -> List[Any]:
    """
    Convert object to a list.
    If the object is a scalar, including astrings, return t a list with that scalar
    as the only element.
    If the object is already an sequence type, return the object unmodified unless
    `strict` is `True`, in which case convert the sequence to a `list`.

    Parameters
    ----------
    obj : Any
        The object to convert to a list
    strict : bool, optional
        When False and `obj` is a `tuple` or a `set`, return the object. When True
        and `obj` is a `tuple` or a `set`, return a list with the same contents. By
        default False

    Returns
    -------
    List[Any]
        A list of objects.
    """
    # check if the object is a sequence
    if is_sequence(obj):

        # if the sequence is not strictly a list, convert to list
        if strict and not isinstance(obj, list):
            return list(obj)

        # return the object
        return obj

    # wrap the object in a list.
    return [obj]


# ------------------------------------------------------------------------------------------------------------------------
def as_numeric(text: Any) -> Union[int, float]:
    """
    Try parsing a string as a numberic value or raise ValueError.

    Parameters
    ----------
    text : Any
        A string.

    Returns
    -------
    Union[int, float]
        The numeric value.

    Raises
    ------
    ValueError
        When `text` can not be interpreted as either an integer or floating point number.
    """
    # try parsing as float
    try:
        return float(text)
    except ValueError:
        pass

    # try parsing as int
    try:
        return int(text)
    except:  # noqa: E722
        raise ValueError("Can not parse text as an integer or float.")


# ------------------------------------------------------------------------------------------------------------------------
def as_encoded(text: Any) -> Any:
    """
    Try parsing a string as an encoded JSON or YAML string.

    Parameters
    ----------
    text : Any
        A string.

    Returns
    -------
    Any
        The decoded value.

    Raises
    ------
    ValueError
        When `text` can not be interpreted as either a JSON- or YAML-encoded string.
    """
    # try parsing as JSON
    try:
        return decode_json(text)
    except:  # noqa: E722
        pass

    # try parsing as YAML
    try:
        return decode_yaml(text)
    except:  # noqa: E722
        raise ValueError("Can not parse text as either JSON or YAML.")


# ------------------------------------------------------------------------------------------------------------------------
def as_literal(text: Any) -> Any:
    """
    Try parsing a string as bool or None literal.

    Parameters
    ----------
    text : Any
        A string.

    Returns
    -------
    Any
        The interpreted value; either a boolean or None.

    Raises
    ------
    ValueError
        When `text` can not be interpreted as either a boolean or None.
    """
    # Strip any quotes
    text2 = strip_quotes(text).lower()

    # test against falsw words
    if text2 in ['no', 'off', 'disabled', 'false']:
        return False

    # test against true words
    if text2 in ['yes', 'on', 'enabled', 'true']:
        return True

    # Check for null/none
    if text2 in ['null', 'none']:
        return None

    raise ValueError("Can not parse text as either boolean or none.")


# ------------------------------------------------------------------------------------------------------------------------
def canonize(text: Any) -> Any:
    """
    Attempt to parse a string into the most canonical pythonic form. For example, this function maps the
    strings 'yes', 'no', etc. to appropriate boolean. If a string is valid JSON or YAML(when supported), or
    a known boolean word, or integer or float, this function will convert the text to that type. If `text`
    is not a string, it is returned unmodified.

    Parameters
    ----------
    text : Any
        The string to process.

    Returns
    -------
    Any
        The most appropriate object based on the content of `text`.
    """

    # interpret bytes as utf-8
    if isinstance(text, bytes):
        return canonize(text.decode('utf-8'))

    # if not a string, return the object unmodified
    if not isinstance(text, str):
        return text

    # try parsing as numeric
    try:
        return as_numeric(text)
    except ValueError:
        pass

    # try parsing as boolean or None literal
    try:
        return as_literal(text)
    except:  # noqa: E722
        pass

    # try parsing as JSON or YAML
    try:
        return as_encoded(text)
    except:  # noqa: E722
        pass

    # give up and return the object unmodified.
    return text


# -----------------------------------------------------------------------------------------------------------------------
def maybe_canonize(v: Any, should_canonize: bool = True) -> Any:
    """
    Optionally `canonize` a value.

    Parameters
    ----------
    v : Any
        The value to possibly canonize.
    should_canonize : bool, optional
        When true, returnb `canonize(v)`, otherwise return `v`, by default True

    Returns
    -------
    Any
        Either `v` or the canonization of `v`.
    """
    return canonize(v) if should_canonize else v


# -----------------------------------------------------------------------------------------------------------------------
def maybe_coerce_none(v: Any, should_coerce: bool = True) -> Any:
    """
    Optionally coerce falsey values to None.

    Parameters
    ----------
    v : Any
        The value to possibly coerce.
    should_coerce : bool, optional
        When true and `v` is falsey, return None. Otherwise return `v`, by default True

    Returns
    -------
    Any
        The value of `v` possibly coerced to None if falsey.
    """
    return (v or None) if should_coerce else v


# -----------------------------------------------------------------------------------------------------------------------
def canonize_dict( x: Dict[ str, Any ]) -> Any:
    """
    Canonize the values of a dictionary (see `canonize`).

    Parameters
    ----------
    x : Dict[ str, Any ]
        A dictionary.

    Returns
    -------
    Any
        A copy of `x` with values replaced with their canonized equivalents.
    """
    return dict(
        (k, canonize(v))
        for (k, v)
        in  x.items()
    )
