#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple decorator system for declaring CLI commands and their arguments.

This moduleis similar in concept to click, but with fewer features.
"""


import sys
import argparse
import functools
import datetime
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple, Union

from ptutils.undefined import UNDEFINED, is_undefined, is_defined, default_if_undefined
from ptutils.typing import is_sequence, is_mapping
from ptutils.encoding import encode_json
from ptutils.punning import listify
from ptutils.logging import getLogger, set_verbosity, DEFAULT_VERBOSITY

# ------------------------------------------------------------------------------------------------------------------------
# Logging config
# ------------------------------------------------------------------------------------------------------------------------
logger = getLogger(__name__)


# ------------------------------------------------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------------------------------------------------
""" The global registry of argument groups. """
__ARG_GROUPS__ = dict()

""" The global registry of command line commands. """
__COMMANDS__   = dict()


# ------------------------------------------------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------------------------------------------------
def normalize_command_name(name: str) -> str:
    """
    Normalize a function name to produce the corresponding command name.

    Parameters
    ----------
    name : str
        The function name.

    Returns
    -------
    str
        The function name converted to lowecase with underscores replaced with hyphens
        and leading/trailing, or repeated hyphens removed.
    """
    name_  = name.lower().replace('_', '-')
    parts_ = [ x for x in name_.split('-') if x ]
    rv     = '-'.join( parts_ )
    return rv


# ------------------------------------------------------------------------------------------------------------------------
def _normalize_arg_name(name: str) -> str:
    """
    Return the normalized argument name of a given string.

    Parameters
    ----------
    name : str
        [description]

    Returns
    -------
    str
        The normalized name.

    Examples
    --------

    >>> _normalize_arg_name('-d')
    d
    >>> _normalize_arg_name('--debug-XyZ')
    debug_XyZ
    >>> _normalize_arg_name('---------a--b--c--------')
    a_b_c

    """

    name = name.lstrip('-').replace('-', '_')
    name = '_'.join([ x for x in name.split('_') if x])
    return name


# ------------------------------------------------------------------------------------------------------------------------
def _arg_name(args: Tuple[Any], kwargs: Dict[str, Any]) -> str:
    """
    Determine an argument's name based on specification
    (`argparse.ArgumentParser.add_argument` arguments).

    Parameters
    ----------
    args : Tuple[Any]
        The argument specification's positional arguments.
    kwargs : [type]
        The argument specification's keyword arguments.

    Returns
    -------
    str
        The resulting name (dest) of the argument.

    Raises
    ------
    Exception
        If no name can be determined.

    Notes
    -----
        This will produce the argument name by first looking for a 'dest' keyword
        argument. If not found, this will look at positional arguments beginning
        with '--' then those beginning with '-'. The positional arguments will have
        hyphens replaced with underscores, and leading/trailing/duplicate
        underscores removed.

    """

    name = kwargs.get('dest', UNDEFINED)
    if is_defined(name):
        return name

    # get positional arguments which may specify argument name (strings starting with hyphens)
    nd = [x for x in args if isinstance(x, str) and not x.startswith('-')]
    dd = [x for x in args if isinstance(x, str) and x.startswith('--')]
    sd = [x for x in args if isinstance(x, str) and x.startswith('-') and (x not in dd)]
    _d = nd + dd + sd

    # ensure there's at least one positional argument we could use to set the name.
    if not _d:
        raise Exception(
            "Can not determine shared argument name from supplied "
            f"arguments: args={args}, kwargs={kwargs}"
        )

    # select the first item in the list, normalize the name and return it.
    return _normalize_arg_name(_d[0])


# ------------------------------------------------------------------------------------------------------------------------
def _resolve(subject: Union[str, Callable]) -> str:
    """
    Given a string or a function, determine the name the cli simple system will use for lookups
    for shared arguments and argument groups.

    Parameters
    ----------
    subject : Union[str, Callable]
        A string or function.

    Returns
    -------
    str
        Either the string unmodified, or in the case of a callable, the callable's __name__.

    Raises
    ------
    TypeError
        When `subject` is not a string and not callable.
    """
    if callable(subject):
        return subject.__name__
    elif isinstance(subject, str):
        return subject
    else:
        raise TypeError(
            f"Object of type '{type(subject).__name__}' may not "
            "be used to reference a command, arg, arg_group, or shared_arg."
        )


# ------------------------------------------------------------------------------------------------------------------------
def _resolve_command(subject: Union[str, Callable]) -> str:
    """
    Given a string or a function, determine the name the cli simple system will use for lookups
    for commands.

    Parameters
    ----------
    subject : Union[str, Callable]
        A string or function.

    Returns
    -------
    str
        Either the string unmodified, or in the case of a callable, the callable's __name__.

    Raises
    ------
    TypeError
        When `subject` is not a string and not callable.
    """
    return normalize_command_name(_resolve(subject))


# ------------------------------------------------------------------------------------------------------------------------
def get_command(name: str) -> Callable:
    """
    Lookup a registered command.

    Parameters
    ----------
    name : str
        The command or function name. Will be normalized with `normalize_command_name` prior to searching.

    Returns
    -------
    Callable
        The function corresponding to that command, if found.

    Raises
    ------
    Exception
        When no such command name has been registered.
    """
    name_ = _resolve_command(name)
    if name_ not in __COMMANDS__:
        raise Exception(f"Unknown command: No command has been defined with name '{name_}'.")
    return __COMMANDS__[name_]


# ------------------------------------------------------------------------------------------------------------------------
def _register_arg_group(name: str, func: Callable):
    """
    Utility function to initialize an argument group on a function and register it globally.

    Parameters
    ----------
    name : atr
        The name of the argument group to add.
    func : Callable
        The function to be decorated as an argument group.

    Raises
    ------
    Exception
        If the argument group is already defined.
    Exception
        If the function is an already decorated command or argument group.
    """
    if name in __ARG_GROUPS__:
        raise Exception(f"Argument group '{name}' is already defined.")
    if hasattr(func, '__cmd_info__'):
        raise Exception(f"Registering argument group {name} on function {func.__name__} which already has metadata.")
    func.__cmd_info__ = dict(
        arg_info   = [],
        call       = lambda kwargs: func(**kwargs)
    )

    __ARG_GROUPS__[name] = func


# ------------------------------------------------------------------------------------------------------------------------
def arg_group_exists(name: Union[str, Callable]) -> bool:
    """
    Check if the named argument group exists

    Parameters
    ----------
    name : Union[str, Callable]
        The name or decorated function of the argument group

    Returns
    -------
    bool
        True if the argument group is defined.
    """
    return _resolve(name) in __ARG_GROUPS__


# ------------------------------------------------------------------------------------------------------------------------
def command_exists(name: Union[str, Callable]) -> bool:
    """
    Check if the named command exists

    Parameters
    ----------
    name : str
        The command or function name, or decorated function itself. Will be normalized
        with `normalize_command_name` prior to searching.

    Returns
    -------
    bool
        True if the command is defined.
    """
    return _resolve_command(name) in __COMMANDS__


# ------------------------------------------------------------------------------------------------------------------------
def shared_arg_exists(name: Union[str, Callable]) -> bool:
    """
    Check if the named shared argument exists

    Parameters
    ----------
    name : Union[str, Callable]
        The name of the shared argument or the return value of `shared_arg`.

    Returns
    -------
    bool
        True if the argument is defined.

    Notes
    -----
    A `shared_arg` is just a single-argument argument group of the same name. As
    such this will ALSO return True if there's an argument group by that name.
    """
    return _resolve(name) in __ARG_GROUPS__


# ------------------------------------------------------------------------------------------------------------------------
def remove_shared_arg(name: Union[str, Callable]) -> None:
    """
    Removes the shared argument definition from the global registry.
    This is useful in unit testing.

    Parameters
    ----------
    name : Union[str, Callable]
        The name of the shared argument or the return value of `shared_arg`.

    Notes
    -----
    This implementation does not remove any references to the shared
    argument, and so may entail undefined behavior if such references are
    not also cleaned up.
    """
    name_ = _resolve(name)
    if name_ in __ARG_GROUPS__:
        del __ARG_GROUPS__[name_]
    else:
        raise Exception(f"No shared arg or arg group by name '{name_}', so nothing to delete.")


# ------------------------------------------------------------------------------------------------------------------------
def remove_arg_group(name: Union[str, Callable]) -> None:
    """
    Removes the argument group definition from the global registry.
    This is useful in unit testing.

    Parameters
    ----------
    name : Union[str, Callable]
        The name or decorated function of the argument group.

    Notes
    -----
    This implementation does not remove any references to the argument
    group, and so may entail undefined behavior if such references are
    not also cleaned up.
    """
    remove_shared_arg(name)


# ------------------------------------------------------------------------------------------------------------------------
def remove_command(name: Union[str, Callable]) -> None:
    """
    Remove a command from the global list of registered commands.

    Parameters
    ----------
    name : Union[str, Callable]
        The command or function name, or decorated function itself. Will be normalized
        with `normalize_command_name` prior to searching.

    """
    name_ = _resolve_command(name)
    if name_ not in __COMMANDS__:
        raise Exception(f"No such command registered: '{name}'")
    print(f"Removing command: '{name}' ('{name_}')")
    del __COMMANDS__[name_]


# ------------------------------------------------------------------------------------------------------------------------
def get_argument(name: Union[str, Callable], argument_name: str) -> Optional[Mapping[ str, Any ]]:
    """
    Given a command or an argument group, return the specification of the named argument.

    Parameters
    ----------
    name : Union[str, Callable]
        The name or decorated function for a command or argument group.
    argument_name : str
        The argument name

    Returns
    -------
    Optional[Mapping[ str, Any ]]
        The argument spec, or None if no argument by that name was found in the argument list.

    Raises
    ------
    ValueError
        If `name` does not refer to a registered command or argument group.

    """
    name_ = _resolve(name)
    if name_ in __ARG_GROUPS__:
        func = __ARG_GROUPS__[name_]
    else:
        name_ = _resolve_command(name)
        if name_ in __COMMANDS__:
            func = __COMMANDS__[name_]
        else:
            raise ValueError(f"could not resolve '{name}' asa known command or argument group.")

    _argument_name = _resolve(argument_name)
    for spec in _walk_argument_specs(func):
        if spec['name'] == _argument_name:
            return spec

    return None


# ------------------------------------------------------------------------------------------------------------------------
def has_argument(name: Union[str, Callable], argument_name: str) -> bool:
    """
    Check if a command or argument group includes an argument with the supplied name.

    Parameters
    ----------
    name : Union[str, Callable]
        [description]
    argument_name : str
        [description]

    Returns
    -------
    bool
        [description]
    """
    return get_argument(name, argument_name) is not None


# ------------------------------------------------------------------------------------------------------------------------
def _walk_argument_specs(
    subject:       Callable,
    _group_chain:  Optional[ Iterable[ str ] ] = None
) -> Tuple[Mapping[ str, Any ], Iterable[ str ]]:
    """
    Iterate over the argument specifications for a command, argument group, or shared argument.

    Parameters
    ----------
    subparser : argparse.ArgumentParser
        The subparser for the command.
    arg_info : Union[ Iterable[ Mapping[ str, Any ] ], Mapping[ str, Any ] ]
        Argument definition metadata
    _group_chain : Optional[ Iterable[ str ] ], optional
        Recursion helper to help properly reporting errors due to usage of shared args or arg groups, by default None.

    Raises
    ------
    Exception
        When an unknown argument or argument group is referenced.
    TypeError
        When an argument specification is of an unknown object type.
    TypeError
        When an argument specification is of an invalid specification type.
    """

    # initialize the gorup chain
    _group_chain = _group_chain or []

    # ensure subject is a command or argument group
    if (
        (not callable(subject)) or
        (not hasattr(subject, '__cmd_info__'))
    ):
        raise ValueError(
            f"Object of type '{type(subject).__name__}' may not be "
            "used as a command, argument group, or shared argument."
            "Did you forget an @command, @arg_group decorator?"
        )

    # get metadata
    __cmd_info__ = subject.__cmd_info__

    # ensure argument info is available.
    if 'arg_info' not in __cmd_info__:
        raise ValueError(
            f"Argument information missing on object of type '{type(subject).__name__}."
            "Did you forget an @command, @arg_group decorator?"
        )

    # get argument info
    specs = listify(__cmd_info__['arg_info'])

    # walk the list
    for spec in specs:
        if not is_mapping(spec):
            raise RuntimeError(
                f"Object of type '{type(spec).__name__}' is "
                "not a valid argument specification."
            )

        kind = spec.get('kind', UNDEFINED)
        if kind == "arg":
            # an argument definition. yield it directly.
            yield spec

        elif kind == 'arg_group':
            # an usage definition. recurse into the named group and yield all children.

            name = spec.get('name', UNDEFINED)
            if is_undefined(name):
                raise Exception("Invalid argument group specification: missing name.")
            if name not in __ARG_GROUPS__:
                raise Exception(
                    f"Invalid argument group specification: Name '{name}' is "
                    f"not a registered argument group: {list(__ARG_GROUPS__.keys())}."
                )

            child_subject     = __ARG_GROUPS__[name]
            child_group_chain = _group_chain + [name]
            for child_spec in _walk_argument_specs(
                subject      = child_subject,
                _group_chain = child_group_chain
            ):
                yield child_spec
        else:
            raise ValueError(f"Unknown kind of argument spec: '{kind}'")


# ------------------------------------------------------------------------------------------------------------------------
# Decorators
# ------------------------------------------------------------------------------------------------------------------------
def command(func: Callable[..., None]) -> Callable[..., None]:
    """
    Decorator for marking a function as a command.

    Parameters
    ----------
    func : Callable[...,None]
        The command implementation.

    Returns
    -------
    Callable[...,None]
        The command, instrumented for calling form the command line with any
        agruments, if defined.

    Raises
    ------
    Exception
        If a command by that name is already registered, or is an argument group or
        shared argument.
    """
    name = normalize_command_name(func.__name__)

    if name in __COMMANDS__:
        raise Exception(f"Command '{name}' is already defined.")

    __COMMANDS__[name] = func

    if hasattr(func, '__cmd_info__'):
        raise Exception(f"Command '{name}' already has metadata.")
    func.__cmd_info__ = dict(
        arg_info   = [],
        call       = lambda kwargs: func(**kwargs)
    )

    return func

# def instance_command(func: Callable[...,None])->Callable[...,None]:
#     name = normalize_command_name(func.__name__)

#     if name in __COMMANDS__:
#         raise Exception(f"Command '{name}' is already defined.")

#     __COMMANDS__[name] = func

#     if hasattr(func, '__cmd_info__'):
#         raise Exception(f"Command '{name}' already has metadata.")

#     func.__cmd_info__ = dict(
#         arg_info   = [],
#         call       = lambda **kwargs: call_instance_command(func, **kwargs)
#     )

#     @classmethod
#     @functools.wraps(func)
#     def _wrapped_instance_command(cls, **kwargs):
#         instance = cls(**kwargs)
#         return func(instance)

#     return func


# ------------------------------------------------------------------------------------------------------------------------
def arg(*args, **kwargs) -> Callable:
    """
    Parametric decorator defines a command argument.

    Parameters
    ----------
    *args: Iterable[Any]
        Positional arguments supplied to `argparse.ArgumentParser.add_argument` when
        adding this argument.
    **kwargs:
        Keyword arguments supplied to `argparse.ArgumentParser.add_argument` when
        adding this argument.

    Returns
    -------
    Callable
        The command function with argument definition metadata attached.

    Raises
    ------
    Exception
        When applied to a function which is not a decorated command, or if the argument
        name is already registered.
    """
    def decorate(func: Callable) -> Callable:
        if not hasattr(func, '__cmd_info__'):
            raise Exception(
                f"Function '{func.__name__}' is not a command. "
                "Did you forget the '@command' decorator?"
            )

        spec = {
            "kind":   "arg",
            "args":   args,
            "kwargs": kwargs,
            "name":   _arg_name(args, kwargs)
        }
        func.__cmd_info__['arg_info'].append(spec)
        return func
    return decorate


# ------------------------------------------------------------------------------------------------------------------------
def use_arg_group(name: Union[str, Callable]) -> Callable:
    """
    Parametric decorator that adds a group of arguments to a command.

    Parameters
    ----------
    name : str
        The name of the argument group (defined elswhere with `arg_group` decorator).

    Returns
    -------
    Callable
        A decorator which injects the collected argument definition to the decorated
        function's metadata.
    """

    def decorate(func: Callable) -> Callable:
        """
        Internal decorator for `use_arg_group` that injects argument group usage
        details into decorated command metadata.

        Parameters
        ----------
        func : Callable
            The decorated function

        Returns
        -------
        Callable
            The function with argument group metadata injected.
        """
        name_ = _resolve(name)
        if name_ not in __ARG_GROUPS__:
            raise Exception(f"Unknown argument group or shared argument: '{name}'")
        spec = {
            "kind":   "arg_group",
            "name":   name_
        }

        func.__cmd_info__['arg_info'].append( spec )
        return func
    return decorate


# ------------------------------------------------------------------------------------------------------------------------
def use_shared_arg(name: str) -> Callable:
    """
    Parametric decorator that allows sharing of argument defined elsewhere with `shared_arg`.

    Parameters
    ----------
    name : str
        The name of the argument.

    Returns
    -------
    Callable
        A decorator which injects the argument definition to the decorated
        function's metadata.
    """
    return use_arg_group(name)


# ------------------------------------------------------------------------------------------------------------------------
def arg_group(func):
    """
    Decorator which defines an argument group.

    Parameters
    ----------
    func : [type]
        [description]

    Returns
    -------
    Callable
        The decorated function with argument metadata injected.

    Raises
    ------
    Exception
        If the decorated function is already a command or argument group, or if the
        argument group name matches an already defined shared argument name.

    Notes
    -----
    The decorated function should have an empty body.
    Calling the decorated function directly may yield undefined behavior.

    Examples
    --------

    >>> @arg('-n', '--number', dest="The number of the counting?", metavar="COUNT", default=3, type=int)
    ... @arg_group
    ... def thing_counts(): pass
    >>> @use_arg_group('thing_counts')
    ... @command
    ... def count_things( thing_counts: int) -> int:
    ...    return thing_counts

    """

    name = func.__name__

    @functools.wraps(func)
    def __cli_internal__(**kwargs):
        raise Exception("An arg group is not callable")

    _register_arg_group(name, __cli_internal__)
    return __cli_internal__


# ------------------------------------------------------------------------------------------------------------------------
# Non-decorator declarations
# ------------------------------------------------------------------------------------------------------------------------
def shared_arg(*args, **kwargs) -> None:
    """
    Define a shared argument.

    Parameters
    ----------
    *args: Iterable[Any]
        Positional arguments supplied to `argparse.ArgumentParser.add_argument` when adding this argument.
    **kwargs:
        Keyword arguments supplied to `argparse.ArgumentParser.add_argument` when adding this argument.

    Raises
    ------
    Exception
        If the argument name can not be determined.
    Exception
        If an argument or argument group by that name already exists.
    """

    name = _arg_name(args, kwargs)

    def __cli_internal__():
        raise Exception("An arg group is not callable")
    __cli_internal__.__name__ = name

    _register_arg_group(name, __cli_internal__)
    spec = {
        "kind":   "arg",
        "args":   args,
        "kwargs": kwargs,
        "name":   name
    }
    __cli_internal__.__cmd_info__['arg_info'].append(spec)

    return __cli_internal__


# ------------------------------------------------------------------------------------------------------------------------
# Entrypoint utility functions
# ------------------------------------------------------------------------------------------------------------------------
def add_command_subparser_args(
    subparser:     argparse.ArgumentParser,
    arg_info:      Union[ Iterable[ Mapping[ str, Any ] ], Mapping[ str, Any ] ],
    _group_chain:  Optional[ Iterable[ str ] ] = None
) -> None:
    """
    Add arguments for a command's subparser based on metadata attached to the decorated function.

    Parameters
    ----------
    subparser : argparse.ArgumentParser
        The subparser for the command.
    arg_info : Union[ Iterable[ Mapping[ str, Any ] ], Mapping[ str, Any ] ]
        Argument definition metadata
    _group_chain : Optional[ Iterable[ str ] ], optional
        Recursion helper to help properly reporting errors due to usage of shared args or arg groups, by default None.

    Raises
    ------
    Exception
        When an unknown argument or argument group is referenced.
    TypeError
        When an argument specification is of an unknown object type.
    TypeError
        When an argument specification is of an invalid specification type.
    """
    _group_chain = _group_chain or []
    if is_sequence(arg_info):
        for spec in arg_info:
            add_command_subparser_args(
                subparser,
                arg_info     = spec,
                _group_chain = _group_chain
            )
    elif is_mapping(arg_info):
        kind = arg_info['kind']
        if kind == "arg_group":
            name = arg_info['name']
            if name not in __ARG_GROUPS__:  # pragma: no cover
                cmd = subparser.get_default('command_name')
                gcs = ' -> '.join(_group_chain)
                gcm = '' if not gcs else f" indirectly via group(s): {gcs}"
                raise Exception(f"Unknown argument group '{name}' referenced by command '{cmd}'{gcm}.")
            add_command_subparser_args(
                subparser,
                arg_info     = __ARG_GROUPS__[name].__cmd_info__['arg_info'],
                _group_chain = _group_chain + [name]
            )
        elif kind == "arg":
            args   = arg_info['args']
            kwargs = arg_info['kwargs']
            subparser.add_argument(*args, **kwargs)
        else:  # pragma: no cover
            raise Exception(f"Unknown argument spec type: '{kind}'")
    else:  # pragma: no cover
        raise TypeError(f"Invalid type for argument spec: '{type(arg_info).__name__}'")


# ------------------------------------------------------------------------------------------------------------------------
""" The main argument parser. """
__PARSER__ = None


# ------------------------------------------------------------------------------------------------------------------------
def program_defaults(
    program:           Optional[str] = None,
    version:           Optional[str] = None,
    copyright_message: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Apply default values for program, version, and copyright message to be included in cli
    application help text.

    Parameters
    ----------
    program : str, optional
        The name of the program. Defaults to `sys.argv[0]`
    version : str
        The current version of the program. Defaults to 'v?.?.?'
    copyright_message : Optional[str]
        The copyright message for the program. Defaults to '(C) copyright YEAR. All rights reserved)'

    Returns
    -------
    Tuple[str, str, str]
        The program, version, and copyright_message in a tuple in respective order.
    """
    year = datetime.datetime.utcnow().year
    if copyright_message is None:
        copyright_message = f"(C) Copyright {year}. All rights reserved."
    if version is None:
        version = "v?.?.?"
    if program is None:
        program = sys.argv[0]

    return (program, version, copyright_message)


