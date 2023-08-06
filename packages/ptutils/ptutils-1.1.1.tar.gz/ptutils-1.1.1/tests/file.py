#!/bin/false
# -*- coding: utf-8 -*-

"""This module provides unit tests for `ptutils.file`."""

import datetime
import os
import shutil
import sys
import tempfile
import pytest
import pathlib
from ptutils.file import ( FolderStore, Path, File, Folder, FolderSet )
from ptutils.undefined import UNDEFINED, is_defined
from ptutils.encoding import HAVE_YAML, decode_json, decode_yaml, encode_json
from ptutils.io import load, load_txt, load_json, load_yaml, save, save_txt, save_json, save_yaml
from ._fs_fixture import sample_file_structure  # noqa: F401
from ._fs_fixture import FILE_STRUCTURE
from ._fs_fixture import localize_path

PATH_EXPECTATIONS_POSIX = {
    "/a/path/to/a/file.ext": {
        "parent":       Path("/a/path/to/a"),
        "parts":        tuple(["/", "a", "path", "to", "a", "file.ext"]),
        "drive":        "",
        "root":         "/",
        "anchor":       "/",
        "name":         "file.ext",
        "suffix":       ".ext",
        "suffixes":     [".ext"],
        "stem":         "file",
        "exists":       False,
        "as_posix":     "/a/path/to/a/file.ext",
        "as_uri":       "file:///a/path/to/a/file.ext",
        "is_absolute":  True,
        "is_reserved":  False,
        "expanduser":   "/a/path/to/a/file.ext"
    },
    "a/path/to/a/file.ext1.ext2": {
        "parent":       Path("a/path/to/a"),
        "parts":        tuple("a/path/to/a/file.ext1.ext2".split("/")),
        "drive":        "",
        "root":         "",
        "anchor":       "",
        "name":         "file.ext1.ext2",
        "suffix":       ".ext2",
        "suffixes":     [".ext1", ".ext2"],
        "stem":         "file.ext1",
        "exists":       False,
        "as_posix":     "a/path/to/a/file.ext1.ext2",
        "as_uri":       ValueError,
        "is_absolute":  False,
        "is_reserved":  False,
        "expanduser":   "a/path/to/a/file.ext1.ext2"
    }
}
PATH_EXPECTATION_KEYS_POSIX = [
    "parent",
    "parts",
    "drive",
    "root",
    "anchor",
    "name",
    "suffix",
    "suffixes",
    "stem",
    "exists",
    "as_posix",
    "as_uri",
    "is_absolute",
    "is_reserved",
    "expanduser"
]


@pytest.mark.parametrize(
    argnames  = "key",
    argvalues = PATH_EXPECTATION_KEYS_POSIX,
    ids       = PATH_EXPECTATION_KEYS_POSIX
)
@pytest.mark.parametrize(
    argnames  = ["path", "expectations"],
    argvalues = PATH_EXPECTATIONS_POSIX.items(),
    ids       = [ x[0] for x in PATH_EXPECTATIONS_POSIX.items() ]
)
def test_path(path, expectations, key):
    p = Path(path)
    e = expectations[key]
    if (isinstance(e, type)) and (issubclass(e, Exception)):
        # expecting an exception to be raised
        with pytest.raises(e):
            a = getattr(p, key, UNDEFINED)
            if callable(a):
                a()
    else:
        # not expecting an exception to be raised
        a = getattr(p, key, UNDEFINED)
        assert is_defined(a)
        if callable(a):
            a = a()
        assert a == expectations[key]


