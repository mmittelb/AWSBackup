#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This is a very important module."""
# Created on Thu Feb 03 2022 by Merlin Mittelbach.

from base64 import b64encode
from pathlib import Path
from random import randbytes
from shutil import rmtree

from dockerVolumeBackup.tar import pack_lzma, unpack_lzma


def test_tar(tmp_path: Path):
    """test tar and untar

    Args:
        tmp_path (Path): temp directory
    """
    test_dir = tmp_path.joinpath("test_dir/")
    test_dir.mkdir()
    rand_str1 = b64encode(randbytes(50)).decode()
    rand_str2 = b64encode(randbytes(50)).decode()
    archive_path = tmp_path.joinpath("test_dir.tar.xz")

    with open(test_dir.joinpath("test1"), "w") as textio:
        textio.write(rand_str1)
    with open(test_dir.joinpath("test2"), "w") as textio:
        textio.write(rand_str2)
    pack_lzma(test_dir, archive_path)
    rmtree(test_dir)
    assert not test_dir.exists()
    unpack_lzma(archive_path)

    assert test_dir.exists()
    assert test_dir.joinpath("test1").exists()
    assert test_dir.joinpath("test2").exists()
    with open(test_dir.joinpath("test1")) as textio:
        assert rand_str1 == textio.read()
    with open(test_dir.joinpath("test2")) as textio:
        assert rand_str2 == textio.read()
