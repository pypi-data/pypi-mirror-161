#!/bin/false
# -*- coding: utf-8 -*-

"""
This module provides unit tests for `ptutils.io`.
"""


import os
import tempfile
import pytest
import shutil
from ptutils.encoding import (
    HAVE_YAML,
    encode_json,
    decode_json,
    encode_yaml,
    decode_yaml
)
from ptutils.globbing import scan_folder
from ptutils.io import (
    get_path_part,
    get_hash_tmp_dir,
    get_filetype,
    makedirs,
    read,
    read_lines,
    read_all,
    write_all,
    HAVE_TAR,
    require_tar,
    extract_archive,
    compress_archive,
    load_txt,
    save_txt,
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    get_encoder,
    get_decoder,
    get_loader,
    get_saver,
    load,
    save,
)
from ._fs_fixture import (  # noqa: F401
    localize_path,
    sample_file_structure,
    FILE_STRUCTURE
)


FILE_TYPE_TEST_CASES = [
    ("/etc/myapp/config.json", "json"),
    ("/etc/myapp/config.jsn", "json"),
    ("/etc/myapp/config.yaml", "yaml"),
    ("/etc/myapp/config.yml", "yaml"),
    ("/etc/myapp.json/config.yml", "yaml"),
    ("/etc/myapp.yaml/config.jsn", "json"),
    ("/etc/myapp/data.zip", "archive-zip"),
    ("/etc/myapp/data.tar", "archive-tar"),
    ("/etc/myapp/data.bz2", "archive-bzip2"),
    ("/etc/myapp/data.gz", "archive-gzip"),
    ("/etc/myapp/data.tar.bz2", "archive-bzip2"),
    ("/etc/myapp/data.tar.gz", "archive-gzip"),
    ("myapp/config.json", "json"),
    ("myapp/config.jsn", "json"),
    ("myapp/config.yaml", "yaml"),
    ("myapp/config.yml", "yaml"),
    ("myapp.json/config.yml", "yaml"),
    ("myapp.yaml/config.jsn", "json"),
    ("myapp/data.zip", "archive-zip"),
    ("myapp/data.tar", "archive-tar"),
    ("myapp/data.bz2", "archive-bzip2"),
    ("myapp/data.gz", "archive-gzip"),
    ("myapp/data.tar.bz2", "archive-bzip2"),
    ("myapp/data.tar.gz", "archive-gzip"),
    ("config.json", "json"),
    ("config.jsn", "json"),
    ("config.yaml", "yaml"),
    ("config.yml", "yaml"),
    ("config.yml", "yaml"),
    ("config.jsn", "json"),
    ("data.zip", "archive-zip"),
    ("data.tar", "archive-tar"),
    ("data.bz2", "archive-bzip2"),
    ("data.gz", "archive-gzip"),
    ("data.tar.bz2", "archive-bzip2"),
    ("data.tar.gz", "archive-gzip"),
]


@pytest.mark.parametrize(
    argnames  = ["path", "expected"],
    argvalues = FILE_TYPE_TEST_CASES,
    ids       = [f"{x[0]},type={x[1]}" for x in FILE_TYPE_TEST_CASES]
)
def test_get_file_type(path, expected):
    filename = localize_path(path)
    assert get_filetype(filename) == expected


PATH_PART_TEST_CASES = [
    (
        "/a/b/c.tar.gz",
        {
            "fullpath":  "/a/b/c.tar.gz",
            "abspath":   "/a/b/c.tar.gz",
            "name":      "c.tar.gz",
            "extension": "gz",
            "basename":  "c.tar"
        }
    ),
    (
        "/a/b/../c.tar.bz2",
        {
            "fullpath":  "/a/b/../c.tar.bz2",
            "abspath":   "/a/c.tar.bz2",
            "name":      "c.tar.bz2",
            "extension": "bz2",
            "basename":  "c.tar"
        }
    ),
    (
        "c.zip",
        {
            "fullpath":  "c.zip",
            "abspath":   os.path.abspath(os.path.join(os.curdir, "c.zip")),
            "name":      "c.zip",
            "extension": "zip",
            "basename":  "c"
        }
    ),
    (
        "/README",
        {
            "fullpath":  "/README",
            "abspath":   os.path.abspath("/README"),
            "name":      "README",
            "extension": '',
            "basename":  "README"
        }
    ),
]
PATH_PART_LABELS = [
    "fullpath",
    "abspath",
    "name",
    "extension",
    "basename",
]