# ------------------------------------------------------------------------------------------------------------------------
def get_args_parser(
    program:           Optional[str] = None,
    version:           Optional[str] = None,
    copyright_message: Optional[str] = None
) -> argparse.ArgumentParser:
    """
    Get the global argument parser for all registered commands and associated arguments.

    Parameters
    ----------
    program : str, optional
        The name of the program. Defaults to `sys.argv[0]`
    version : str
        The current version of the program. Defaults to 'v?.?.?'
    copyright_message : Optional[str]
        The copyright message for the program. Defaults to '(C) copyright YEAR. All rights reserved)'

    Returns
    -------
    argparse.ArgumentParser
        An argument parser which handles all commands.

    """
    global __PARSER__
    if __PARSER__ is None:

        # get the program default values
        (program, version, copyright_message) = program_defaults(
            program, version, copyright_message
        )

        # initialize the main parser
        parser = argparse.ArgumentParser(
            prog = sys.argv[0],
            description = (f"{program} v{version}"),
            epilog = copyright_message or "",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False
        )
        parser.add_argument(
            '-h', '--help',
            help    = 'Display this help information.',
            dest    = 'help',
            action  = "store_true"
        )
        subparsers = parser.add_subparsers(
            title       = 'Commands',
            description = (
                f'For help a command, type:\n\t'
                f'{sys.argv[0]} COMMAND --help.\n'
                'The following commands are supported:'
            )
        )

        for (command_name, command_function) in __COMMANDS__.items():
            # print(f"Adding the {command_name} command: {command_function.__name__}(...)")
            description  = command_function.__doc__ or f'The {command_name} command.'
            subparser = subparsers.add_parser(
                command_name,
                description = description,
                help        = description
            )
            subparser.set_defaults(
                command_name     = command_name,
                command_function = command_function,
                subparser        = subparser
            )
            subparser.add_argument(
                '-v', '--verbose',
                help    = 'Increase logging verbosity.',
                dest    = 'verbosity',
                action  = "count"
            )
            subparser.add_argument(
                '-q', '--quiet',
                help    = 'Decrease logging verbosity.',
                dest    = '__quiet',
                action  = "count"
            )
            # subparser.add_argument(
            #     '-h', '--help',
            #     help    = f"Display help for the '{command_name}' command.",
            #     dest    = 'help',
            #     action  = "store_true"
            # )
            add_command_subparser_args(
                subparser,
                command_function.__cmd_info__['arg_info']
            )

        __PARSER__ = parser

    return __PARSER__


