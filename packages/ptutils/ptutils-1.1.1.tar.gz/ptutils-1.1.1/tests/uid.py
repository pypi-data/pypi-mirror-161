#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.uid`.
"""

import uuid
from ptutils.uid import random_uuid, parse_uuid, uuid_from_name, PTUTILS_NAMESPACE_UUID


def test_random_uuid_returns_a_uuid():
    assert isinstance(random_uuid(), uuid.UUID)


def test_subsequent_random_uuids_differ():
    last = None
    for _ in range(1000):
        current = random_uuid()
        assert current != last
        last = current


def test_parse_uuid_round_trip_conversion():
    uuids      = [ random_uuid() for _ in range(100) ]
    uuid_texts = map(str, uuids)
    rt_uuids   = list( map( parse_uuid, uuid_texts ) )
    assert rt_uuids == uuids


def test_uuid_from_name_is_stable_with_respect_to_stable_name():
    assert uuid_from_name(
        name = "abc123"
    ) == uuid_from_name(
        name = "abc123"
    )


def test_uuid_from_name_varies_with_respect_to_varying_name():
    assert uuid_from_name(
        name = "abc123"
    ) != uuid_from_name(
        name = "123abc"
    )


def test_uuid_from_name_uses_ptutils_namespace_uuid():
    assert uuid_from_name(
        name = "abc"
    ) == uuid_from_name(
        name = "abc",
        namespace_uuid = PTUTILS_NAMESPACE_UUID
    )


def test_uuid_from_name_allows_other_namespace_uuid():
    assert uuid_from_name(
        name = "abc"
    ) != uuid_from_name(
        name = "abc",
        namespace_uuid = random_uuid()
    )
