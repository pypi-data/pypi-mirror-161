#!/bin/false
# -*- coding: utf-8 -*-

""" Object-oriented filesystem helper classes. """


# ------------------------------------------------------------------------------------------------------------------------
# Import and pathing setup
# ------------------------------------------------------------------------------------------------------------------------
import errno
import os
import sys
import pathlib
from typing import Any, Callable, Dict, Generator, Iterable, Optional, Pattern, Tuple, Union

from ptutils.io import get_loader, get_saver, load_txt, save_txt
from ptutils.encoding import HAVE_YAML, register_yaml_type
from ptutils.globbing import get_subdirs, get_subfiles
from ptutils.text import strip_line_ending
from ptutils.undefined import UNDEFINED, is_defined
from ptutils.typing import MutableMapping

# ------------------------------------------------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------------------------------------------------
FOLDER_STORE_DEFAULT_SUFFIX = "yml" if HAVE_YAML else "json"

# ------------------------------------------------------------------------------------------------------------------------
# Typehint helpers
# ------------------------------------------------------------------------------------------------------------------------
""" Typehint for things which are like a filesystem path. """
PathLike = Union[str, pathlib.Path, 'Path', 'File', 'Folder']

""" Typehint for things which are like a list of filesystem paths. """
PathList = Iterable[PathLike]


