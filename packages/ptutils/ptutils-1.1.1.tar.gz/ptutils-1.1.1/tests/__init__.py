#!/usr/bin/env python
# -*- coding: utf-8 -*-

def test_import_version():
    """ Test theat the package version is defined and that imports are working. """
    from ptutils.version import version
    assert isinstance(version, str)
    assert bool(version)
