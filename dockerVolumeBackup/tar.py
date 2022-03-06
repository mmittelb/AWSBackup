#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tar related procedures."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.

from logging import getLogger
from pathlib import Path
from tarfile import open as taropen
from subprocess import CalledProcessError, run
from typing import List

logger = getLogger(__file__)


def call_tar(cmd: List[str], raise_exc=False) -> bool:
    """Call tar subprocess.

    Args:
        cmd (List[str]): command parameters
        raise_exc (bool, optional): Raise exception on error.
            Defaults to False.

    Raises:
        CalledProcessError: execution failed

    Returns:
        bool: True if tar successfully finished
    """
    success = False
    try:
        run(
            ["tar", *cmd],
            check=True,
            text=True,
            capture_output=True
        )
        success = True
    except CalledProcessError as error:
        logger.warning(
            "Running tar failed. stdout: '%s' stderr: '%s'",
            error.stdout.encode("string_escape"),
            error.stderr.encode("string_escape")
        )
        if raise_exc:
            raise error
    return success


def pack_bzip2(path: Path, archive_path: Path) -> None:
    """Create bzip2 compressed tar archive.

    Args:
        path (Path): file(s) to compress
        archive_path (Path): path to archive
    """
    call_tar(["-c", "-Ipbzip2", "-f", archive_path, path], raise_exc=True)


def unpack_bzip2(archive_path: Path) -> None:
    """Decompress bzip2 compressed tar archive. Uses pbzip2 library.

    Args:
        archive_path (Path): path to archive
    """
    call_tar(["-x", "-Ipbzip2", "-f", archive_path], raise_exc=True)


def pack_lzma(path: Path, archive_path: Path):
    """Create lzma compressed tar archive.

    Fall back to python if tar subprocess failed.

    Args:
        path (Path): file(s) to compress
        archive_path (Path): path to archive
    """
    if not call_tar(["cJf", archive_path, path]):
        # fall back to python
        with taropen(archive_path, "w|xz") as archive:
            archive.add(path)


def unpack_lzma(archive_path: Path):
    """Decompress lzma compressed tar archive.

    Args:
        archive_path (Path): path to archive
    """
    if not call_tar(["xJf", archive_path]):
        # fall back to python
        with taropen(archive_path, "r|xz") as archive:
            archive.extractall(path="/")
