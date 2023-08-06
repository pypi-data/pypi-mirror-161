#!/bin/false
# -*- coding: utf-8 -*-

""" Functions for locating files and folders on the local filesystem. """

# ------------------------------------------------------------------------------------------------------------------------
# Main imports
# ------------------------------------------------------------------------------------------------------------------------
import os
import re
from typing import Callable, Optional, Pattern, Generator


# ------------------------------------------------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------------------------------------------------
def scan_folder(
    folder:     str,
    pattern:    Optional[Pattern]     = None,
    recursive:  bool                  = False,
    filterfunc: Callable[[str], bool] = None
) -> Generator[str, None, None]:
    """
    Scan folder for files and folders matching a regular expression.

    Parameters
    ----------
    folder : str
        The folder in which to start the search.
    pattern : Pattern, optional
        A regular expression to match against file and folder basenames, by
        default None. When omitted, every file or folder in the search folder
        will be returned.
    recursive : bool, optional
        When True, search recursively into all subfolders of the search
        folder, by default False.
    filterfunc : Callable[[str], bool], optional
        A function to apply to file or folder full paths to further filter
        the returned results, by default None.

    Yields
    -------
    Generator[str, None, None]
        The fullpath to files or folders which match the specified constraints.
    """
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for dirname in dirnames:
            if (pattern is None) or re.match(pattern, dirname):
                fullpath = os.path.join(dirpath, dirname)
                if (filterfunc is None) or filterfunc(fullpath):
                    yield fullpath

        for filename in filenames:
            if (pattern is None) or re.match(pattern, filename):
                fullpath = os.path.join(dirpath, filename)
                if (filterfunc is None) or filterfunc(fullpath):
                    yield fullpath

        if not recursive:
            dirnames.clear()


# ------------------------------------------------------------------------------------------------------------------------
def get_subdirs(
    folder:     str,
    pattern:    Pattern               = None,
    recursive:  bool                  = False,
):
    """
    Scan folder for folders matching a regular expression.

    Parameters
    ----------
    folder : str
        The folder in which to start the search.
    pattern : Pattern, optional
        A regular expression to match against folder basenames, by
        default None. When omitted, every folder in the search folder
        will be returned.
    recursive : bool, optional
        When True, search recursively into all subfolders of the search
        folder, by default False.

    Yields
    -------
    Generator[str, None, None]
        The fullpath to folders which match the specified constraints.
    """
    return scan_folder(
        folder,
        pattern    = pattern,
        recursive  = recursive,
        filterfunc = os.path.isdir
    )


# ------------------------------------------------------------------------------------------------------------------------
def get_subfiles(
    folder:     str,
    pattern:    Pattern               = None,
    recursive:  bool                  = False,
):
    """
    Scan folder for files matching a regular expression.

    Parameters
    ----------
    folder : str
        The folder in which to start the search.
    pattern : Pattern, optional
        A regular expression to match against file basenames, by
        default None. When omitted, every file in the search folder
        will be returned.
    recursive : bool, optional
        When True, search recursively into all subfolders of the search
        folder, by default False.

    Yields
    -------
    Generator[str, None, None]
        The fullpath to files which match the specified constraints.
    """
    return scan_folder(
        folder,
        pattern    = pattern,
        recursive  = recursive,
        filterfunc = os.path.isfile
    )