# ------------------------------------------------------------------------------------------------------------------------
# Class: Path
# ------------------------------------------------------------------------------------------------------------------------
class Path():
    """ A filesystem path. this is a wrapper class for `pathlib.Path`. """
    def _native_of(path: PathLike):
        if isinstance(path, Path):
            return path._instance
        elif isinstance(path, pathlib.Path):
            return path
        else:
            return str(path)

    def __init__(self, path: PathLike):
        self._instance = pathlib.Path(Path._native_of(path))

    def __enter__(self):
        return self._instance.__enter__()

    def __exit__(self, t, v, tb):
        self._instance.__exit__(t, v, tb)

    @classmethod
    def cwd(cls):
        return cls(os.getcwd())

    @classmethod
    def home(cls):
        return cls(cls('.')._instance.home())

    def samefile(self, other_path):
        return self._instance.samefile(Path._native_of(other_path))

    def iterdir(self):
        for path in self._instance.iterdir():
            yield Path(path)

    def glob(self, pattern):
        for path in self._instance.glob(pattern):
            yield Path(path)

    def rglob(self, pattern):
        for path in self._instance.rglob(pattern):
            yield Path(path)

    def absolute(self):
        return Path(self._instance.absolute())

    def resolve(self, strict=False):
        return Path(self._instance.resolve(strict=strict))

    def stat(self):
        return self._instance.stat()

    def owner(self):
        return self._instance.owner()

    def group(self):
        return self._instance.group()

    def open(self, *args, **kwargs):
        return self._instance.open(*args, **kwargs)

    def read_bytes(self):
        return self._instance.read_bytes()

    def read_text(self, *args, **kwargs):
        return self._instance.read_text(*args, **kwargs)

    def write_bytes(self, data):
        return self._instance.write_bytes(data)

    def write_text(self, *args, **kwargs):
        return self._instance.write_text(*args, **kwargs)

    def touch(self, *args, **kwargs):
        self._instance.touch(*args, **kwargs)

    def mkdir(self, *args, **kwargs):
        self._instance.mkdir(*args, **kwargs)

    def chmod(self, *args, **kwargs):
        self._instance.chmod(*args, **kwargs)

    def lchmod(self, *args, **kwargs):
        self._instance.lchmod(*args, **kwargs)

    def unlink(self):
        self._instance.unlink()

    def rmdir(self):
        self._instance.rmdir()

    def lstat(self):
        return self._instance.lstat()

    def rename(self, target):
        self._instance.rename(Path._native_of(target))

    def replace(self, target):
        if sys.version_info >= (3, 8):  # pragma: no cover
            return Path(self._instance.replace(Path._native_of(target)))
        else:
            self._instance.replace(Path._native_of(target))

    def symlink_to(self, target, target_is_directory=False):
        self._instance.symlink_to(
            target              = Path._native_of(target),
            target_is_directory = target_is_directory
        )

    # Convenience functions for querying the stat results
    def exists(self):
        return self._instance.exists()

    def is_dir(self):
        return self._instance.is_dir()

    def is_file(self):
        return self._instance.is_file()

    def is_symlink(self):
        return self._instance.is_symlink()

    def is_block_device(self):
        return self._instance.is_block_device()

    def is_char_device(self):
        return self._instance.is_char_device()

    def is_fifo(self):
        return self._instance.is_fifo()

    def is_socket(self):
        return self._instance.is_socket()

    def expanduser(self):
        return Path(self._instance.expanduser())

    def __str__(self):
        return str(self._instance)

    def __fspath__(self):
        return str(self)

    def as_posix(self):
        return self._instance.as_posix()

    def __bytes__(self):
        return self._instance.__bytes__()

    def __repr__(self):
        return f"{type(self).__name__}('{str(self)}')"

    def as_uri(self):
        return self._instance.as_uri()

    def __eq__(self, other):
        return self._instance == pathlib.Path(Path._native_of(other))

    def __ne__(self, other):
        return self._instance != pathlib.Path(Path._native_of(other))

    def __hash__(self):
        return self._instance.__hash__()

    def __lt__(self, other):
        return self._instance < pathlib.Path(Path._native_of(other))

    def __le__(self, other):
        return self._instance <= pathlib.Path(Path._native_of(other))

    def __gt__(self, other):
        return self._instance > pathlib.Path(Path._native_of(other))

    def __ge__(self, other):
        return self._instance >= pathlib.Path(Path._native_of(other))

    @property
    def drive(self):
        return self._instance.drive

    @property
    def root(self):
        return self._instance.root

    @property
    def anchor(self):
        return self._instance.anchor

    @property
    def name(self):
        return self._instance.name

    @property
    def suffix(self):
        return self._instance.suffix

    @property
    def suffixes(self):
        return self._instance.suffixes

    @property
    def stem(self):
        return self._instance.stem

    def with_name(self, name):
        return Path(self._instance.with_name(name=name))

    def with_suffix(self, suffix):
        return Path(self._instance.with_suffix(suffix=suffix))

    def relative_to(self, *other):
        return Path(
            self._instance.relative_to(
                *(
                    Path._native_of(x) for x in other
                )
            )
        )

    @property
    def parts(self):
        return self._instance.parts

    def joinpath(self, *args):
        return Path(self._instance.joinpath(*args))

    def __truediv__(self, key):
        return Path(self._instance / key)

    def __rtruediv__(self, key):
        return Path(key / self._instance)

    @property
    def parent(self):
        return Path(self._instance.parent)

    @property
    def parents(self):
        return [Path(x) for x in self._instance.parents]

    def is_absolute(self):
        return self._instance.is_absolute()

    def is_reserved(self):
        return self._instance.is_reserved()

    def match(self, path_pattern):
        return self._instance.match(path_pattern)

    # --------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def path_of(path: PathLike) -> 'Path':
        """
        Given a `PathLike` object, coerce it into being a `Path`.

        Returns
        -------
        Path
            A path object referencing the same path as `path`
        """
        return Path(path)

    # --------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def names_of(paths: PathList) -> Generator[str, None, None]:
        """
        Given a list of path objects, return a list of the filename portion of each path.

        Parameters
        ----------
        paths : PathList
            An iterable of `PathLike` objects. To determine filename, these will be coerced
            into `Path` objects before retrieving the filename portion of the path.

        Yields
        ------
        str
            The filename portion of each path provided in `paths`
        """
        for path in paths:
            yield Path.path_of(path).name

    # --------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def relative_paths_to(paths: PathList, reference: PathLike) -> Generator[str, None, None]:
        """
        Given a list of paths and a reference path, compute and return a list of the relative paths.

        Parameters
        ----------
        paths : PathList
            An iterable of `PathLike` objects. To relative path filename, these will be coerced
            into `Path` objects before retrieving the relative path with respect to `reference`.
        reference: PathLike
            A path from which to compute the relative paths of each path in `paths`. this will be
            coerced to a `Path` object before use.

        Yields
        ------
        str
            The filename portion of each path provided in `paths`
        """
        reference = Path.path_of(reference)
        for path in paths:
            yield Path(path).relative_to(reference)


