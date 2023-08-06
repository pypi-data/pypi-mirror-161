#!/bin/false
# -*- coding: utf-8 -*-

"""
A collection of functions for working with regular expressions.
"""
# =======================================================================================================================
# imports
# =======================================================================================================================
import re
from typing import Iterable, List, Match, Optional, Pattern, Tuple, Union

from ptutils.text import elide
from ptutils.punning import to_string


# =======================================================================================================================
# TypeHints
# =======================================================================================================================
PatternList        = Iterable[Pattern]
OneOrMorePatterns  = Union[Pattern, PatternList]
ZeroOrMorePatterns = Optional[Union[Pattern, PatternList]]
MatchOrMatchTuple  = Union[ Optional[ Match ], Tuple[ Optional[ Pattern ], Optional[ Match ] ] ]


# =======================================================================================================================
# utility functions
# =======================================================================================================================
def _match_or_match_tuple(pattern: Pattern, match: Match, return_pattern: bool = False) -> MatchOrMatchTuple:
    """
    Helper function to select desired outputs.

    Parameters
    ----------
    pattern : Pattern
        A regular expression.
    match : Match
        A corresponding match object
    return_pattern : bool, optional
        True if the tuple pattern,match should be returned, False if only the match is returned, by default False

    Returns
    -------
    MatchOrMatchTuple
        Returns pattern,match if return_pattern is True, or match if return_pattern is False
    """
    if return_pattern:
        return (pattern, match)
    else:
        return  match


# -----------------------------------------------------------------------------------------------------------------------
def match_one_of(
    patterns:          PatternList,
    text:              str,
    return_pattern:    bool = False,
    raise_on_no_match: bool = False
) -> MatchOrMatchTuple:
    """
    Match text against a list of regular expressions returning the first match, if any.
    Optionally includes exression which matched. Optionally raises exception if no match
    is found.

    Parameters
    ----------
    patterns : PatternList
        A list of regular expressions (either a string or a compiled pattern).
    text : str
        The text to match.
    return_pattern : bool, optional
        Return both the matching pattern and the match object, by default False. When
        false, only returns the match object.
    raise_on_no_match : bool, optional
        If no patterns match the text (or none are supplied) raise an Exception, by
        default False. When false and no match is found, either None or (None, None) is returned
        based on the value of `return_pattern`.

    Returns
    -------
    MatchOrMatchTuple
        Either a match object, or a tuple of pattern and match object.

    Raises
    ------
    Exception
        When no pattern is matched and `raise_on_no_match` is set to true.
    """

    # use match_many to find 1 match
    result = match_many(
        patterns          = patterns,
        text              = text,
        return_patterns   = return_pattern,
        raise_on_no_match = raise_on_no_match,
        limit             = 1
    )

    # no match, but no exception needs to be thrown.
    return result[0] if result else _match_or_match_tuple( None, None, return_pattern )


# -----------------------------------------------------------------------------------------------------------------------
def match_many(
    patterns:          PatternList,
    text:              str,
    return_patterns:   bool = False,
    raise_on_no_match: bool = False,
    limit:             int  = None
) -> List[ MatchOrMatchTuple ]:
    """
    Match text against a list of regular expressions returning all matches, if any.
    Optionally includes exression(s) which matched. Optionally raises exception if no match
    is found.

    Parameters
    ----------
    patterns : PatternList
        A list of regular expressions (either a string or a compiled pattern).
    text : str
        The text to match.
    return_pattern : bool, optional
        Return both the matching pattern and the match object, by default False. When
        false, only returns the match object.
    raise_on_no_match : bool, optional
        If no patterns match the text (or none are supplied) raise an Exception, by
        default False. When false and no match is found, either None or (None, None) is returned
        based on the value of `return_pattern`.

    Returns
    -------
    List[ MatchOrMatchTuple ]
        List of match objects, or a list of tuples of pattern and match object.

    Raises
    ------
    Exception
        When no pattern is matched and `raise_on_no_match` is set to true.
    """
    # set up return variable
    result = []

    # iterate over patterns
    for pattern in patterns:

        # check if the string matches the pattern
        match = re.match(pattern, text)
        if match:

            # append the result
            result.append( _match_or_match_tuple( pattern, match, return_patterns) )

            # check limit condition
            if (limit is not None) and ( len(result) >= limit ):
                break

    # if we got here there was no match. Should we raise?
    if (not result) and raise_on_no_match:

        # get a list of the patterns as strings
        p = [ regex_to_string(x) for x in patterns ]

        # set up the message
        msg = f"Text '{elide(text, 80)}' failed to match any of the supplied patterns {p}."

        # raise the exception
        raise Exception( msg )

    # return the result(s)
    return result


# -----------------------------------------------------------------------------------------------------------------------
def regex_to_string(
    pattern:       Pattern,
    auto_compile:  bool = False,
    coerce_string: bool = False
) -> str:
    """
    Return a regular expression's string representation.

    Parameters
    ----------
    pattern : Pattern
        The regular expression
    auto_compile : bool, optional
        Flag indicating the input argument should automatically bre compiled, by default False
    coerce_string : bool, optional
        Flag indicating the input argument should be coerced toa string, by default False

    Returns
    -------
    str
        The string representation of the regular expression.
    """
    # if already a compiled pattern, shortcut.
    if isinstance(pattern, re.Pattern):
        return pattern.pattern

    # coerce to string as necessary
    if coerce_string and not isinstance(pattern, str):
        pattern = to_string( pattern )

    # ensure we have a compiled pattern
    if auto_compile:
        return re.compile( pattern ).pattern
    return pattern
