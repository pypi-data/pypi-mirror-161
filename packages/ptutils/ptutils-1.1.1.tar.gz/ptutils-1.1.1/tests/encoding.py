#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.encoding`."""

import pytest
import datetime
from typing import Dict, Any
from ptutils.encoding import (
    HAVE_YAML,
    encode_json,
    encode_yaml,
    pretty_json,
    pretty_yaml,
    decode_json,
    decode_yaml,
    json_serial,
    register_yaml_type
)


def test_json_serial_handles_datetime():
    val = json_serial(datetime.datetime.utcnow())
    assert isinstance(val, str)
    assert bool(val)


def test_json_serial_handles_timedelta():
    val = json_serial(datetime.timedelta(seconds=5))
    assert isinstance(val, (int, float))
    assert val == 5


def test_json_serial_fails_with_unknown_class():
    class C:
        pass
    with pytest.raises(TypeError) as _:
        _ = json_serial(C())


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


@pytest.mark.parametrize(
    "test_case",
    NATIVE_CASES,
    ids = [f"NATIVE_CASES[{i}]" for i in range(len(NATIVE_CASES))]
)
def test_json_roundtrip(test_case):
    encoded_test_case = encode_json(test_case)
    assert isinstance(encoded_test_case, str)
    assert bool(encoded_test_case)
    decoded_test_case = decode_json(encoded_test_case)
    assert decoded_test_case == test_case


@pytest.mark.parametrize(
    "test_case",
    NATIVE_CASES,
    ids = [f"NATIVE_CASES[{i}]" for i in range(len(NATIVE_CASES))]
)
def test_json_pretty_roundtrip(test_case):
    encoded_test_case = pretty_json(test_case)
    assert isinstance(encoded_test_case, str)
    assert bool(encoded_test_case)
    decoded_test_case = decode_yaml(encoded_test_case)
    assert decoded_test_case == test_case


@pytest.mark.parametrize(
    "test_case",
    NATIVE_CASES,
    ids = [f"NATIVE_CASES[{i}]" for i in range(len(NATIVE_CASES))]
)
def test_yaml_roundtrip(test_case):
    if HAVE_YAML:
        encoded_test_case = encode_yaml(test_case)
        assert isinstance(encoded_test_case, str)
        assert bool(encoded_test_case)
        decoded_test_case = decode_yaml(encoded_test_case)
        assert decoded_test_case == test_case
    else:
        pytest.skip("No YAML support")


@pytest.mark.parametrize(
    "test_case",
    NATIVE_CASES,
    ids = [f"NATIVE_CASES[{i}]" for i in range(len(NATIVE_CASES))]
)
def test_yaml_pretty_roundtrip(test_case):
    if HAVE_YAML:
        encoded_test_case = pretty_yaml(test_case)
        assert isinstance(encoded_test_case, str)
        assert bool(encoded_test_case)
        decoded_test_case = decode_yaml(encoded_test_case)
        assert decoded_test_case == test_case
    else:
        pytest.skip("No YAML support")


def test_yaml_register_type():

    if HAVE_YAML:
        class T:
            def __init__(self, data: Dict[str, Any]):
                self.a = data.get('a', None)
                self.b = data.get('b', None)
                self.c = data.get('c', None)

            def to_dict(self) -> Dict[str, Any]:
                rv = dict()
                if self.a is not None:
                    rv['a'] = self.a
                if self.b is not None:
                    rv['b'] = self.b
                if self.c is not None:
                    rv['c'] = self.c
                return rv

        def encode_t(t: T) -> Dict[str, Any]:
            return t.to_dict()

        def decode_t(data: Dict[str, Any]) -> T:
            return T(data)

        register_yaml_type(T, encode_t, decode_t, key='special')

        t = decode_yaml(
            '\n'.join([
                '--- !special',
                'a: 1',
                'b: 2'
            ])
        )
        assert isinstance(t, T)
        assert t.to_dict() == {'a': 1, 'b': 2}
        assert t.c is None

        t2 = T(data = {'a': 7, 'b': 8, 'c': 9})
        print(f">>>{encode_yaml(t2)}<<<")
        assert encode_yaml(t2) == '--- !special\na: 7\nb: 8\nc: 9\n'

    else:
        pytest.skip("No YAML support")