# =======================================================================================================================
# Class: File
# =======================================================================================================================
class File(Path):
    """ Class to simplify common file operations. """
    # def __new__(cls, *args, **kwargs):
    #     klass = ShimWindowsFile if os.name == 'nt' else ShimPosixFile
    #     return super().__new__(klass, *args, **kwargs)

    # --------------------------------------------------------------------------------------------------------------------
    def __init__(self, path: PathLike):
        """
        Create a new File path object.

        Parameters
        ----------
        path : PathLike
            The filesystem path of a file. This file may or may not exist.
        """
        super().__init__(path)
        self._loader = None
        self._saver = None

    # --------------------------------------------------------------------------------------------------------------------
    def exists(self) -> bool:
        """
        Test whether this path exists and refers to a file.

        Returns
        -------
        bool
            True if the path refers to an existing file.
        """
        return super().exists() and self.is_file()

    # --------------------------------------------------------------------------------------------------------------------
    def initialize_content(self, content: Any = UNDEFINED) -> None:
        """
        Initialize a file's contents by setting the content property if the file doesn't already exist.

        Parameters
        ----------
        content : Any, optional
            [description], by default UNDEFINED
        """
        if is_defined(content):
            if not self.exists():
                self.content = content

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def loader(self) -> Callable[[PathLike], Any]:
        """
        Get the most appropriate loader for this path based on the filename's extension.

        Returns
        -------
        Callable[[PathLike], Any]
            A function which loads the content of the file.

        """
        if self._loader is None:
            self._loader = get_loader(
                filename = str(self),
                default  = load_txt
            )
        return self._loader

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def saver(self) -> Callable[[PathLike, Any], None]:
        """
        Get the most appropriate saver for this path based on the filename's extension.

        Returns
        -------
        Callable[[PathLike, Any], None]
            A function which saves an object to the file in whatever format is most appropriate.

        """
        if self._saver is None:
            self._saver = get_saver(
                filename = str(self),
                default  = save_txt
            )
        return self._saver

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def content(self) -> Any:
        """
        Load the file's contents using the loader determined when the `File` object was created.

        Returns
        -------
        Any
            The loaded/decoded file content. The structure and format is determined by the
        """
        return self.loader(self)

    # --------------------------------------------------------------------------------------------------------------------
    @content.setter
    def content(self, value: Any) -> None:
        """
        Set the file's content by invoking the appropriate saver.

        Parameters
        ----------
        value : Any
            The value to encode and save to the file.
        """
        self.saver(self, value)

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def lines(self) -> Generator[str, None, None]:
        """
        Iterator over the text lines in a file.

        Yields
        ------
        str
            A line of text from the file.

        Notes
        -----
            This property bypasses the determined loader and instead directly
            reads the file as text. If used with binary files, undefined behaviour may result.
        """
        with open(self, 'r') as filp:
            for line in filp.readlines():
                yield strip_line_ending( line )


