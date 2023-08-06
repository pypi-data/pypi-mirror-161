#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the main module for the package.
"""

# ------------------------------------------------------------------------------------------------------------------------
# Main imports
# ------------------------------------------------------------------------------------------------------------------------
from ptutils.version import version as __version__  # noqa: F401

all = [
    '__version__'
]

# ------------------------------------------------------------------------------------------------------------------------
# Import protection
# ------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    raise Exception(
        "This module is not executable. To use it, add "
        "'from pt import ptutils' to your python source "
        "code. Refer to the API documentation for more "
        "information."
    )
