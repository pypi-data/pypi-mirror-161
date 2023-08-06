#!/bin/false
# -*- coding: utf-8 -*-


""" Legacy python2 file io utility functions. This module is dated and will eventually be replaced by object-oriented
versions of these utilities. """

# =======================================================================================================================
# Main imports
# =======================================================================================================================
import os
import tempfile
import errno
import hashlib
from typing import Any, Union, Callable, List
from ptutils.encoding import encode_json, decode_json, encode_yaml, decode_yaml
from ptutils.undefined import UNDEFINED, Undefined, is_undefined

# =======================================================================================================================
# Import checks
# =======================================================================================================================
try:
    import tarfile
    HAVE_TAR = True
except ImportError:  # pragma: no cover
    HAVE_TAR = False

# -----------------------------------------------------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------------------------------------------------
__FILETYPES__ = {
    'archive-zip': ['zip'],
    'archive-tar': ['tar'],
    'archive-bzip2': ['bz2'],
    'archive-gzip':  ['gz'],
    'yaml': ['yml', 'yaml'],
    'json': ['jsn', 'json']
}


# -----------------------------------------------------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------------------------------------------------
def get_path_part(filename: str, part: str) -> str:
    """
    Get the specified part of a filename.

    Parameters
    ----------
    filename : str
        The path or filename as a string.
    part : str
        The desired part. Valid part names are: 'fullpath', 'abspath', 'name', 'extension', 'basename'

    Returns
    -------
    str
        The indicated part.

    Raises
    ------
    ValueError
        If the specified part type is not one of the known types.
    """
    if part == 'fullpath':
        return filename
    elif part == 'abspath':
        return os.path.abspath(filename)
    elif part == 'name':
        return os.path.split(filename.rstrip(os.sep))[1]
    elif part == 'extension':
        (_, e) = os.path.splitext(
            os.path.split(
                filename.rstrip(os.sep)
            )[1]
        )
        return e.lstrip('.')
    elif part == 'basename':
        (b, _) = os.path.splitext(
            os.path.split(
                filename.rstrip(os.sep)
            )[1]
        )
        return b
    else:
        raise ValueError(f"Unknown filename part: '{part}'")


# ------------------------------------------------------------------------------------------------------------------------
def get_hash_tmp_dir(relpath: str) -> str:
    """
    Get a temporary directory based on a hashing of another directory name.

    Parameters
    ----------
    relpath : str
        The other directory name or path to hash.

    Returns
    -------
    str
        A temporary directory name as a string.
    """
    h = hashlib.md5(relpath.encode('utf-8')).hexdigest()
    return os.path.join( tempfile.gettempdir(), h )


# ------------------------------------------------------------------------------------------------------------------------
def get_filetype(filename: str) -> str:
    """
    Get the registered filetype based on the file's extension.

    Parameters
    ----------
    filename : str
        The path or filename.

    Returns
    -------
    str
        The registered typename. See `__FILETYPES__` for more a list of known filetypes.
    """
    global __FILETYPES__
    extension = get_path_part(filename, 'extension').lower()
    for (filetype, extensions) in __FILETYPES__.items():
        if extension in extensions:
            return filetype
    return extension.lstrip('.')


