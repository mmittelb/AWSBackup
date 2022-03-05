#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backup and restore docker volumes."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.

from argparse import ArgumentParser
from getpass import getpass
from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from pathlib import Path
from typing import Any, Dict

from .mycrypt import decrypt, encrypt, load_public_key, prompt_private_key
from .tar import pack_lzma, unpack_lzma
from .storage import download, upload

KEY_OUTPUT_DIR = Path("/keyout/")
logger = getLogger(__file__)


def ensure_unique(filepath: Path) -> Path:
    """Ensure file path is unique.

    Args:
        filepath (Path): original file path

    Returns:
        Path: unique file path
    """
    orig_name = filepath.name
    counter = 0
    while filepath.exists():
        filepath = filepath.with_name(orig_name+f"_{counter}")
        counter += 1
    return filepath


def is_dir_empty(dirname: Path) -> bool:
    """Check if directory is empty.

    Args:
        dirname (Path): path to directoy

    Raises:
        RuntimeError: dirname is not a directory

    Returns:
        bool: true if empty
    """
    if dirname.is_dir():
        return len(list(dirname.iterdir())) == 0
    else:
        raise RuntimeError(f"{dirname} is not a directory.")


def backup(cert: Path, bucket: str, name: str, **_: Dict[str, Any]) -> None:
    """Pack and encrypt data in '/data/'. Then upload to AWS S3 storage.

    Args:
        cert (Path): path to certificate used for encryption.
        bucket (str): bucket name
    """
    if is_dir_empty(Path("/data/")):
        logger.error("No point in backing up an empty volume.")
    else:
        logger.info("Loading certificate.")
        with open(cert, "rb") as bytesio:
            public_key = load_public_key(bytesio)

        logger.info("Packing data.")
        pack_lzma(Path("/data/"), Path("/tmp/backup.tar.xz"))

        logger.info("Encrypting data.")
        encrypt(Path("/tmp/backup.tar.xz"), public_key)

        logger.info("Uploading data.")
        upload(bucket, Path("/tmp/backup.tar.xz.crypt"), name)


def restore(cert: Path, bucket: str, name: str, **_: Dict[str, Any]) -> None:
    """Download backup, decrypt and unpack.

    Args:
        cert (Path): path to certificate used for encryption.
        bucket (str): bucket name
        name (str): name of file in bucket
    """
    if is_dir_empty(Path("/data/")):
        logger.info("Loading certificate.")
        with open(cert, "rb") as bytesio:
            public_key = load_public_key(bytesio)
        private_key = prompt_private_key(public_key)
        logger.info("Downloading backup.")
        download(bucket, name, Path("/tmp/backup.tar.xz.crypt"))
        logger.info("Decrypting backup.")
        decrypt(private_key, Path("/tmp/backup.tar.xz.crypt"))
        logger.info("Unpacking backup.")
        unpack_lzma(Path("/tmp/backup.tar.xz.crypt"))
    else:
        logger.error("Volume must be empty.")


def gen_cert(**_: Dict[str, Any]) -> None:
    """Generate self signed certificate."""
    if KEY_OUTPUT_DIR.exists():
        logger.info(
            "Specify password for private key. Leave empty for no password."
        )
        try:
            password = getpass()
            password = password if password else None
        except EOFError:
            logger.warning("No tty. Generate certificate without password.")
            password = None
        priv, pub = AsymmetricFernet.gen_certificate(password)

        # never overwrite
        keypath = ensure_unique(KEY_OUTPUT_DIR/"key.pem")
        with open(keypath, "wb") as bytesio:
            bytesio.write(priv)
        logger.info("Successfully wrote '%s'", keypath)

        certpath = ensure_unique(KEY_OUTPUT_DIR/"cert.pem")
        with open(certpath, "wb") as bytesio:
            bytesio.write(pub)
        logger.info("Successfully wrote '%s'", certpath)
    else:
        logger.error("No output directory mounted.")


def main():
    """Main entry point."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", help="enable debug log")
    subparsers = parser.add_subparsers(help="Choose mode.", required=True)

    backup_parser = subparsers.add_parser(
        "backup", help="Backup files mounted to /data/ to AWS S3 storage."
    )
    backup_parser.set_defaults(func=backup)
    backup_parser.add_argument(
        "--cert", type=Path, default=Path("/cert/cert.pem"),
        help="Path to certificate file. Defaults to '/cert/cert.pem'."
    )
    backup_parser.add_argument(
        "bucket", type=str, help="Select bucket to store backup."
    )
    backup_parser.add_argument(
        "name", type=str, help="Name of file in bucket."
    )

    gen_cert_parser = subparsers.add_parser(
        "gencert", help="Generate self-signed certificate."
    )
    gen_cert_parser.set_defaults(func=gen_cert)

    args = parser.parse_args()

    root_logger = getLogger()
    loghandler = StreamHandler()
    loghandler.setFormatter(
        Formatter("%(asctime)s %(levelname)s:%(message)s")
    )
    root_logger.addHandler(loghandler)
    root_logger.setLevel(
        DEBUG if args.verbose else INFO
    )
    args.func(**args.__dict__)


if __name__ == "__main__":
    main()