# ------------------------------------------------------------------------------------------------------------------------
def convert_undefined_attributes_to_none( args: object ) -> None:
    """
    Change any `UNDEFINED` attributes to `None`.
    This will be modified in-place, and nothing is returned.

    Parameters
    ----------
    args : object
        An arguments object to modify.
    """
    # Convert any undefined values to None
    for (k, v) in args.__dict__.items():
        if is_undefined(v):
            args.__dict__[k] = None


# ------------------------------------------------------------------------------------------------------------------------
def apply_verbosity_args( args: object ) -> None:
    """
    Handle verbosity and quiet arguments, setting log verbosity accordingly.
    The 'verbosity' and '__quiet' arguments (which were automatically added)
    will be captured, applied, and removed from the `args` object, in-place.

    Parameters
    ----------
    args : object
        An arguments object.
    """
    # set log verbosity
    verbosity = getattr(args, 'verbosity', UNDEFINED)
    if is_defined(verbosity):  # pragma : no cover
        delattr(args, 'verbosity')
    verbosity = default_if_undefined(verbosity, 0)
    verbosity = verbosity if (verbosity is not None) else 0

    quiet     = getattr(args, '__quiet', UNDEFINED)
    if is_defined(quiet):  # pragma : no cover
        delattr(args, '__quiet')
    quiet = default_if_undefined(quiet, 0)
    quiet = quiet if (quiet is not None) else 0

    set_verbosity( DEFAULT_VERBOSITY + verbosity - quiet )