def test_path_wrapper_methods(sample_file_structure):  # noqa: F811
    folder = Path(sample_file_structure)
    folder2 = Path(sample_file_structure)

    # test context entry/exit
    with folder as _:

        # test is_xxx
        assert folder.is_absolute() is True
        assert folder.is_dir() is True
        assert folder.is_file() is False
        assert folder.is_symlink() is False
        assert folder.is_block_device() is False
        assert folder.is_char_device() is False
        assert folder.is_fifo() is False
        assert folder.is_socket() is False

        # test same file
        assert folder.samefile(folder2)

        # test iterdir
        count = sum(1 for _ in folder.iterdir())
        assert count > 0

        # test glob
        count = sum(1 for _ in folder.glob('*'))
        assert count > 0

        # test rglob
        count = sum(1 for _ in folder.rglob('*.json'))
        assert count > 0

        # test absolute
        assert isinstance(folder.absolute(), Path)

        # test resolve
        assert isinstance(folder.resolve(), Path)
        assert isinstance(folder.resolve(strict=True), Path)

        # test stat
        assert folder.stat() is not None

        # test owner/group
        if os.name != 'nt':
            assert folder.owner() is not None
            assert folder.group() is not None

        # test bytes
        assert bytes(folder) == str(folder).encode('utf-8')

        # test comparisons
        for part in ['abc', 'abc/def', 'abc/def/', '/abc', '/abd/def', '/abd/def/']:
            for case in [part, Path(part), pathlib.Path(part)]:
                assert isinstance(folder > case, bool)
                assert isinstance(folder < case, bool)
                assert isinstance(folder >= case, bool)
                assert isinstance(folder <= case, bool)

    # file write_text/read_text/unlink text
    content = encode_json(SAMPLE_DATAFILE_DATA)
    tmpfile = folder / "temp.file.json"
    with tmpfile.open("w") as _:
        tmpfile.write_text(content)
    assert tmpfile.exists()
    assert tmpfile.is_file()
    with tmpfile.open("r") as _:
        assert tmpfile.read_text() == content
    tmpfile.unlink()
    assert not tmpfile.exists()

    # file write_bytes/read_bytes/unlink binary
    content = encode_json(SAMPLE_DATAFILE_DATA).encode('utf-8')
    with tmpfile.open("wb") as _:
        tmpfile.write_bytes(content)
    assert tmpfile.exists()
    assert tmpfile.is_file()
    with tmpfile.open("rb") as _:
        assert tmpfile.read_bytes() == content
    tmpfile.unlink()
    assert not tmpfile.exists()

    # file touch/is_file/unlink
    tmpfile.touch()
    assert tmpfile.exists()
    tmpfile.unlink()
    assert not tmpfile.exists()

    # folder mkdir/rmdir
    folder3 = folder / "new-folder"
    assert not folder3.exists()
    folder3.mkdir()
    assert folder3.exists()
    assert folder3.is_dir()
    folder3.rmdir()
    assert not folder3.exists()

    # folder mkdir/rename/rmdir
    folder4 = folder / "new-folder.bak"
    assert not folder4.exists()
    folder3.mkdir()
    folder3.rename(folder4)
    assert folder4.exists()
    assert folder4.is_dir()
    folder4.rmdir()
    assert not folder4.exists()

    # file stat/lstat
    assert not tmpfile.exists()
    tmpfile.touch()
    assert tmpfile.exists()
    assert tmpfile.lstat() is not None
    assert tmpfile.stat() is not None
    assert tmpfile.stat() == tmpfile.lstat()
    tmpfile.unlink()
    assert not tmpfile.exists()

    if os.name != 'nt':
        assert not tmpfile.exists()
        tmpfile.touch()
        assert tmpfile.exists()
        tmpfile.chmod(0o444)
        assert (tmpfile.stat().st_mode & 0o777) == 0o444
        tmpfile.chmod(0o456)
        assert (tmpfile.stat().st_mode & 0o777) == 0o456
        tmpfile.unlink()
        assert not tmpfile.exists()

    # home/cwd class methods
    assert Path.cwd() == Path(os.getcwd())
    assert isinstance(Path.home(), Path)

    # folder symlink symlink_to/lstat/lchmod
    folder_symlink = folder / "folder_symlink"
    assert not folder_symlink.exists()
    folder_symlink.symlink_to(folder / "folder_symlink_target_dne", target_is_directory=True)
    assert folder_symlink.is_symlink()
    assert not folder_symlink.exists()
    assert folder_symlink.lstat() is not None
    with pytest.raises(Exception) as _:
        folder_symlink.stat()
    if os.name != 'nt':
        try:
            folder_symlink.lchmod(0o444)
            assert (folder_symlink.lstat().st_mode & 0o777) == 0o444
            folder_symlink.lchmod(0o456)
            assert (folder_symlink.lstat().st_mode & 0o777) == 0o456
        except NotImplementedError:
            pass
    folder_symlink.unlink()
    assert not folder_symlink.exists()
    assert not folder_symlink.is_symlink()

    # link stat/lstat
    # file_symlink   = folder / "file_symlink"
    # assert not file_symlink.exists()
    file_symlink = folder / "file_symlink"
    assert not file_symlink.exists()
    file_symlink.symlink_to(folder / "file_symlink_target_dne", target_is_directory=False)
    assert file_symlink.is_symlink()
    assert not file_symlink.exists()
    assert file_symlink.lstat() is not None
    with pytest.raises(Exception) as _:
        file_symlink.stat()
    if os.name != 'nt':
        try:
            file_symlink.lchmod(0o444)
            assert (file_symlink.lstat().st_mode & 0o777) == 0o444
            file_symlink.lchmod(0o456)
            assert (file_symlink.lstat().st_mode & 0o777) == 0o456
        except NotImplementedError:
            pass
    file_symlink.unlink()
    assert not file_symlink.exists()
    assert not file_symlink.is_symlink()

    assert isinstance(hash(folder), int)
    assert isinstance((folder != ''), bool)
    assert repr(folder) == f"Path('{str(folder)}')"
    assert (folder / "abc").with_name("xyz").name == "xyz"
    assert (folder / "abc").with_suffix(".xyz").suffix == ".xyz"
    assert folder.joinpath("abc", "xyz") == folder / "abc" / "xyz"
    assert ("x" / folder) == Path(os.path.join("x", sample_file_structure))
    assert len(folder.parents) == 2
    assert isinstance(folder.match('abc'), bool)
    assert (folder / "abc" / "xyz").relative_to(folder) == Path('abc/xyz')

    tmpfile1 = folder.joinpath('boring_things', 'thing.json')
    tmpfile2 = folder.joinpath('boring_things', 'another-thing.json')
    assert tmpfile1.exists()
    assert not tmpfile2.exists()
    tmpfile3 = tmpfile1.replace(tmpfile2)
    if sys.version_info >= (3, 8):
        assert tmpfile3 == tmpfile2
    else:
        assert tmpfile3 is None
    assert not tmpfile1.exists()
    assert tmpfile2.exists()
    tmpfile4 = tmpfile2.replace(tmpfile1)
    if sys.version_info >= (3, 8):
        assert tmpfile4 == tmpfile1
    else:
        assert tmpfile4 is None
    assert tmpfile1.exists()
    assert not tmpfile2.exists()
    if sys.version_info >= (3, 8):
        assert not tmpfile3.exists()
        assert tmpfile4.exists()