@pytest.mark.parametrize(
    argnames = "part",
    argvalues = PATH_PART_LABELS,
    ids       = [f"PART={label}" for label in PATH_PART_LABELS]
)
@pytest.mark.parametrize(
    argnames = ["path", "expectations"],
    argvalues = PATH_PART_TEST_CASES,
    ids       = [ x[0] for x in PATH_PART_TEST_CASES ]
)
def test_get_path_part(path, expectations, part):
    filename = localize_path(path)
    result   = localize_path(expectations[part])
    assert get_path_part(filename=filename, part=part) == result


def test_get_path_part_raises_for_unknown_part():
    with pytest.raises(ValueError) as _:
        get_path_part(filename="/path/to/a/file.ext", part="unknown")


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


def test_makedirs_creates_all(sample_file_structure):  # noqa: F811
    parts = ["apples", "lesser-known", "from-mexico", "juarez"]
    folder = os.path.join(localize_path('/'.join(parts)))
    makedirs(folder)
    for i in range(1, len(parts)):
        assert os.path.isdir(
            os.path.join(localize_path('/'.join(parts[:i])))
        )


def test_makedirs_fails_when_a_parent_is_a_file(sample_file_structure):  # noqa: F811
    parts = ["apples", "granny-smith", "lesser-known", "from-mexico", "juarez"]
    folder = os.path.join(sample_file_structure, localize_path('/'.join(parts)))
    filename = os.path.join(sample_file_structure, "apples/granny-smith")
    assert os.path.isfile(filename)
    with pytest.raises(OSError) as _:
        makedirs(folder)
    assert os.path.isdir(os.path.dirname(filename))
    assert os.path.isfile(filename)


def test_read(sample_file_structure):  # noqa: F811
    folder = os.path.join(sample_file_structure, 'boring_things')
    f1     = os.path.join(folder, 'thing.json')
    assert read(f1) == FILE_STRUCTURE['boring_things']['thing.json']
    f2     = os.path.join(folder, 'text_thing')
    assert read(f2) == FILE_STRUCTURE['boring_things']['text_thing']
    assert read_all(f1) == FILE_STRUCTURE['boring_things']['thing.json']
    assert read_all(f2) == FILE_STRUCTURE['boring_things']['text_thing']
    assert load_txt(f1) == FILE_STRUCTURE['boring_things']['thing.json']
    assert load_txt(f2) == FILE_STRUCTURE['boring_things']['text_thing']


def test_write(sample_file_structure):  # noqa: F811
    folder = os.path.join(sample_file_structure, 'boring_things', 'tbd_things')
    f1     = os.path.join(folder, 'tbd.txt')
    write_all(f1, FILE_STRUCTURE['boring_things']['text_thing'])
    assert read(f1) == FILE_STRUCTURE['boring_things']['text_thing']


def test_txt(sample_file_structure):  # noqa: F811
    folder = os.path.join(sample_file_structure, 'boring_things', 'tbd_things')
    f1     = os.path.join(folder, 'tbd.txt')
    save_txt(f1, FILE_STRUCTURE['boring_things']['text_thing'])
    assert load_txt(f1) == FILE_STRUCTURE['boring_things']['text_thing']


def test_get_encoder():
    assert get_encoder("x.json") is encode_json
    assert get_encoder("x.jsn") is encode_json
    assert get_encoder("x.yaml") is encode_yaml
    assert get_encoder("x.yml") is encode_yaml
    with pytest.raises(Exception) as _:
        get_encoder("x.txt")
    with pytest.raises(Exception) as _:
        get_encoder("x")


def test_get_decoder():
    assert get_decoder("x.json") is decode_json
    assert get_decoder("x.jsn") is decode_json
    assert get_decoder("x.yaml") is decode_yaml
    assert get_decoder("x.yml") is decode_yaml
    with pytest.raises(Exception) as _:
        get_decoder("x.txt")
    with pytest.raises(Exception) as _:
        get_decoder("x")


def test_get_loader():
    assert get_loader("x.json") is load_json
    assert get_loader("x.jsn") is load_json
    assert get_loader("x.yaml") is load_yaml
    assert get_loader("x.yml") is load_yaml
    with pytest.raises(Exception) as _:
        get_loader("x.txt")

    assert get_loader("x", default=load_txt) is load_txt


def test_get_saver():
    assert get_saver("x.json") is save_json
    assert get_saver("x.jsn") is save_json
    assert get_saver("x.yaml") is save_yaml
    assert get_saver("x.yml") is save_yaml
    with pytest.raises(Exception) as _:
        get_saver("x.txt")

    assert get_saver("x", default=save_txt) is save_txt