# ------------------------------------------------------------------------------------------------------------------------
def get_args(
    args:              Optional[Iterable[str]] = None,
    program:           Optional[str] = None,
    version:           Optional[str] = None,
    copyright_message: Optional[str] = None,
) -> Tuple[object, argparse.ArgumentParser]:
    """
    Get an argument parser based on all registered `command` functions, parse supplied
    arguments, and return an arguments object.

    Parameters
    ----------
    args: Iterable[str], optional
        A list of positional arguments excluding the program name, defaults to `sys.argv[1:]`
    program : str, optional
        The name of the program. Defaults to `sys.argv[0]`
    version : str
        The current version of the program. Defaults to 'v?.?.?'
    copyright_message : Optional[str]
        The copyright message for the program. Defaults to '(C) copyright YEAR. All rights reserved)'


    Returns
    -------
    Tuple[object, argparse.ArgumentParser]
        A tuple whose first element is an arguments object ( as returned by
        `argparse.ArgumentParser.parse_arguments` ) with attributes matching the registered
        argument names for the selected command, and whose second element is the argument
        parser itself.

    """
    # get the program default values
    (program, version, copyright_message) = program_defaults(
        program, version, copyright_message
    )
    if args is None:
        args = sys.argv[1:]

    # get parser
    try:
        parser = get_args_parser(
            program = program,
            version = version,
            copyright_message = copyright_message
        )
    except Exception as e:
        raise Exception("Error building parser(s).") from e

    # parse args
    try:
        args = parser.parse_args( args = args )
    except SystemExit:
        raise
    except Exception as e:  # noqa F722  # pragma : no cover
        raise Exception("Error parsing arguments.") from e

    # Convert any undefined values to None
    convert_undefined_attributes_to_none(args)

    # determine if we have a specified command
    subparser = getattr(args, 'subparser', None)
    if subparser is None:
        logger.error("No command specified")
        parser.print_help(file=sys.stderr)
        sys.exit(-1)
    delattr(args, 'subparser')

    # done. return the result
    return args, subparser