def test_path_static_methods():
    assert Path.path_of('abc') == Path('abc')
    assert Path.path_of(Path('abc')) == Path('abc')
    assert Path.path_of(pathlib.Path('abc')) == Path('abc')

    paths = [
        Path.path_of('abc'),
        Path.path_of(Path('abc')),
        Path.path_of(pathlib.Path('abc'))
    ]
    for path in paths:
        assert path.name == 'abc'

    assert list(Path.names_of(paths)) == paths
    folder = Path(localize_path('a/b/c/d/e'))
    ref    = Path(localize_path('a/b'))
    paths = [ (folder / x) for x in "vwxyz" ]
    assert list(Path.relative_paths_to(paths, ref)) == [ (Path(localize_path("c/d/e")) / x) for x in "vwxyz" ]


FILE_TEST_CASES = [
    ('boring_things/thing.json', 'json', True),
    ('boring_things/thing.yaml', 'yaml', True),
    ('boring_things/text_thing', 'text', True),
    ('boring_things/tbd_things/thing.json', 'json', False),
    ('boring_things/tbd_things/thing.yaml', 'yaml', False),
    ('boring_things/tbd_things/text_thing', 'text', False)
]


SAMPLE_TEXTFILE_DATA = '\n'.join([
    "This is a text file",
    "It has a few lines.",
    "There's nothing special about it.",
    "It can be used for testing",
    "text file manipulation ",
    "functions and classes."
])


SAMPLE_DATAFILE_DATA = {
    "a": True,
    "b": 12345,
    "c": None,
    "d": 3.14,
    "e": [False, 678, None, 1.2, [], {}],
    "f": {
        "1": 1,
        "2": 2.0,
        "3": None,
        "4": [False, 678, None, 1.2, [], {}],
        "5": {}
    }
}


LOADERS = {
    "text": load_txt,
    "json": load_json,
    "yaml": load_yaml
}


SAVERS = {
    "text": save_txt,
    "json": save_json,
    "yaml": save_yaml
}