# ------------------------------------------------------------------------------------------------------------------------
def makedirs(path: str) -> None:
    """
    Create a directory, recursively creating any parents as needed.

    Parameters
    ----------
    path : str
        The path to the folder to create. When relative, it is assumed to be relative to the current
        working dir (`os.curdir`).

    Raises
    ------
    OSError
        As per `os.makedirs`, except in the case of `errno.EEXIST`, in which case no error is raised.

    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
            raise


# ------------------------------------------------------------------------------------------------------------------------
def read(filename: str) -> str:
    """
    Read the entire content of a text file.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    str
        The content of the file as a string.

    Raises
    ------
    Exception
        As per `open` or `io.TextIOBase.read`.

    """
    with open(filename, 'r') as filp:
        return filp.read()


# ------------------------------------------------------------------------------------------------------------------------
def read_lines(filename: str) -> List[str]:
    """
    Read all of the lines of a text file.

    Parameters
    ----------
    filename : str
        The path to the file.

    Returns
    -------
    List[str]
        A list of the lines in the text file.

    Raises
    ------
    Exception
        As per `open` or `io.TextIOBase.readlines`.
    """
    with open(filename, 'r') as filp:
        return [ x.rstrip('\r\n') for x in filp.readlines() ]


# ------------------------------------------------------------------------------------------------------------------------
def read_all(filename: str) -> str:
    """
    Read the entire content of a text file.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    str
        The content of the file as a string.

    Raises
    ------
    Exception
        As per `open` or `io.TextIOBase.read`.


    Notes
    -----
    This is an alias of `read`.
    """
    return read(filename)


# ------------------------------------------------------------------------------------------------------------------------
def write_all(filename: str, content: str) -> None:
    """
    Write the content of a string to a text file.

    Parameters
    ----------
    filename : str
        The name of the file.
    content: str
        The text content of the file to be written.

    Raises
    ------
    Exception
        As per `open` or `io.TextIOBase.write`.

    """
    with open(filename, 'w') as filp:
        filp.write(content)


# ------------------------------------------------------------------------------------------------------------------------
def require_tar() -> None:
    """
    Test if TarFile support is available or raise an Exception.

    Raises
    ------
    Exception
        When `import tarfile` raises `ImportError`
    """
    if not HAVE_TAR:  # pragma: no cover
        raise Exception("Tarfile support is not available on this platform.")


# ------------------------------------------------------------------------------------------------------------------------
def extract_archive(archive: str, folder: str) -> None:
    """
    Extract an archive file to the specified folder.

    Parameters
    ----------
    archive : str
        Path to the archive file to extract.
    folder : str
        Path to the folder in which to extract the archive's contents.

    Raises
    ------
    NotImplementedError
        When the archive pointed to by `archive` is of an unsupported filetype.
    Exception
        when tarfile support is unavailable on this platform.
    Exception
        As per `tarfile.open` or `tarfile.TarFile.extractall`
    """
    filetype = get_filetype(archive)
    if filetype in ['archive-tar', 'archive-gzip', 'archive-bzip2']:
        require_tar()
        modes = {
            'archive-tar':   "r",
            'archive-gzip':  "r:gz",
            'archive-bzip2': "r:bz2"
        }
        tar = tarfile.open(archive, mode=modes[filetype])
        tar.extractall(folder)
        tar.close()
    else:
        raise NotImplementedError(f"No extraction support for files of type '{filetype}'.")


# ------------------------------------------------------------------------------------------------------------------------
def compress_archive(archive: str, folder: str):
    """
    Compress the specified folder into an archive file.

    Parameters
    ----------
    archive : str
        Path to the archive file to create.
    folder : str
        Path to the folder from which to populate the archive's contents.

    Raises
    ------
    NotImplementedError
        When the archive pointed to by `archive` is of an unsupported filetype.
    Exception
        when tarfile support is unavailable on this platform.
    Exception
        As per `tarfile.open` or `tarfile.TarFile.extractall`
    """
    filetype = get_filetype(archive)
    if filetype in ['archive-tar', 'archive-gzip', 'archive-bzip2']:
        modes = {
            'archive-tar':   "w",
            'archive-gzip':  "w:gz",
            'archive-bzip2': "w:bz2"
        }
        require_tar()
        with tarfile.open(archive, mode = modes[filetype]) as tar:
            tar.add(folder, arcname = os.path.sep)
            tar.close()
    else:
        raise NotImplementedError(f"No compression support for files of type '{filetype}'.")


# ------------------------------------------------------------------------------------------------------------------------
def load_txt(filename: str) -> str:
    """
    Read the entire content of a text file.

    Parameters
    ----------
    filename : str
        The name of the file.

    Returns
    -------
    str
        The content of the file as a string.

    Raises
    ------
    Exception
        As per `open` or `io.TextIOBase.read`.

    Notes
    -----
    This is an alias of `read_all`.

    """
    return read_all(filename)


# ------------------------------------------------------------------------------------------------------------------------
def save_txt(filename: str, obj: Any) -> None:
    """
    Write the content of a string to a text file.

    Parameters
    ----------
    filename : str
        The name of the file.
    obj: Any
        A string or object to write to the file. If not a string, `obj` will be converted
        to string by `str`.

    Raises
    ------
    Exception
        As per `open` or `io.TextIOBase.write`.
    """
    write_all(filename, str(obj))


# ------------------------------------------------------------------------------------------------------------------------
def load_json(filename: str) -> Any:
    """
    Load and deserialize a JSON-formatted text file.

    Parameters
    ----------
    filename : str
        The path to the file.

    Returns
    -------
    Any
        The python-native object represented by the content of the JSON file. See `decode_json`
        for more information on how `obj` is decoded.
    """
    return decode_json(read_all(filename))


# ------------------------------------------------------------------------------------------------------------------------
def save_json(filename: str, obj: Any) -> None:
    """
    Serialize and save a python object to a JSON-formatted text file.

    Parameters
    ----------
    filename : str
        The path to the file.
    obj : Any
        The object to serialize. Must consist of JSON serializable types. See `encode_json` for more
        information on how `obj` is encoded.
    """
    write_all(filename, encode_json(obj))


# ------------------------------------------------------------------------------------------------------------------------
def load_yaml(filename: str) -> Any:
    """
    Load and deserialize a YAML-formatted textfile.

    Parameters
    ----------
    filename : str
        The path to the file.

    Returns
    -------
    Any
        The python-native object represented by the content of the YAML file. See `decode_yaml`
        for more information on how `obj` is decoded.
    """
    with open(filename, 'r') as filp:
        return decode_yaml(filp)


# ------------------------------------------------------------------------------------------------------------------------
def save_yaml(filename: str, obj: Any) -> None:
    """
    Serialize and save a python object to a YAML-formatted text file.

    Parameters
    ----------
    filename : str
        The path to the file.
    obj : Any
        The object to serialize. Must consist of JSON serializable types. See `encode_yaml` for more
        information on how `obj` is encoded.
    """
    with open(filename, 'w') as filp:
        encode_yaml(obj, filp)


# ------------------------------------------------------------------------------------------------------------------------
def get_encoder(filename: str) -> Callable[[Any], str]:
    """
    Get the most appropriate encoder for serializing data to a format consistent with
    the file's extension.

    Parameters
    ----------
    filename : str
        The filename to examine.

    Returns
    -------
    Callable[[Any],str]
        A function which encodes an object to the text format most appropriate to the file's extension.

    Raises
    ------
    Exception
        When the filename's extension is not recognized. (see `__FILETYPES__` for more information.)
    """

    filetype = get_filetype(filename)
    if filetype == 'yaml':
        return encode_yaml

    elif filetype == 'json':
        return encode_json

    else:
        raise Exception(f'No known encoder for files with extension: "{filetype}"')


# ------------------------------------------------------------------------------------------------------------------------
def get_decoder(filename: str) -> Callable[ [str], Any ]:
    """
    Get the most appropriate decoder for serializing data to a format consistent with
    the file's extension.

    Parameters
    ----------
    filename : str
        The filename to examine.

    Returns
    -------
    Callable[ [str], Any ]
        A function which decodes an object from the text format most appropriate to the file's extension.

    Raises
    ------
    Exception
        When the filename's extension is not recognized. (see `__FILETYPES__` for more information.)
    """
    filetype = get_filetype(filename)
    if filetype == 'yaml':
        return decode_yaml

    elif filetype == 'json':
        return decode_json

    else:
        raise Exception(f'No known decoder for files with extension: "{filetype}"')


# ------------------------------------------------------------------------------------------------------------------------
def get_loader(
    filename: str,
    default:  Union[Undefined, Callable[[str], Any]] = UNDEFINED
) -> Callable[[str], Any]:
    """
    Get the most appropriate file loader for reading and deserializing data from a format consistent with
    the file's extension.

    Parameters
    ----------
    filename : str
        The filename to examine.
    default : Union[Undefined, Callable[[str], Any]], optional
        A loader function to return if no other loader could be found, by default UNDEFINED

    Returns
    -------
    Callable[[str],Any]
        A function which takes a filename and returns the deserialized content of that file.

    Raises
    ------
    Exception
        When no known loader could be found and `default` is `UNDEFINED`.
    """
    filetype = get_filetype(filename)
    if filetype == 'yaml':
        return load_yaml

    elif filetype == 'json':
        return load_json

    else:
        if is_undefined(default):
            raise Exception(f'No known load function for files with extension: "{filetype}"')
        else:
            return default


# ------------------------------------------------------------------------------------------------------------------------
def get_saver(
    filename: str,
    default: Union[Undefined, Callable[[str, Any], None]] = UNDEFINED
) -> Callable[[str, Any], None]:
    """
    Get the most appropriate file saver for serializing and writing data in a format consistent with
    the file's extension.

    Parameters
    ----------
    filename : str
        The filename to examine.
    default : Union[Undefined, Callable[[str, Any],None]], optional
        A saver function to return if no other saver could be found, by default UNDEFINED

    Returns
    -------
    Callable[[str, Any],None]
        A function which takes a filename and an object and writes the serialized object to that file.

    Raises
    ------
    Exception
        When no known saver could be found and `default` is `UNDEFINED`.
    """
    filetype = get_filetype(filename)
    if filetype == 'yaml':
        return save_yaml

    elif filetype == 'json':
        return save_json

    else:
        if is_undefined(default):
            raise Exception(f'No known save function for files with extension: "{filetype}"')
        else:
            return default


# ------------------------------------------------------------------------------------------------------------------------
def load(filename: str) -> Any:
    """
    Load the data in a file using an appropriate loader function based on the file's filename.

    Parameters
    ----------
    filename : str
        The filename to read and deserialize.

    Returns
    -------
    Any
        The deserialized object. Deserialization of this object must be supported by the
        relevant loader function. (See `get_loader` for more information).
    """
    return get_loader(filename)(filename)


# ------------------------------------------------------------------------------------------------------------------------
def save(filename: str, obj: Any) -> None:
    """
    Save a python object to a data file in a format determined by the file's filename.

    Parameters
    ----------
    filename : str
        The filename into which serialized version of `obj` will be written.
    obj : [type]
        The object to serialize. Serialization of this object must be supported by the
        relevant saver function. (See `get_saver` for more information).
    """
    get_saver(filename)(filename, obj)
