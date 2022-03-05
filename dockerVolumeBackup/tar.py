#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tar related procedures."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.

from logging import getLogger
from pathlib import Path
from tarfile import open as taropen
from subprocess import CalledProcessError, run

logger = getLogger(__file__)


def pack_lzma(path: Path, archive_path: Path):
    """Create lzma compressed tar archive.

    Args:
        path (Path): file(s) to compress
        archive_path (Path): path to archive
    """
    if not _pack_lzma_subprocess(path, archive_path):
        # fall back to python
        with taropen(archive_path, "w|xz") as archive:
            archive.add(path)


def _pack_lzma_subprocess(path: Path, archive_path: Path) -> bool:
    """Create lzma compressed tar archive using system binary.

    Args:
        path (Path): file(s) to compress
        archive_path (Path): path to archive

    Returns:
        bool: True on success
    """
    try:
        run(
            ["tar", "cJf", archive_path, path],
            check=True,
            text=True,
            capture_output=True
        )
        return True
    except CalledProcessError as error:
        logger.warning(
            "Running tar failed. stdout: '%s' stderr: '%s'",
            error.stdout.encode("string_escape"),
            error.stderr.encode("string_escape")
        )
        return False


def unpack_lzma(archive_path: Path):
    """Decompress lzma compressed tar archive.

    Args:
        archive_path (Path): path to archive
    """
    if not _unpack_lzma_subprocess(archive_path):
        # fall back to python
        with taropen(archive_path, "r|xz") as archive:
            archive.extractall(path="/")


def _unpack_lzma_subprocess(archive_path: Path) -> bool:
    """Decompress lzma compressed tar archive using system binary.

    Args:
        archive_path (Path): path to archive

    Returns:
        bool: True on success
    """
    try:
        run(
            ["tar", "xJf", archive_path],
            check=True,
            text=True,
            capture_output=True
        )
        return True
    except CalledProcessError as error:
        logger.warning(
            "Running tar failed. stdout: '%s' stderr: '%s'",
            error.stdout.encode("string_escape"),
            error.stderr.encode("string_escape")
        )
        return False
