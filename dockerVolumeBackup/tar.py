#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tar related procedures."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.

from pathlib import Path
from tarfile import open as taropen


def pack_lzma(path: Path, archive_path: Path):
    """Create lzma compressed tar archive.

    Args:
        path (Path): file(s) to compress
        archive_path (Path): path to archive
    """
    with taropen(archive_path, "w|xz") as archive:
        archive.add(path)


def unpack_lzma(archive_path: Path):
    """Decompress lzma compressed tar archive.

    Args:
        archive_path (Path): path to archive
    """
    with taropen(archive_path, "r|xz") as archive:
        archive.extractall(path="/")
