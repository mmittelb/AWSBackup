#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test crypto module."""
# Created on Sun Feb 06 2022 by Merlin Mittelbach.

from io import BytesIO
from pathlib import Path
from random import randbytes
from dockerVolumeBackup.mycrypt import \
    decrypt, encrypt, gen_certificate, load_public_key, load_private_key


def test_encrypt(tmp_path: Path):
    """Test encryption and decryption of files.

    Args:
        tmp_path (Path): temp dir
    """
    priv, pub = gen_certificate()
    public_key = load_public_key(BytesIO(pub))
    file_path = tmp_path/"test.file"
    test_bytes = randbytes(5000)
    with open(file_path, "wb") as bytesio:
        bytesio.write(test_bytes)

    encrypt(file_path, public_key, block_size=1024)
    file_path_encrypted = file_path.with_suffix(file_path.suffix+".crypt")
    assert file_path_encrypted.exists()

    file_path.unlink()
    assert not file_path.exists()

    private_key = load_private_key(BytesIO(priv), None)
    decrypt(private_key, file_path_encrypted)
    assert file_path.exists()

    with open(file_path, "rb") as textio:
        assert test_bytes == textio.read()
