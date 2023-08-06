#!/bin/false
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.globbing`."""

import os
import pytest
from ptutils.globbing import scan_folder, get_subdirs, get_subfiles
from ._fs_fixture import GLOBBING_QUERIES, sample_file_structure, path_parts  # noqa: F401


@pytest.mark.parametrize(
    ["path", "pattern", "recursive", "filterfunc", "expected"],
    GLOBBING_QUERIES,
    ids = [f"GLOBBING_QUERIES[{i}]" for i in range(len(GLOBBING_QUERIES))]
)
def test_scan_folder(sample_file_structure, path, pattern, recursive, filterfunc, expected):  # noqa: F811
    folder = os.path.join(sample_file_structure, path)
    items = list(scan_folder(
        folder     = folder,
        pattern    = pattern,
        recursive  = recursive,
        filterfunc = filterfunc
    ))
    items_rel    = set([os.path.relpath(item, sample_file_structure) for item in items])
    expected_rel = set([os.path.join(*path_parts(path)) for path in expected])
    assert bool(items_rel)
    assert bool(expected_rel)
    assert items_rel == expected_rel


@pytest.mark.parametrize(
    ["path", "pattern", "recursive", "filterfunc", "expected"],
    GLOBBING_QUERIES,
    ids = [f"GLOBBING_QUERIES[{i}]" for i in range(len(GLOBBING_QUERIES))]
)
def test_get_subdirs(sample_file_structure, path, pattern, recursive, filterfunc, expected):  # noqa: F811
    if filterfunc is os.path.isdir:
        folder = os.path.join(sample_file_structure, path)
        items = list(get_subdirs(
            folder     = folder,
            pattern    = pattern,
            recursive  = recursive
        ))
        items_rel    = set([os.path.relpath(item, sample_file_structure) for item in items])
        expected_rel = set([os.path.join(*path_parts(path)) for path in expected])
        assert bool(items_rel)
        assert bool(expected_rel)
        assert items_rel == expected_rel


@pytest.mark.parametrize(
    ["path", "pattern", "recursive", "filterfunc", "expected"],
    GLOBBING_QUERIES,
    ids = [f"GLOBBING_QUERIES[{i}]" for i in range(len(GLOBBING_QUERIES))]
)
def test_get_subfiles(sample_file_structure, path, pattern, recursive, filterfunc, expected):  # noqa: F811
    if filterfunc is os.path.isfile:
        folder = os.path.join(sample_file_structure, path)
        items = list(get_subfiles(
            folder     = folder,
            pattern    = pattern,
            recursive  = recursive
        ))
        items_rel    = set([os.path.relpath(item, sample_file_structure) for item in items])
        expected_rel = set([os.path.join(*path_parts(path)) for path in expected])
        assert bool(items_rel)
        assert bool(expected_rel)
        assert items_rel == expected_rel
