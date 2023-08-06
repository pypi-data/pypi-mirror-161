#!/bin/false
# -*- coding: utf-8 -*-

""" Logging functions. """

# ------------------------------------------------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------------------------------------------------
import logging
from typing import Dict, Tuple, Union
from ptutils.undefined import default_if_undefined, UNDEFINED, Undefined

# ------------------------------------------------------------------------------------------------------------------------
# Logger config
# ------------------------------------------------------------------------------------------------------------------------
""" The default verbosity to use when not otherwise specified."""
DEFAULT_VERBOSITY = 3


""" The currently configured verbosity. use `get_verbosity` or `set_verbosity` to modify. """
__VERBOSITY__ = DEFAULT_VERBOSITY


# ------------------------------------------------------------------------------------------------------------------------
""" The currently configured log level. use `get_verbosity` or `set_verbosity` to modify. """
__LEVEL__ = logging.INFO


# ------------------------------------------------------------------------------------------------------------------------
""" The currently configured log level name. use `get_verbosity` or `set_verbosity` to modify. """
__LEVEL_NAME__ = 'INFO'


# ------------------------------------------------------------------------------------------------------------------------
""" A mapping between verbosity levels and standard python logging levels. """
__VERBOSITY_LEVELS__: Dict[int, Tuple[int, str]] = {
    5: (logging.NOTSET + 1, "VERBOSE"),
    4: (logging.DEBUG,      "DEBUG"),
    3: (logging.INFO,       "INFO"),
    2: (logging.WARNING,    "WARNING"),
    1: (logging.ERROR,      "ERROR"),
    0: (logging.CRITICAL,   "CRITICAL")
}


# ------------------------------------------------------------------------------------------------------------------------
def clip_verbosity_level(verbosity: int) -> int:  # pragma: no cover
    """
    Given a verbosity level, clip it to the allowable range of [0,5] (inclusive).

    Parameters
    ----------
    verbosity : int
        An integer verbosity level.

    Returns
    -------
    int
        The value clipped to the range [0,5].

    Raises
    ------
    Exception
        When verbosity is not or can not be converted to an integer.

    """
    verbosity = int(verbosity)
    if verbosity < 0:
        return 0
    if verbosity > 5:
        return 5
    return verbosity


# ------------------------------------------------------------------------------------------------------------------------
def translate_verbosity_level(verbosity: int) -> Tuple[int, str]:  # pragma: no cover
    """
    Given a verbosity level, get the python `logging` standard library level and level name.

    Parameters
    ----------
    verbosity : int
        A verbosity level on the range [0,5].

    Returns
    -------
    Tuple[int, str]
        The corresponding logging level and level name.

    Raises
    ------
    ValueError
        If verbosity is not an integer on the range [0,5].
    """
    if verbosity in __VERBOSITY_LEVELS__:
        return __VERBOSITY_LEVELS__[verbosity]
    else:
        raise ValueError(f"I don't know how to interpret verbosity level {verbosity}.")


# ------------------------------------------------------------------------------------------------------------------------
def set_verbosity(verbosity: Union[int, Undefined] = UNDEFINED) -> None:  # pragma: no cover
    """
    Set the logging verbosity.

    Parameters
    ----------
    verbosity : Union[int, Undefined], optional
        A verbosity level on the range [0,5] or UNDEFINED, by default UNDEFINED. When
        UNDEFINED, the default value of `DEFAULT_VERBOSITY` is used.

    Notes
    -----
    `verbosity` may be any thing convertaible to an integer, and will be clipped to
    the valid range use.
    """
    global __VERBOSITY__
    global __LEVEL__
    global __LEVEL_NAME__

    # set the verbosity to default if not specified.
    verbosity = default_if_undefined(verbosity, DEFAULT_VERBOSITY)

    # clip verbosity to allowed range.
    verbosity = clip_verbosity_level(verbosity)

    # translate verbosity to log level
    level, name = translate_verbosity_level(verbosity)

    # apply verbosity level
    logger.setLevel(level)
    __VERBOSITY__  = verbosity
    __LEVEL__      = level
    __LEVEL_NAME__ = name


# ------------------------------------------------------------------------------------------------------------------------
def get_verbosity() -> int:  # pragma: no cover
    """
    Get the currently configured logging verbosity.

    Returns
    -------
    int
        The verbosity value on range [0,5].
    """
    return __VERBOSITY__


# ------------------------------------------------------------------------------------------------------------------------
def get_level() -> int:  # pragma: no cover
    """
    Get the currently configured logging level.

    Returns
    -------
    int
        The verbosity value on range [0,5].
    """
    return __LEVEL__


# ------------------------------------------------------------------------------------------------------------------------
def get_level_name() -> str:  # pragma: no cover
    """
    Get the currently configured logging level name.

    Returns
    -------
    str
        One of VERBOSE, DEBUG, INFO, WARNING, ERROR, or CRITICAL
    """
    return __LEVEL_NAME__


# ------------------------------------------------------------------------------------------------------------------------
def getLogger(*args, **kwargs) -> logging.Logger:  # pragma: no cover
    """
    Get a logger.

    Returns
    -------
    logging.Logger
        a logger.
    """
    return logging.getLogger(*args, **kwargs)


# ------------------------------------------------------------------------------------------------------------------------
# Root logger initialization
# ------------------------------------------------------------------------------------------------------------------------
logging.basicConfig(level=__LEVEL__)
logger = logging.getLogger()
logger.setLevel( __LEVEL__ )
