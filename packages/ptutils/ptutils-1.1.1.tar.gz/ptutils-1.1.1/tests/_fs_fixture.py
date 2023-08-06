#!/bin/false
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.globbing`."""

import datetime
import os
import pytest
import tempfile
import shutil

FILE_STRUCTURE = {
    "boring_things": {
        "thing.json":      '{ "a": 1, "b": true, "c": 123.45, "d": "hello world" }',
        "thing.yaml":      '---\na: 1\nb: true\nc: 123.45\nd: hello world',
        "text_thing":      'this is file 2',
        "tbd_things": {
        }
    },
    "interesting_things": {
        "scary_thing": "Dracula",
        "silly_thing": "Spongebob",
        "bright_thing": "The sun",
        "heavy_things": {
            "divorce": "nope",
            "lead": "plumbum"
        },
        "auto_things": {
            "mobile": "car",
            "graph": "signature"
        },
        "missing_things": {}
    },
    "apples": {
        "granny-smith": "green",
        "red-delicious": "red"
    },
    "a_file": "some content",
    "another_file": "some other content"
}
PATH_THINGS = ""
PATH_BORING_THINGS = "/boring_things"
PATH_TBD_THINGS = "/boring_things/tbd_things"
PATH_INTERESTING_THINGS = "/interesting_things"
PATH_HEAVY_THINGS = "/interesting_things/heavy_things"
PATH_AUTO_THINGS_THINGS = "/interesting_things/auto_things"
PATH_MISSING_THINGS = "/interesting_things/missing_things"
PATH_APPLES = "apples"

THING_SUBDIRS = ["/boring_things", "/interesting_things", "/apples"]
THING_SUBFILES = ["/a_file", "/another_file"]
THING_SUBS = THING_SUBDIRS + THING_SUBFILES

THING_SUBDIRS_REC = [
    PATH_BORING_THINGS,
    PATH_TBD_THINGS,
    PATH_INTERESTING_THINGS,
    PATH_HEAVY_THINGS,
    PATH_AUTO_THINGS_THINGS,
    PATH_MISSING_THINGS,
    PATH_APPLES
]
THING_SUBFILES_REC = [
    "/a_file",
    "/another_file",
    PATH_BORING_THINGS + "/thing.json",
    PATH_BORING_THINGS + "/thing.yaml",
    PATH_BORING_THINGS + "/text_thing",
    PATH_INTERESTING_THINGS + "/scary_thing",
    PATH_INTERESTING_THINGS + "/silly_thing",
    PATH_INTERESTING_THINGS + "/bright_thing",
    PATH_HEAVY_THINGS + "/divorce",
    PATH_HEAVY_THINGS + "/lead",
    PATH_AUTO_THINGS_THINGS + "/mobile",
    PATH_AUTO_THINGS_THINGS + "/graph",
    PATH_APPLES + "/granny-smith",
    PATH_APPLES + "/red-delicious",
]

THING_KEYED_SUBFILES_REC = [
    PATH_BORING_THINGS + "/text_thing",
    PATH_INTERESTING_THINGS + "/scary_thing",
    PATH_INTERESTING_THINGS + "/silly_thing",
    PATH_INTERESTING_THINGS + "/bright_thing",
]

STARTS_WITH_A_REC = [
    "/a_file",
    "/another_file",
    PATH_AUTO_THINGS_THINGS,
    PATH_APPLES
]



def path_parts(path: str):
    return [x for x in path.split('/') if x ]


def localize_path(path: str):
    return path.replace('/', os.sep)


def populate(path, content):
    if isinstance(content, dict):
        os.makedirs(path, exist_ok=True)
        for (k, v) in content.items():
            populate(os.path.join(path, k), v)
    elif isinstance(content, str):
        with open(path, "w") as filp:
            filp.write(content)
    else:
        raise Exception("BUG: content is not a string and is not a dict.")


@pytest.fixture(autouse=True)
def sample_file_structure():
    dir = tempfile.TemporaryDirectory()
    populate(dir.name, FILE_STRUCTURE)
    yield dir.name
    shutil.rmtree(dir.name)


""" Queries for globbing and expected results. """
GLOBBING_QUERIES = [
    # (path, pattern, recursive, filter_func, expected_relpaths)
    (PATH_THINGS, None, False, None,           THING_SUBS),
    (PATH_THINGS, None, False, os.path.isfile, THING_SUBFILES),
    (PATH_THINGS, None, False, os.path.isdir,  THING_SUBDIRS),
    (PATH_THINGS, None, True,  os.path.isfile, THING_SUBFILES_REC),
    (PATH_THINGS, None, True, os.path.isdir,  THING_SUBDIRS_REC),
    (PATH_THINGS, r'^.*_thing$', True, None,  THING_KEYED_SUBFILES_REC),
    (PATH_THINGS, r'^a.*$', True, None,  STARTS_WITH_A_REC),
]