# =======================================================================================================================
# Class: Folder
# =======================================================================================================================
class Folder(Path):
    """ Class to simplify common folder operations. """

    # --------------------------------------------------------------------------------------------------------------------
    def exists(self) -> bool:
        """
        Test whether this path exists and refers to a folder.

        Returns
        -------
        bool
            True if the path refers to an existing folder.
        """
        return super().exists() and self.is_dir()

    # --------------------------------------------------------------------------------------------------------------------
    def search_subdirectories(
        self,
        pattern:   Optional[Pattern] = None,
        recursive: bool    = False
    ) -> Generator['Folder', None, None]:
        """
        Search for subdirectories of this folder, optionally recursive, optionally
        matching a regular expression.

        Parameters
        ----------
        pattern : Pattern, optional
            A regular expression to match against folder basenames, by default
            None. When omitted, every folder in the search folder will be returned.
        recursive : bool, optional
            When True, search recursively into all subfolders of the search
            folder, by default False.

        Yields
        -------
        Folder
            Any folders matching the constraints specified.
        """
        for fullpath in get_subdirs(self, pattern=pattern, recursive=recursive):
            yield Folder(fullpath)

    # --------------------------------------------------------------------------------------------------------------------
    def search_files(
        self,
        pattern:   Pattern = None,
        recursive: bool    = False
    ) -> Generator['File', None, None]:
        """
        Search for files within this folder, optionally recursive, optionally
        matching a regular expression.

        Parameters
        ----------
        pattern : Pattern, optional
            A regular expression to match against file basenames, by default
            None. When omitted, every files in the search folder will be returned.
        recursive : bool, optional
            When True, search recursively into all subfolders of the search
            folder, by default False.

        Yields
        -------
        Folder
            Any files matching the constraints specified.
        """
        for fullpath in get_subfiles(self, pattern=pattern, recursive=recursive):
            yield File(fullpath)

    # --------------------------------------------------------------------------------------------------------------------
    def child(self, name: PathLike) -> Path:
        """
        Return a a child path of this folder created by concatenating the provided
        `name` with this folder's path.

        Parameters
        ----------
        name : PathLike
            A name or relative path of the child.

        Returns
        -------
        Path
            A new `Path` object referring to the child path.
        """
        return Path(self / Path.path_of(name))

    # --------------------------------------------------------------------------------------------------------------------
    def child_file(self, name: PathLike) -> 'File':
        """
        Return a a child file of this folder created by concatenating the provided
        `name` with this folder's path.

        Parameters
        ----------
        name : PathLike
            A name or relative path of the child.

        Returns
        -------
        File
            A new `File` object referring to the child path.
        """
        return File(self / Path.path_of(name))

    # --------------------------------------------------------------------------------------------------------------------
    def child_folder(self, name: PathLike) -> 'Folder':
        """
        Return a a child folder of this folder created by concatenating the provided
        `name` with this folder's path.

        Parameters
        ----------
        name : PathLike
            A name or relative path of the child.

        Returns
        -------
        Folder
            A new `Folder` object referring to the child path.
        """
        return Folder(self / Path.path_of(name))

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def subdirectories(self) -> Generator['Folder', None, None]:
        """
        An iterator over this folder's subdirectories.

        Returns
        -------
        Folder
            Any child folder.
        """
        return self.search_subdirectories()

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def files(self) -> PathList:
        """
        An iterator over this folder's files.

        Returns
        -------
        Folder
            Any child file.
        """
        return self.search_files()