@pytest.mark.parametrize(
    argnames  = ["path", "format", "exists"],
    argvalues = FILE_TEST_CASES,
    ids       = [f"{x[0]}(format={x[1]},exists={x[2]})" for x in FILE_TEST_CASES]
)
def test_file(sample_file_structure, path, format, exists):  # noqa: F811
    path = os.path.join(sample_file_structure, localize_path(path))
    file = File(path)
    assert file.exists() == exists
    assert file.loader   is LOADERS[format]  # noqa: E272,E271
    assert file.saver    is SAVERS[format]   # noqa: E272,E271
    assert file.parent   == os.path.join(sample_file_structure, os.path.dirname(path))

    if exists:
        dir_data = FILE_STRUCTURE['boring_things']
        if format == "text":
            assert file.content == dir_data['text_thing']

        else:
            if format == "json":
                assert file.content == decode_json(dir_data['thing.json'])
                assert list(file.lines) == dir_data['thing.json'].split('\n')
            else:
                assert file.content == decode_yaml(dir_data['thing.yaml'])
                assert list(file.lines) == dir_data['thing.yaml'].split('\n')

    else:
        if format == "text":
            content = SAMPLE_TEXTFILE_DATA
        else:
            content = SAMPLE_DATAFILE_DATA

        assert not file.exists()
        file.initialize_content(content = content)
        assert file.exists()
        assert file.content == content
        file.initialize_content(content = content)
        assert file.exists()
        assert file.content == content
        file.initialize_content(content = UNDEFINED)
        assert file.exists()
        assert file.content == content


def test_folder(sample_file_structure):  # noqa: F811
    folder = Folder(sample_file_structure)
    subfiles = [ File(folder / x) for x in ["a_file", "another_file"] ]
    subdirs  = [ Folder(folder / x) for x in ["boring_things", "interesting_things", "apples"] ]
    assert folder.exists()
    assert set(list(folder.search_files())) == set(subfiles)
    assert set(list(folder.search_subdirectories())) == set(subdirs)
    assert set(folder.subdirectories) == set(subdirs)
    assert set(folder.files) == set(subfiles)
    assert folder.child("abc") == folder / "abc"
    assert isinstance(folder.child_file("abc"), File)
    assert folder.child_file("abc") == File(folder / "abc")
    assert isinstance(folder.child_folder("abc"), Folder)
    assert folder.child_folder("abc") == Folder(folder / "abc")


def test_folderset(sample_file_structure):  # noqa: F811
    folderset = FolderSet(sample_file_structure)
    assert folderset.folder == Folder(sample_file_structure)
    f1 = folderset.a_file
    assert isinstance(f1, File)
    assert f1.exists()
    with pytest.raises(AttributeError):
        folderset.a_file_that_doesnt_exist
    with pytest.raises(KeyError):
        folderset['a_file_that_doesnt_exist']
    with pytest.raises(KeyError):
        folderset / 'a_file_that_doesnt_exist'
    f3 = folderset.apples
    assert isinstance(f3, FolderSet)
    assert f3.folder.exists()
    assert f3.folder == folderset.folder / 'apples'
    assert (folderset / 'apples').folder == folderset.folder / 'apples'
    with pytest.raises(KeyError):
        folderset['a_file_that_doesnt_exist']
    assert folderset['$$a_file'] == folderset.a_file


def test_folderset_structured(sample_file_structure):  # noqa: F811
    folderset = FolderSet(
        sample_file_structure,
        structure={
            "$$files": [
                "a_file"
            ],
            "$$folders": [
                "apples"
            ],
            "boring_things": {}
        }
    )
    f1 = folderset.a_file
    assert isinstance(f1, File)
    assert f1.exists()

    with pytest.raises(AttributeError):
        folderset.a_file_that_doesnt_exist

    with pytest.raises(KeyError):
        folderset / 'a_file_that_doesnt_exist'

    with pytest.raises(KeyError):
        folderset['a_file_that_doesnt_exist']

    with pytest.raises(AttributeError):
        folderset.another_file

    with pytest.raises(KeyError):
        folderset["another_file"]

    with pytest.raises(KeyError):
        folderset / "another_file"

    f2 = folderset.apples
    assert isinstance(f2, FolderSet)
    assert f2.folder.exists()
    assert f2.folder == folderset.folder / 'apples'
    assert (folderset / 'apples').folder == folderset.folder / 'apples'

    f3 = folderset.boring_things
    assert isinstance(f3, FolderSet)
    assert f3.folder.exists()
    assert f3.folder == folderset.folder / 'boring_things'
    assert (folderset / 'boring_things').folder == folderset.folder / 'boring_things'

    with pytest.raises(AttributeError):
        folderset.interesting_things

    with pytest.raises(KeyError):
        folderset["interesting_things"]

    with pytest.raises(KeyError):
        folderset / "interesting_things"

    f4 = f3.text_thing
    assert isinstance(f4, File)
    assert f4.exists()

    f5 = f2 / "red-delicious"
    assert isinstance(f5, File)
    assert f5.exists()


