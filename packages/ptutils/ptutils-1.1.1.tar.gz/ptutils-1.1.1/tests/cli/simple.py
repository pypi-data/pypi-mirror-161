#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines unit tests for `ptutils.cli.simple`.
"""
import pytest
import argparse
from ptutils.cli.simple import (
    _arg_name,
    arg,
    get_command,
    run_command,
    shared_arg,
    use_shared_arg,
    shared_arg_exists,
    remove_shared_arg,
    arg_group,
    use_arg_group,
    arg_group_exists,
    remove_arg_group,
    command,
    command_exists,
    remove_command,
    get_argument,
    has_argument,
    _resolve_command,
    _resolve,
    _walk_argument_specs,
    get_args_parser
)


# ------------------------------------------------------------------------------------------------------------------------
def test_double_decorate_raises():
    try:
        with pytest.raises(Exception) as _:
            @command
            @command
            def my_command():
                pass
    finally:
        remove_command('my_command')
        assert not command_exists('my_command')


# ------------------------------------------------------------------------------------------------------------------------
def test_duplicate_arg_group_raises():
    try:
        @arg_group
        def fruits():
            pass
        assert arg_group_exists('fruits')

        with pytest.raises(Exception) as _:
            @arg_group  # noqa: F811
            def fruits():
                pass

    finally:
        remove_arg_group('fruits')
        assert not arg_group_exists('fruits')


# ------------------------------------------------------------------------------------------------------------------------
def test_mixing_command_and_arg_group_raises():
    try:
        with pytest.raises(Exception) as _:
            @command  # noqa: F811
            @arg_group
            def fruits():
                pass

    finally:
        remove_arg_group('fruits')
        assert not arg_group_exists('fruits')

    try:
        with pytest.raises(Exception) as _:
            @arg_group
            @command
            def my_command():
                pass

    finally:
        remove_command('my_command')
        assert not command_exists('my_command')


# ------------------------------------------------------------------------------------------------------------------------
def test_removing_nonexistent_raises():
    with pytest.raises(Exception) as _:
        remove_shared_arg('DNE')

    with pytest.raises(Exception) as _:
        remove_arg_group('DNE')

    with pytest.raises(Exception) as _:
        remove_command('DNE')

    with pytest.raises(ValueError) as _:
        get_argument('DNE', 'whatever')


# ------------------------------------------------------------------------------------------------------------------------
def test_arg_not_present_returns_none():
    try:
        @command
        def my_command():
            pass

        assert get_argument(my_command, 'DNE') is None
        assert get_argument('my_command', 'DNE') is None

    finally:
        remove_command('my_command')
        assert not command_exists('my_command')

    try:
        @arg_group
        def fruits():
            pass

        assert get_argument(fruits, 'DNE') is None
        assert get_argument('fruits', 'DNE') is None

    finally:
        remove_arg_group(fruits)
        assert not arg_group_exists('fruits')


# ------------------------------------------------------------------------------------------------------------------------
def test_arg_on_undecorated_raises():
    with pytest.raises(Exception) as _:
        @arg('-f', dest='free', action='store_true')
        def undecorated():
            pass


# ------------------------------------------------------------------------------------------------------------------------
def test_use_arg_group_on_undecorated_raises():
    try:
        with pytest.raises(Exception) as _:
            @arg_group
            def fruits():
                pass

            @use_arg_group('fruits')
            def undecorated():
                pass
    finally:
        remove_arg_group('fruits')
        assert not arg_group_exists('fruits')


# ------------------------------------------------------------------------------------------------------------------------
def test_invoking_arg_group_func_raises():
    try:
        @arg_group
        def fruits():
            pass

        with pytest.raises(Exception) as _:
            fruits()

    finally:
        remove_arg_group('fruits')
        assert not arg_group_exists('fruits')


# ------------------------------------------------------------------------------------------------------------------------
def test_shared_arg_func_raises():
    try:
        cherry = shared_arg('-c', '--cherry', dest='cherry')

        with pytest.raises(Exception) as _:
            cherry()

    finally:
        remove_shared_arg('cherry')
        assert not shared_arg_exists(cherry)


# ------------------------------------------------------------------------------------------------------------------------
def test_resolve_none_raises():
    with pytest.raises(TypeError) as _:
        _resolve(None)


# ------------------------------------------------------------------------------------------------------------------------
def test_resolve_command_none_raises():
    with pytest.raises(TypeError) as _:
        _resolve_command(None)


# ------------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def arg_group_fruits():
    @arg("--cherry")
    @arg("--banana")
    @arg("--apple")
    @arg_group
    def fruits():
        pass

    yield fruits

    remove_arg_group('fruits')


# ------------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def arg_group_veggies():
    @arg("--carrots")
    @arg("--broccoli")
    @arg("--asparagus")
    @arg_group
    def veggies():
        pass

    yield veggies

    remove_arg_group('veggies')


# ------------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def arg_group_meats():
    anchovies = shared_arg("--anchovies")
    bacon = shared_arg("--bacon")
    _ = shared_arg("--chicken")

    @use_shared_arg(anchovies)
    @use_shared_arg(bacon)
    @use_shared_arg('chicken')
    @arg_group
    def meats():
        pass

    yield meats

    remove_arg_group('meats')
    remove_shared_arg('anchovies')
    remove_shared_arg('bacon')
    remove_shared_arg('chicken')


# ------------------------------------------------------------------------------------------------------------------------
COOK_CALLED_MARKER = []


# ------------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def hierarchical_cli(arg_group_fruits, arg_group_veggies, arg_group_meats):
    global COOK_CALLED_MARKER
    COOK_CALLED_MARKER = []

    @use_arg_group('fruits')
    @use_arg_group('veggies')
    @use_arg_group('meats')
    @command
    def cook(**kwargs):
        global COOK_CALLED_MARKER
        COOK_CALLED_MARKER.append(kwargs)

    yield cook

    remove_command('cook')
    COOK_CALLED_MARKER = []


# ------------------------------------------------------------------------------------------------------------------------
HIERARCHICAL_CLI_SPECS = dict(
    (name, {"kind": "arg", "name": name, "args": tuple([f"--{name}"]), "kwargs": {}})
    for name in [
        'apple',
        'banana',
        'cherry',
        'asparagus',
        'broccoli',
        'carrots',
        'anchovies',
        'bacon',
        'chicken'
    ]
)


# ------------------------------------------------------------------------------------------------------------------------
def test_args_parser(hierarchical_cli):
    p = get_args_parser(
        program = "program",
        version = "version",
        copyright_message = "(C) Someone, 1984."
    )
    assert isinstance(p, argparse.ArgumentParser)
    args = p.parse_args(
        [
            "cook",
            "--apple", "granny-smith",
            "--banana", "cavendish",
            "--cherry", "bing",

            "--asparagus", "skinny",
            "--broccoli",  "green",
            "--carrots",   "pointy",

            "--anchovies", "sea",
            "--bacon",     "land",
            "--chicken",   "sky"
        ]
    )
    assert args.apple     == "granny-smith"
    assert args.banana    == "cavendish"
    assert args.cherry    == "bing"
    assert args.asparagus == "skinny"
    assert args.broccoli  == "green"
    assert args.carrots   == "pointy"
    assert args.anchovies == "sea"
    assert args.bacon     == "land"
    assert args.chicken   == "sky"

    p2 = get_args_parser(
        program = "dfsadfas",
        version = "fasdfsadf",
        copyright_message = "asdfasdf"
    )
    assert p2 is p


# ------------------------------------------------------------------------------------------------------------------------
def test_run_command(hierarchical_cli):
    global COOK_CALLED_MARKER
    assert len(COOK_CALLED_MARKER) == 0

    rc = run_command(
        args = [
            "cook",
            "--apple", "granny-smith",
            "--banana", "cavendish",
            "--cherry", "bing",

            "--asparagus", "skinny",
            "--broccoli",  "green",
            "--carrots",   "pointy",

            "--anchovies", "sea",
            "--bacon",     "land",
            "--chicken",   "sky"
        ],
        program = "program",
        version = "version",
        copyright_message = "(C) Someone, 1984."
    )
    assert rc == 0
    assert len(COOK_CALLED_MARKER) == 1
    assert isinstance(COOK_CALLED_MARKER[0], dict)
    args = COOK_CALLED_MARKER[0]

    assert args['apple']     == "granny-smith"
    assert args['banana']    == "cavendish"
    assert args['cherry']    == "bing"
    assert args['asparagus'] == "skinny"
    assert args['broccoli']  == "green"
    assert args['carrots']   == "pointy"
    assert args['anchovies'] == "sea"
    assert args['bacon']     == "land"
    assert args['chicken']   == "sky"


# ------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["var_name", "var_spec"],
    argvalues = HIERARCHICAL_CLI_SPECS.items(),
    ids       = [ f"{k}->{v}" for (k, v) in HIERARCHICAL_CLI_SPECS.items() ]
)
def test_walk_argument_specs(hierarchical_cli, var_name, var_spec):
    assert get_argument(hierarchical_cli, var_name) == var_spec

    for spec in _walk_argument_specs(hierarchical_cli):
        if _resolve(_arg_name) == spec['name']:
            assert spec == var_spec


# ------------------------------------------------------------------------------------------------------------------------
def test_walk_argument_bad_subject_raises():
    with pytest.raises(ValueError) as _:
        for __ in _walk_argument_specs(None):
            pass


# ------------------------------------------------------------------------------------------------------------------------
BAD_CMD_INFO_TYPE_CASES = [
    (None, ), ("None", ), ([], ), (True, ), (False, )
]


# ------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["cmd_info"],
    argvalues = BAD_CMD_INFO_TYPE_CASES,
    ids       = [ f"{x}" for x in BAD_CMD_INFO_TYPE_CASES ]
)
def test_cmd_info_not_mapping_raises(cmd_info):

    def f_bad_cmd_info():
        pass

    f_bad_cmd_info.cmd_info = None
    with pytest.raises(ValueError) as _:
        for __ in _walk_argument_specs(f_bad_cmd_info):
            pass


# ------------------------------------------------------------------------------------------------------------------------
MALFORMED_CMD_INFO_CASES = [
    ({}, ValueError),                                                     # arg info not present
    ({'arg_info': None}, RuntimeError),                                   # arg info not a mapping or list of mappings
    ({'arg_info': [{}]}, ValueError),                                     # no kind field
    ({'arg_info': [{'kind': 'arg_group'}]}, Exception),                  # no name specified in arg group
    ({'arg_info': [{'kind': 'arg_group', 'name': 'DNE'}]}, Exception),   # arg group name does not exist
]


# ------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    argnames  = ["cmd_info", "exception"],
    argvalues = MALFORMED_CMD_INFO_CASES,
    ids       = [ f"{x}" for x in MALFORMED_CMD_INFO_CASES ]
)
def test_malformed_cmd_info_raises(cmd_info, exception):

    def f_bad_cmd_info():
        pass

    f_bad_cmd_info.__cmd_info__ = cmd_info

    with pytest.raises(exception) as _:
        for __ in _walk_argument_specs(f_bad_cmd_info):
            pass


# ------------------------------------------------------------------------------------------------------------------------
def test_no_arg_positionals_raises():
    try:
        with pytest.raises(Exception) as _:
            @arg()
            @command
            def my_command():
                pass
    finally:
        remove_command('my_command')
        assert not command_exists('my_command')


# ------------------------------------------------------------------------------------------------------------------------
def test_using_unknown_arg_group_raises():
    try:
        with pytest.raises(Exception) as _:
            @use_arg_group('DNE')
            @command
            def my_command():
                pass
    finally:
        remove_command('my_command')
        assert not command_exists('my_command')


# ------------------------------------------------------------------------------------------------------------------------
def test_indeterminate_arg_name_raises():
    try:
        with pytest.raises(Exception) as _:
            @arg()
            @command
            def my_command():
                pass
    finally:
        remove_command('my_command')
        assert not command_exists('my_command')


# ------------------------------------------------------------------------------------------------------------------------
def test_cli_simple_create_command():
    """ Test ability to create a command using the `ptutils.cli.simple.command` decorator. """
    with pytest.raises(Exception) as _:
        get_command('my_command')

    try:
        @command
        def my_command():
            pass
        assert command_exists('my_command')
        assert get_command('my_command') is not None

    finally:
        remove_command('my_command')
        assert not command_exists('my_command')


# ------------------------------------------------------------------------------------------------------------------------
def test_cli_simple_create_arg_group():
    """ Test ability to create an argument group using the `ptutils.cli.simple.arg_group` decorator. """
    try:
        @arg_group
        def fruits():
            pass
        assert arg_group_exists('fruits')
    finally:
        remove_arg_group('fruits')
        assert not arg_group_exists('fruits')


# ------------------------------------------------------------------------------------------------------------------------
def test_cli_simple_create_shared_arg():
    """ Test ability to create a shared argument using the `ptutils.cli.simple.shared_arg` function. """
    try:
        sa = shared_arg(
            '-w', '--whatchamacallits',
            dest = "whatchamacallits"
        )
        assert shared_arg_exists('whatchamacallits')
        assert shared_arg_exists(sa)

    finally:
        remove_shared_arg(sa)
        assert not shared_arg_exists('whatchamacallits')


# ------------------------------------------------------------------------------------------------------------------------
def test_resolve_shared_arg_func_returns_name():
    try:
        sa = shared_arg('-s', '--shared')
        assert sa.__name__ == 'shared'
        assert _resolve(sa) == 'shared'

    finally:
        remove_shared_arg(sa)
        assert not shared_arg_exists('whatchamacallits')


# ------------------------------------------------------------------------------------------------------------------------
def test_cli_simple_use_shared_arg():
    """ Test ability to use a shared argument using the `ptutils.cli.simple.use_shared_arg` function. """
    try:
        # define shared arg
        batch = shared_arg(
            '-b', '--batch',
            metavar = "BATCH_SIZE",
            help = "Batch size"
        )

        # define command using shared arg
        @use_shared_arg('batch')
        @command
        def my_command(batch: int = 5):
            assert batch == 25

        # check
        assert shared_arg_exists('batch')
        assert shared_arg_exists(batch)
        assert command_exists('my_command')
        assert command_exists(my_command)
        assert get_argument('my_command', 'batch') == {
            "kind":   "arg",
            "args":   tuple(['-b', '--batch']),
            "kwargs": {
                "metavar": "BATCH_SIZE",
                "help": "Batch size"
            },
            "name": "batch"
        }
        assert get_argument('my_command', batch) == {
            "kind":   "arg",
            "args":   tuple(['-b', '--batch']),
            "kwargs": {
                "metavar": "BATCH_SIZE",
                "help": "Batch size"
            },
            "name": "batch"
        }
        assert has_argument(my_command, batch)
        assert has_argument('my_command', 'batch')

    finally:
        # cleanup
        remove_command('my_command')
        remove_shared_arg(batch)

        assert not command_exists('my_command')
        assert not shared_arg_exists('batch')


# ------------------------------------------------------------------------------------------------------------------------
def test_cli_simple():
    """ Tests many functions of the simple cli system together. """
    try:
        # define a fruits arguments group
        @arg(
            '-b', '--banana',
            help    = 'Yummy yellow fruit',
            dest    = 'banana',
            metavar = 'BANANA',
            default = 'banana'
        )
        @arg(
            '-c', '--cherry',
            help    = 'Yummy red fruit',
            dest    = 'cherry',
            metavar = 'CHERRY',
            default = 'cherry'
        )
        @arg_group
        def fruits():
            pass

        # define a vegetables arguments group
        @arg(
            '-s', '--squash',
            help    = 'Yucky green vegetable',
            dest    = 'squash',
            metavar = 'SQUASH',
            default = 'squash'
        )
        @arg(
            '-t', '--tomato',
            help    = 'Yummy red vegetable',
            dest    = 'tomato',
            metavar = 'TOMATO',
            default = 'tomato'
        )
        @arg_group
        def vegetables():
            pass

        # define a produce arguments group
        @use_arg_group('fruits')
        @use_arg_group('vegetables')
        @arg_group
        def produce():
            pass

        # define a shared argument
        shared_arg(
            '-w', '--whatchamacallits',
            dest = "whatchamacallits"
        )

        # define a command using shared argument, argument group, and some directly defined arguments
        @use_shared_arg('whatchamacallits')
        @use_arg_group('produce')
        @arg(
            '-p', '--prefix',
            help    = 'Folder prefix',
            dest    = 'prefix',
            metavar = 'FOLDER',
            default = '/tmp'
        )
        @arg(
            '-f', '--force',
            help    = 'When present, ignore cached results and perform all actions again.',
            dest    = 'force',
            action  = 'store_true',
            default = False
        )
        @command
        def my_command(prefix: str, force: bool, **kwargs) -> None:
            print("I'm now running stuff!")

        assert arg_group_exists('fruits')
        assert has_argument('fruits', 'cherry')
        assert has_argument('fruits', 'banana')

        assert arg_group_exists('vegetables')
        assert has_argument('vegetables', 'squash')
        assert has_argument('vegetables', 'tomato')

        assert arg_group_exists('produce')
        assert has_argument(produce, 'cherry')
        assert has_argument('produce', 'banana')
        assert get_argument(produce, 'squash') is not None
        assert get_argument('produce', 'tomato') is not None

        assert shared_arg_exists('whatchamacallits')
        assert command_exists('my_command')

        assert has_argument('my_command', 'whatchamacallits')
        assert has_argument('my_command', 'cherry')
        assert has_argument('my_command', 'banana')
        assert has_argument('my_command', 'squash')
        assert has_argument('my_command', 'tomato')
        assert has_argument('my_command', 'force')
        assert has_argument('my_command', 'prefix')

        assert get_argument('my_command', 'whatchamacallits') == {
            "kind":   "arg",
            "args":   tuple(['-w', '--whatchamacallits']),
            "kwargs": {
                "dest": "whatchamacallits"
            },
            "name": "whatchamacallits"
        }

    finally:
        remove_shared_arg('whatchamacallits')
        remove_arg_group('produce')
        remove_arg_group('vegetables')
        remove_arg_group('fruits')
        remove_command('my_command')

        assert not command_exists('my_command')
        assert not arg_group_exists('produce')
        assert not arg_group_exists('vegetables')
        assert not arg_group_exists('fruits')
        assert not shared_arg_exists('whatchamacallits')