# ------------------------------------------------------------------------------------------------------------------------
def get_command_from_args(args: object) -> Tuple[Callable, str]:
    """
    Given a parsed arguments object, extract the command function and name, and
    remove those attributes from the args object, in-place.

    Parameters
    ----------
    args : object
        An arguments object.

    Returns
    -------
    Tuple[Callable, str]
        The command function and command name.
    """
    command      = args.command_function
    command_name = args.command_name
    delattr(args, 'command_function')
    delattr(args, 'command_name')
    return (command, command_name)


# ------------------------------------------------------------------------------------------------------------------------
def handle_help_flag(args: object, parser: argparse.ArgumentParser) -> None:
    """
    Explicitly handle displaying of help information for a command when
    the --help flag is specified. When present and True, the help is displayed
    and the program exits. When present and False, the help attribute is
    removed from args, in-place. When absent, no action is taken.

    Parameters
    ----------
    args : object
        An arguments object
    parser : argparse.ArgumentParser
        The argument parser.

    """
    help = getattr(args, 'help', None)
    if help is not None:
        if help:
            parser.print_help(file = sys.stderr)
            return 0
        delattr(args, 'help')


# ------------------------------------------------------------------------------------------------------------------------
def display_invocation_details(command_name: str, kwargs: Dict[str, Any]) -> None:
    """
    Display program invocation details.

    Parameters
    ----------
    command_name : str
        The selected command name.
    kwargs : Dict[str, Any]
        Parsed dictionary of command line arguments.
    """
    logger.debug('=======================================================')
    logger.debug('Command:   %s' % command_name)

    if kwargs:
        logger.debug('Arguments:')
        mk = max(len(k) for k in kwargs) + 1
        for (k, v) in kwargs.items():
            try:
                val = encode_json(v)
            except:  # noqa F722
                val = repr(v)
            logger.debug(f"  {(k+':'):{mk}} {val}")
    else:
        logger.debug('Arguments: <<< No arguments provided >>>')
    logger.debug('=======================================================')