STORE_INITIAL_CONTENT = {
    "banana":      123,
    "cherry":      None,
    "dragonfruit": True,
    "elderberry":  "hello",
    "fig":         [],
    "guava":       { "a": 123, "b": 456.789, "c": None, "d": { "x": [1, 2, 3], "y": { } } },
    "icaco":       789.0,
    "jackfruit":   False
}
STORE_YAML_ONLY_CONTENT = {
    "apple": {
        "when":    datetime.datetime.utcnow(),
        "file":    File('does-not-exist.yml')
    }
}
STORE_UPDATES = {
    "potato": "not a fruit",
    "tomato": "kinda fruit"
}


def _create_folder_store(content: dict, suffix: str = "yml") -> str:
    dir = tempfile.TemporaryDirectory()
    for k, v in content.items():
        save(str(pathlib.Path(dir.name) / f"{k}.{suffix}"), v)
    return dir


def _dump_folder(folder):
    print("HISTORY: ")
    for i, h in enumerate(HISTORY):
        print(f"{i:-3d}: {h}")
    p = pathlib.Path(str(folder))
    print(f"Dump of folder {folder}:")
    for child in p.iterdir():
        print(f"  * {child.absolute()}")
        # with open(child) as filp:
        #     text = filp.read()
        for line in  load_txt( str(child.absolute()) ).split("\n"):
            print(f"    | {line}" )


HISTORY = []


def _folder_store_checks(content, folder, suffix):  # noqa: F811
    try:
        store = FolderStore( folder, suffix=suffix )
        Li = len(content)
        Lo = len(store)
        assert Lo == Li, f"Length of store was {Lo} instead of expected {Li}."

        for k in store.keys():
            assert k in list(content.keys()), f"Key '{k}' in FolderStore not present in config."

        for k in content.keys():
            assert k in list(store.keys()), f"Key '{k}' in config not present in FolderStore."

        for k, v in content.items():
            v2 = store[k]
            assert v2 == v, f"Store key '{k}' should be {v} but was {v2} instead."

        assert "12345" not in store, "Non-existing key '12345' failed to not be in store."

        assert "cherry" in store, "Existing key 'cherry' failed to be in store."

        del store["banana"]
        assert "banana" not in store, "Trying to remove key 'banana', but it still exists."

        store["xyz"] = "xyz"
        xyz = store["xyz"]
        assert xyz == "xyz", f"Trying to set key 'xyz' to 'xyz', but when accessed later returns '{xyz}'."

        store["xyz"] = "abc"
        xyz = store["xyz"]
        assert xyz == "abc", f"Trying to update key 'xyz' to 'abc', but when accessed later returns '{xyz}'."

        store.update(STORE_UPDATES)
        Li2 = len( STORE_UPDATES ) + Li
        Lo2 = len( store )
        assert Lo2 == Li2, f"After updating, length of store was {Lo2} instead of expected {Li2}."

        for k, v in STORE_UPDATES.items():
            v2 = store[k]
            assert v2 == v, f"After updating, store key '{k}' should be {v} but was {v2} instead."

        store.clear()
        Lo3 = len( store )
        assert Lo3 == 0, f"After clearing, length of store was {Lo3} instead of expected 0."
    except Exception:
        print(f"Suffix:   {store.suffix}")
        print(f"Pattern:  {store.pattern}")
        print(f"Template: {store.template}")
        _dump_folder(folder)
        raise


if HAVE_YAML:
    @pytest.fixture(autouse=True)
    def sample_yaml_store():
        content = {}
        content.update(**STORE_INITIAL_CONTENT)
        content.update(**STORE_YAML_ONLY_CONTENT)
        dir = _create_folder_store(content, suffix="yml")
        print(f"Created: {dir.name}")
        HISTORY.append(dir.name)
        yield content, dir.name
        shutil.rmtree(dir.name)
        HISTORY.clear()
        print(f"Destroyed: {dir.name}")

    def test_folder_store_yaml(sample_yaml_store):  # noqa: F811
        _folder_store_checks( *sample_yaml_store, suffix="yml" )


@pytest.fixture(autouse=True)
def sample_json_store():
    content = {}
    content.update(**STORE_INITIAL_CONTENT)
    dir = _create_folder_store(content, suffix="json")
    print(f"Created: {dir.name}")
    HISTORY.append(dir.name)
    yield content, dir.name
    shutil.rmtree(dir.name)
    HISTORY.clear()
    print(f"Destroyed: {dir.name}")


def test_folder_store_json(sample_json_store):  # noqa: F811
    _folder_store_checks( *sample_json_store, suffix="json" )
