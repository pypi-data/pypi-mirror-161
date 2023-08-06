#!/bin/false
# -*- coding: utf-8 -*-

""" Tolls for JSON and YAML encoding/decoding. """


# ------------------------------------------------------------------------------------------------------------------------
# Main imports
# ------------------------------------------------------------------------------------------------------------------------
import datetime
from io import FileIO
import json
import os
from types import ModuleType
from typing import Any, Callable, Union, IO, Optional, Pattern
from ptutils.typing import is_mapping, is_sequence

# ------------------------------------------------------------------------------------------------------------------------
# Import checks
# ------------------------------------------------------------------------------------------------------------------------
try:
    import yaml
    HAVE_YAML = True
except ImportError:  # pragma: no cover
    HAVE_YAML = False

if HAVE_YAML:
    try:
        from yaml import CLoader as YamlLoader, CDumper as YamlDumper
    except ImportError:
        from yaml import Loader as YamlLoader, Dumper as YamlDumper

# ------------------------------------------------------------------------------------------------------------------------
# Debug functions
# ------------------------------------------------------------------------------------------------------------------------
"""
Global flag for whether or not to log encoding error debugging info when encoding fails.
This is initialized with the content of environment variable 'PTUTILS_ENABLE_ENCODER_DEBUG'.
"""
PTUTILS_ENABLE_ENCODER_DEBUG = (
    os.environ.get('PTUTILS_ENABLE_ENCODER_DEBUG', '').lower()
    in
    ['yes', 'true', 'on', 'enabled']
)


# ------------------------------------------------------------------------------------------------------------------------
def debug_encoder_failure(obj: Any) -> None:

    if PTUTILS_ENABLE_ENCODER_DEBUG:  # pragma: no cover
        # dont create a logger unless we need it...
        from ptutils.logging import getLogger
        logger = getLogger(__name__)

        # dump some useful information about the failure
        try:
            logger.debug('#' * 80)
            logger.debug('# JSON Encoding error. Unable to encode object as JSON.')
            logger.debug("# Object details:")
            logger.debug("#   class name:     %s" % type(obj).__name__)
            logger.debug("#   Representation: %s" % repr(obj))
            logger.debug("#   String:         %s" % str(obj))
            logger.debug('#' * 80)
        except:  # noqa E722 # pylint: disable=broad-except
            logger.exception("Error debugging object JSON serialization failure.")