# ------------------------------------------------------------------------------------------------------------------------
def run_command(
    args:              Optional[Iterable[str]] = None,
    program:           Optional[str] = None,
    version:           Optional[str] = None,
    copyright_message: Optional[str] = None,
) -> int:
    """
    Parse supplied command line arguments and run the corresponding command if specified.

    Parameters
    ----------
    args: Iterable[str], optional
        A list of positional arguments excluding the program name, defaults to `sys.argv[1:]`
    program : str, optional
        The name of the program. Defaults to `sys.argv[0]`
    version : str
        The current version of the program. Defaults to 'v?.?.?'
    copyright_message : Optional[str]
        The copyright message for the program. Defaults to '(C) copyright YEAR. All rights reserved)'

    Returns
    -------
    int
        The command's exit code.
    """

    try:
        args, subparser = get_args(
            args              = args,
            program           = program,
            version           = version,
            copyright_message = copyright_message
        )
    except SystemExit:
        raise
    except:  # noqa F722  # pragma : no cover
        logger.exception("Error getting program arguments")
        return -1

    # apply logging verbosity args (verbose and quiet)
    apply_verbosity_args(args)

    # get command details
    command, command_name = get_command_from_args(args)

    # get help flag
    handle_help_flag(args, subparser)

    # convert args to a dictionary
    kwargs = vars(args)

    # log command invocation arguments
    display_invocation_details(command_name, kwargs)

    # invoke the command
    try:
        rv = command.__cmd_info__['call'](kwargs)
        if rv is None:
            return 0
        return rv
    except Exception as e:
        logger.exception(f"Error while running command '{command_name}': {e}")
        subparser.print_help()
        return -1