STRUCTURED_DATA = {
    "a_bool": True,
    "An_int": 123,
    "An_float": 123.456,
    "a string": "hello world",
    "A list of things": [
        True,
        None,
        "hello",
        [],
        123,
        456.789
    ],
    "a dict": {
        "a": 123,
        "b": True,
        "c": "hi",
        "d": dict(),
        "e": list()
    }
}


def test_round_trip_json_file(sample_file_structure):  # noqa: F811
    f1 = os.path.join(sample_file_structure, 'something.json')
    save_json(f1, STRUCTURED_DATA)
    assert load_json(f1) == STRUCTURED_DATA


def test_round_trip_yaml_file(sample_file_structure):  # noqa: F811
    if HAVE_YAML:
        f1 = os.path.join(sample_file_structure, 'something.yaml')
        save_yaml(f1, STRUCTURED_DATA)
        assert load_yaml(f1) == STRUCTURED_DATA
    else:
        pytest.skip("No YAML support")


def test_round_trip_save_load(sample_file_structure):  # noqa: F811
    f1 = os.path.join(sample_file_structure, 'something.json')
    save(f1, STRUCTURED_DATA)
    assert load(f1) == STRUCTURED_DATA

    if HAVE_YAML:
        f1 = os.path.join(sample_file_structure, 'something.yaml')
        save(f1, STRUCTURED_DATA)
        assert load(f1) == STRUCTURED_DATA
    else:
        pytest.skip("No YAML support")


def test_get_hash_tmp_dir():
    for case in [
        "",
        "a/b/c",
        "/a/b"
    ]:
        d1 = get_hash_tmp_dir(case)
        d2 = os.path.dirname(d1)
        assert d2 == tempfile.gettempdir()
        assert isinstance(d1, str)
        assert bool(d1)
        assert not os.path.isdir(d1)
        assert os.path.isdir(d2)


def test_read_lines(sample_file_structure):  # noqa: F811
    content_lines = [
        "rootfs / lxfs rw,noatime 0 0",
        "none /dev tmpfs rw,noatime,mode=755 0 0",
        "sysfs /sys sysfs rw,nosuid,nodev,noexec,noatime 0 0",
        "proc /proc proc rw,nosuid,nodev,noexec,noatime 0 0",
        "devpts /dev/pts devpts rw,nosuid,noexec,noatime,gid=5,mode=620 0 0",
        "none /run tmpfs rw,nosuid,noexec,noatime,mode=755 0 0",
        "none /run/lock tmpfs rw,nosuid,nodev,noexec,noatime 0 0",
        "none /run/shm tmpfs rw,nosuid,nodev,noatime 0 0",
        "none /run/user tmpfs rw,nosuid,nodev,noexec,noatime,mode=755 0 0",
        "binfmt_misc /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0",
        "tmpfs /sys/fs/cgroup tmpfs rw,nosuid,nodev,noexec,relatime,mode=755 0 0",
        "cgroup /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0"
    ]
    content = os.linesep.join(content_lines)
    filename = os.path.join(sample_file_structure, 'boring_things', 'tbd_things', 'a-text-file.txt')
    write_all(filename, content)
    assert read(filename) == content
    assert read_lines(filename) == content_lines


def test_require_tar():
    if HAVE_TAR:
        require_tar()
    else:
        with pytest.raises(Exception) as _:
            require_tar()


def test_archive_round_trip(sample_file_structure):  # noqa: F811
    with pytest.raises(NotImplementedError) as _:
        extract_archive(archive=localize_path("/file.zip"), folder=localize_path("/tmp"))
    with pytest.raises(NotImplementedError) as _:
        extract_archive(archive=localize_path("/file.7z"), folder=localize_path("/tmp"))
    if not HAVE_TAR:
        with pytest.raises(Exception) as _:
            extract_archive(archive=localize_path("/file.tar.gz"), folder=localize_path("/tmp"))
    else:
        source_folder   = sample_file_structure
        source_contents = [ os.path.relpath(x, source_folder) for x in list(scan_folder(source_folder))]

        archive         = os.path.join(tempfile.gettempdir(), 'something.tar.gz')
        dest_folder     = os.path.join(tempfile.gettempdir(), 'something.tar.gz.contents')
        try:
            compress_archive(archive=archive, folder=source_folder)
            assert os.path.isfile( archive )
            extract_archive(archive=archive, folder=dest_folder)
            assert os.path.isdir( dest_folder )
            dest_contents = [ os.path.relpath(x, dest_folder) for x in list(scan_folder(dest_folder))]
            assert dest_contents == source_contents
        finally:
            try:
                os.unlink(archive)
            except:  # noqa: E722
                pass
            try:
                shutil.rmtree(dest_contents)
            except:  # noqa: E722
                pass
