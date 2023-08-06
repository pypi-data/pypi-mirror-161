#!/bin/false
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.globbing`."""

# =======================================================================================================================
# imports
# =======================================================================================================================
import shutil
import tempfile
from time import sleep
from typing import Any
import pytest
from ptutils.caching import Cache
from ptutils.file import Folder, FolderStore
from ptutils.undefined import UNDEFINED


# =======================================================================================================================
# Test case data
# =======================================================================================================================
NATIVE_CASES = [
    None,
    "string",
    123456,
    123456.789,
    True,
    False,
    [],
    [None],
    ["a", 2, 3.0, True, False, {}],
    {"a": 1, "5": 123, "p": False}
]


# =======================================================================================================================
# Test fixtures
# =======================================================================================================================
@pytest.fixture(autouse=True)
def store_cache():
    dir    = tempfile.TemporaryDirectory()
    folder = Folder(dir.name)
    store  = FolderStore(folder=folder, suffix="yml")
    cache  = Cache(
        store    = store,
        default  = UNDEFINED,
        create   = UNDEFINED,
        max_age  = UNDEFINED,
        validate = UNDEFINED
    )
    yield cache
    shutil.rmtree( dir.name )


# -----------------------------------------------------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def dict_cache():
    cache  = Cache( store = dict() )
    yield cache


# =======================================================================================================================
# Helper functions
# =======================================================================================================================
def cache_checks( cache ) -> None:

    # check initially empty cache has length 0
    L0 = len(cache)
    assert L0 == 0, f"Cache did not have an initial size of 0, was {L0} instead."

    # check round-trip conversion for key/value set/get
    for i, value in enumerate(NATIVE_CASES):
        key = f"item-{i}"
        cache[key] = value
        result = cache[key]
        assert result == value, f"Cache value '{key}' was {result} instead of expected {value}."

        L1 = len(cache)
        assert L1 == ( i + 1 ), f"Cache did not have the expected size of {i+1}, was {L1} instead."

    cache.clear()

    # check cleared cache has length 0
    L2 = len(cache)
    assert L2 == 0, f"Cache did not have an cleared size of 0, was {L2} instead."

    # Check default is applied
    computed = cache.get_entry(
        name = 'does-not-exist',
        default = 'default'
    )
    assert computed.value == 'default', f"Cache miss w/ default does not return default, was {computed.value} instead."

    # Check applied default is persisted
    try:
        result = cache['does-not-exist']
    except Exception as e:
        raise Exception("Failed to fetch cached value after populating with default.") from e

    assert result == 'default', f"Cache miss w/ default does not return default, was {computed.value} instead."

    # Check create is applied
    computed = cache.get_entry(
        name = 'also-does-not-exist',
        create = lambda: 'default'
    )
    assert computed.value == 'default', f"Cache miss w/ create does not return default, was {computed.value} instead."

    # Check applied create is persisted
    try:
        result = cache['also-does-not-exist']
    except Exception as e:
        raise Exception("Failed to fetch cached value after populating with create().") from e

    assert result == 'default', f"Cache miss w/ create does not return default, was {computed.value} instead."

    # Sleep for 0.5 seconds
    sleep( 0.1 )

    # check expired cache entry results in raised key error.
    with pytest.raises(KeyError) as ke:
        _ = cache.get_entry(
            name    = 'does-not-exist',
            max_age = 0.05
        )

    error = f"Expired cache entry access does not raise KeyError. Instead raised {type(ke.value).__qualname__}"
    assert isinstance(ke.value, KeyError), error


# =======================================================================================================================
# Tests
# =======================================================================================================================
def test_dict_cache(dict_cache) -> None:
    cache_checks(
        cache = dict_cache
    )


# -----------------------------------------------------------------------------------------------------------------------
def test_store_cache(store_cache) -> None:
    cache_checks(
        cache = store_cache
    )