# ------------------------------------------------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------------------------------------------------
def json_serial(obj: Any) -> Any:
    """
    JSON serialization helper for objects not serializable by default.

    Parameters
    ----------
    obj : Any
        The object to be serialized

    Returns
    -------
    Any
        An object which is serializable by the `json` python standard library.

    Raises
    ------
    TypeError
        If the object could not be converted to a serializable type.

    Notes
    -----
    This function provides serialization for `datetime.datetime`,
    `datetime.timedelta`, and `datetime.date`.
    For other types, a TypeError will be raised, and some debugging information
    about the encoding failure will be logged using `logger.debug`.

    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
        return obj.total_seconds()

    debug_encoder_failure(obj)

    raise TypeError(f"Type {type(obj).__name__} not serializable.")


# ------------------------------------------------------------------------------------------------------------------------
def encode_json(obj: Any) -> str:
    """
    Encode the object as a JSON string

    Parameters
    ----------
    obj : Any
        The object to encode

    Returns
    -------
    str
        A JSON string representation of the object.
    """
    return json.dumps(obj, sort_keys=True, indent=4, separators=[', ', ': '], default=json_serial)


# ------------------------------------------------------------------------------------------------------------------------
def pretty_json(obj: Any) -> str:
    """
    Encode the object as a JSON string in human-friendly format.

    Parameters
    ----------
    obj : Any
        The object to encode

    Returns
    -------
    str
        A JSON string representation of the object.
    """
    return encode_json(obj)


# ------------------------------------------------------------------------------------------------------------------------
def decode_json(text: str) -> Any:
    """
    Encode a JSON string into a python object.

    Parameters
    ----------
    text : str
        The JSON text to parse.

    Returns
    -------
    Any
        The decoded object.
    """
    return json.loads(text)


# ------------------------------------------------------------------------------------------------------------------------
def require_yaml() -> ModuleType:
    """
    Ensure that YAML encoder is installed or else raise an exception.

    Returns
    -------
    ModuleType
        The yaml module itself.

    Raises
    ------
    Exception
        When YAML encoder can not be imported.
    """
    if not HAVE_YAML:  # pragma: no cover
        raise Exception("YAML encoder is not available. Try 'pip install pyyaml'")

    return yaml


# ------------------------------------------------------------------------------------------------------------------------
def decode_yaml(text_or_stream: Union[str, IO]) -> Any:
    """
    Decode a YAML string into a python object.

    Parameters
    ----------
    text_or_stream : Union[str, IO]
        Either a string literal containing YAML formatted markup, or an object
        providing the stream protocol whose contents will be read and then parsed.

    Returns
    -------
    Any
        The python object described by the yaml text.

    Raises
    ------
    Exception
        When YAML encoder can not be imported.
    """
    require_yaml()
    return yaml.load(text_or_stream, Loader=YamlLoader)


# ------------------------------------------------------------------------------------------------------------------------
def encode_yaml(obj: Any, filp: Optional[FileIO] = None) -> str:
    """
    Serialize an object to a YAML-formatted string.

    Parameters
    ----------
    obj : Any
        The object to be serialized.
    filp : FileIO, optional
        A file to write to insetead of returning a string

    Returns
    -------
    str
        The YAML-formatted string representation of `obj`

    Raises
    ------
    Exception
        When YAML encoder can not be imported.
    """
    require_yaml()
    if filp is not None:
        return yaml.dump(obj, filp, explicit_start=True, default_flow_style=False, Dumper=YamlDumper)
    else:
        return yaml.dump(obj, explicit_start=True, default_flow_style=False, Dumper=YamlDumper)


# ------------------------------------------------------------------------------------------------------------------------
def pretty_yaml(obj: Any) -> str:
    """
    Serialize an object to a human-friendly, YAML-formatted string.

    Parameters
    ----------
    obj : Any
        The object to be serialized.

    Returns
    -------
    str
        The YAML-formatted string representation of `obj`

    Raises
    ------
    Exception
        When YAML encoder can not be imported.
    """
    return encode_yaml(obj)


# ------------------------------------------------------------------------------------------------------------------------
def _yaml_auto_represent(dumper: Any, tag: str, data: Any) -> Any:
    """
    Automatically represent either a scalar, a sequence, or a mapping.

    Parameters
    ----------
    dumper : Any
        The yaml dumper.
    tag : str
        The tag to use for the node.
    data : Any
        The data to represent.

    Returns
    -------
    Any
        The result of calling dumper.represent_scalar(tag, data) for scalars,
        dumper.represent_sequence(tag, data) for sequences, or
        dumper.represent_mapping(tag, data) for mappings.
    """
    require_yaml()
    from yaml import BaseDumper
    dumper: BaseDumper = dumper

    if is_sequence(data):
        return dumper.represent_sequence(tag, data)
    elif is_mapping(data):
        return dumper.represent_mapping(tag, data)
    else:
        return dumper.represent_scalar(tag, data)


# ------------------------------------------------------------------------------------------------------------------------
def _yaml_auto_construct(loader: Any, node: Any) -> Any:
    """
    Automatically construct the appropriate structure based on node type.

    Parameters
    ----------
    loader : yaml.BaseLoader
        The YAML loader object
    node : yaml.Node
        The node to construct.

    Returns
    -------
    Any
        The result of calling loader.construct_scalar(node) for scalars,
        loader.construct_sequence(node) for sequences, or
        loader.construct_mapping(node) for mappings.
    """
    require_yaml()
    from yaml import SequenceNode, MappingNode, Node, BaseLoader
    loader: BaseLoader = loader
    node:   Node       = node

    if isinstance(node, SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, MappingNode):
        return loader.construct_mapping(node)
    else:
        return loader.construct_scalar(node)


# ------------------------------------------------------------------------------------------------------------------------
def register_yaml_type(
    klass:       type,
    encoder:     Callable[[Any], Any],
    decoder:     Callable[[Any], Any],
    key:         Optional[str]     = None,
    resolver:    Optional[Pattern] = None,
):
    """
    Register a class for YAML loading/dumping.

    Parameters
    ----------
    klass : type
        The class to register.
    encoder : Callable[[Any], Any]
        A method which takes an instance of the class and returns either a
        scalar, a sequence, or a mapping.
    decoder : Callable[[Any], Any]
        A method which takes the result of the encoder and instantiates an
        instance of the class.
    key : Optional[str], optional
        YAML tag to use (less leading '!'), by default will be lowercase name of class.
    resolver : Pattern, optional
        A regular expression to use to enable implicit construction, by default None.
        When omitted no implicit resolver will be defined.
        Note: for large documents, implicit resolvers can seriously degrade performance.
    """
    require_yaml()
    key = key or klass.__name__.lower()
    tag = f'!{key}'
    YamlDumper.add_representer(
        klass,
        lambda dumper, data: _yaml_auto_represent(dumper, tag, encoder(data))
    )
    YamlLoader.add_constructor(
        tag,
        lambda loader, node: decoder(_yaml_auto_construct(loader, node))
    )
    if resolver:
        YamlLoader.add_implicit_resolver(tag, resolver)