# =======================================================================================================================
# Class: FolderSet
# =======================================================================================================================
class FolderSet:
    """
    A convenience class to allow attribute/index-style traversal of folder structures.
    """

    def __init__(self, root: PathLike, structure: Optional[Dict[str, Any]] = None):
        """
        Create a new folder set.

        Parameters
        ----------
        root: PathLike
            The path to the folder.
        structure: Optional[Dict[str, Any]], optional
            A hierarchical structure used to limit traversal, by default None
        """
        self._root      = Folder(root)
        self._structure = structure
        self._cache     = dict()

    # --------------------------------------------------------------------------------------------------------------------
    def __truediv__(self, name: PathLike) -> Union['FolderSet', 'File']:
        """
        Convenience method to allow using division operator to access child objects.

        Parameters
        ----------
        name: PathLike
            The relative path to the child.

        Returns
        -------
        Union['FolderSet', 'File']
            Either a file or folder set object depending on what the child path refers to.
        """
        return self[name]

    # --------------------------------------------------------------------------------------------------------------------
    @property
    def folder(self) -> Folder:
        """
        The root folder object of this folder set.

        Returns
        -------
        Folder
            The `Folder` referring to our root path.
        """
        return self._root

    # --------------------------------------------------------------------------------------------------------------------
    def __getattr__(self, name: str) -> Union['FolderSet', 'File']:
        """
        Access a child file or folder with attribute-style access of this folder object.

        Returns
        -------
        Union['FolderSet', 'File']
            Either a file or folder set object depending on what the child path refers to.

        Raises
        ------
        AttributeError
            When no such child file or folder exists.
        """
        try:
            return self[name]
        except Exception as e:
            raise AttributeError(f"Object of type {type(self)} has no '{name}' attribute.") from e

    # --------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, name: str) -> Union['FolderSet', 'File']:
        """
        Access a child file or folder with index-style access of this folder object.

        Returns
        -------
        Union['FolderSet', 'File']
            Either a file or folder set object depending on what the child path refers to.

        Raises
        ------
        KeyError
            When no such child file or folder exists.
        """
        if name.startswith('$$'):
            name = name[2:]

        child = self._root.child(name)
        if not child.exists():
            raise KeyError(f"Object '{name}' is not found in directory '{self._root}'.")

        if child.is_dir():
            if self._structure is not None:
                if name not in self._structure:
                    if (
                        ('$$folders' not in self._structure) or
                        (name not in self._structure['$$folders'])
                    ):
                        raise KeyError(
                            f"Object '{name}' is not defined in the "
                            f"FolderSet structure for '{self._root}', and "
                            "so may not be accessed."
                        )
                    return FolderSet(root=child, structure=None)
                return FolderSet(root=child, structure=self._structure[name])
            return FolderSet(root=child, structure=None)

        elif child.is_file():
            if (self._structure is not None) and ('$$files' in self._structure):
                if name not in self._structure['$$files']:
                    raise KeyError(
                        f"Object '{name}' is not defined in the "
                        f"FolderSet structure for '{self._root}', and "
                        "so may not be accessed."
                    )
            return File(path=child)

        raise KeyError(  # pragma: no cover
            f"Object '{name}' found in directory '{self._root}' "
            "is neither a file nor a directory."
        )


# -----------------------------------------------------------------------------------------------------------------------
# class: FolderStore
# -----------------------------------------------------------------------------------------------------------------------
class FolderStore(MutableMapping):
    """
    An adapter class to use mapping-style access to a folder of datafiles. Mapping indices
    are the stem of the filenames, with suffix being either 'yml', 'json', or other formats
    for which encoding are supported.

    """
    def __init__(self, folder: Folder, suffix=FOLDER_STORE_DEFAULT_SUFFIX):
        """
        Create a folder store.

        Parameters
        ----------
        folder : Folder
            The path to the filesystem location where data files will be kept.
        suffix : str, optional
            The filename extension to use, by default "yml" if YAML support is available, else "json". Supported formats
            are the same as for `File.content`.

        Raises
        ------
        ValueError
            If the path is a protected path path (e.g. '/').
        """
        if suffix not in ["yaml", "yml", "json"]:
            raise ValueError(f"Suffix is not a supported format ('yml', 'yaml', or 'json'): '{suffix}'")
        self.folder  = Folder(Folder(folder).absolute())
        self.suffix  = suffix
        self.pattern = r"^.*\." + suffix + r"$"
        self.template = "{name}." + suffix
        if str(self.folder) == "/":
            raise ValueError("Can't create a cache at the root path '/'.")
        self._create_folder()

    def _create_folder(self) -> None:
        """
        Create the backing folder.

        Raises
        ------
        Exception
            When the backing folder does not already exist and can not be created.
        """
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create cache directory: {e}") from e

    def _destroy_folder(self) -> None:
        """
        Destroy the backing folder and delete all contents.

        Raises
        ------
        Exception
            When removal of the directory fails.
        """
        try:
            from shutil import rmtree
            rmtree(str(self.folder))
        except Exception as e:
            raise Exception(f"Failed to destroy cache directory: {e}") from e

    def clear(self) -> None:
        """
        Clear all folder contents.
        """
        self._destroy_folder()
        self._create_folder()

    def get_datafile(self, name: str, ensure_exists: bool = False) -> File:
        """
        get the backing `File` object corresponding to the supplied `name`.

        Parameters
        ----------
        name : str
            The name of the file. Must be a valid filename component.
        ensure_exists : bool, optional
            When true check if the file exists already and raise FileNotFoundError
            if missing, by default False

        Returns
        -------
        File
            A file object corresponding to the given `name`.

        Raises
        ------
        FileNotFoundError
            When `ensure_exists` is true but the file does not exist.
        """
        rv = self.folder.child_file( self.template.format(name = name) )
        if ensure_exists and not rv.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(rv))
        return rv

    @property
    def files(self) -> Generator[File, None, None]:
        """
        An iterable over all files in the backing folder matching the store's filename pattern.

        Returns
        -------
        Iterable[File]
            The matching files.
        """
        return self.folder.search_files(pattern=self.pattern, recursive=False)

    def __getitem__(self, name: str) -> Any:
        """
        Get a file-backed item value corresponding to the supplied `name`.

        Parameters
        ----------
        name : str
            The name of the value.

        Returns
        -------
        Any
            The value.

        Raises
        ------
        KeyError
            When the backing file does not exist.
        """
        try:
            return self.get_datafile(name, ensure_exists=True).content
        except Exception as e:
            raise KeyError(name) from e

    def __setitem__(self, name: str, value: Any) -> None:
        """
        Set the file-backed item value corresponding to the supplied `name`.

        Parameters
        ----------
        name : str
            The name.
        value : Any
            The new value.
        """
        self.get_datafile(name, ensure_exists=False).content = value

    def __delitem__(self, name: str) -> None:
        """
        Remove the file-backed item value corresponding to the supplied `name`.

        Parameters
        ----------
        name : str
            The name.

        Raises
        ------
        KeyError
            When the backing file does not exist.
        """
        try:
            file = self.get_datafile(name, ensure_exists=True)
        except FileNotFoundError as e:
            raise KeyError(name) from e
        file.unlink()

    def __iter__(self) -> Generator[str, None, None]:
        """
        Iterate over names of the file-backed store.

        Yields
        ------
        str
            The names of the values.
        """
        for file in self.files:
            yield str(file.stem)

    def __len__(self) -> int:
        """
        Return the count of items in the store.

        Returns
        -------
        int
            The count of files in the backing directory which match the naming pattern.
        """
        return sum( 1 for _ in iter( self ) )

    def items(self) -> Generator[ Tuple[str, Any], None, None ]:
        """
        Iterator over key-value pairs.

        Yields
        ------
        Tuple[str, Any]
            key-value pairs.
        """
        for file in self.files:
            yield str(file.stem), file.content


# =======================================================================================================================
# Helpers: yaml encoding/decoding of file/folder/path classes
# =======================================================================================================================
if HAVE_YAML:
    register_yaml_type(Folder, lambda folder: str(folder), lambda text: Folder(text))
    register_yaml_type(File,   lambda file:   str(file),   lambda text: File(text))  # noqa: E272
    register_yaml_type(Path,   lambda path:   str(path),   lambda text: Path(text))  # noqa: E272
