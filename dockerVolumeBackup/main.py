#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backup and restore docker volumes."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.

from argparse import ArgumentParser
from getpass import getpass
from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from pathlib import Path
from typing import Any, Dict

from .mycrypt import \
    decrypt, encrypt, gen_certificate, load_public_key, prompt_private_key
from .tar import pack_lzma, unpack_lzma
from .storage import download, upload

DATA_DIR = Path("/data/")
CONFIG_DIR = Path("/config/")
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


def backup(bucket: str, name: str, **_: Dict[str, Any]) -> None:
    """Pack and encrypt data in '/data/'. Then upload to AWS S3 storage.

    Args:
        cert (Path): path to certificate used for encryption.
        bucket (str): bucket name
    """
    if is_dir_empty(DATA_DIR):
        logger.error("No point in backing up an empty volume.")
    else:
        logger.info("Loading certificate.")
        with open(CONFIG_DIR/"cert.pem", "rb") as bytesio:
            public_key = load_public_key(bytesio)

        logger.info("Packing data.")
        pack_lzma(DATA_DIR, Path("/tmp/backup.tar.xz"))

        logger.info("Encrypting data.")
        encrypt(Path("/tmp/backup.tar.xz"), public_key)

        logger.info("Uploading data.")
        upload(bucket, Path("/tmp/backup.tar.xz.crypt"), name)


def restore(bucket: str, name: str, **_: Dict[str, Any]) -> None:
    """Download backup, decrypt and unpack.

    Args:
        cert (Path): path to certificate used for encryption.
        bucket (str): bucket name
        name (str): name of file in bucket
    """
    if is_dir_empty(DATA_DIR):
        logger.info("Loading certificate.")
        with open(CONFIG_DIR/"cert.pem", "rb") as bytesio:
            public_key = load_public_key(bytesio)
        private_key = prompt_private_key(CONFIG_DIR/"key.pem")
        if private_key is None:
            logger.error("Could not load private key.")
        elif private_key.public_key().public_numbers() != \
                public_key.public_numbers():
            logger.error(
                "Private key does not belong to public key."
            )
        else:
            logger.info("Downloading backup.")
            download(bucket, name, Path("/tmp/backup.tar.xz.crypt"))
            logger.info("Decrypting backup.")
            decrypt(private_key, Path("/tmp/backup.tar.xz.crypt"))
            logger.info("Unpacking backup.")
            unpack_lzma(Path("/tmp/backup.tar.xz"))
    else:
        logger.error("Volume must be empty.")


def gen_cert(**_: Dict[str, Any]) -> None:
    """Generate self signed certificate."""
    if CONFIG_DIR.exists():
        logger.info(
            "Specify password for private key. Leave empty for no password."
        )
        # double check if password is correct
        while True:
            try:
                password = getpass("Password:")
                if password:
                    if password == getpass("Confirm password:"):
                        break
                    else:
                        logger.info(
                            "Password confirmation failed. Try again."
                        )
                else:
                    password = None
            except EOFError:
                logger.warning(
                    "No tty. Generate certificate without password."
                )
                password = None
                break
        priv, pub = gen_certificate(password)

        # prevent overwrite
        keypath = ensure_unique(CONFIG_DIR/"key.pem")
        with open(keypath, "wb") as bytesio:
            bytesio.write(priv)
        logger.info("Successfully wrote '%s'", keypath)

        certpath = ensure_unique(CONFIG_DIR/"cert.pem")
        with open(certpath, "wb") as bytesio:
            bytesio.write(pub)
        logger.info("Successfully wrote '%s'", certpath)
    else:
        logger.error("No output directory mounted.")


def main():
    """Entrypoint."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", help="enable debug log")
    subparsers = parser.add_subparsers(help="Choose mode.", required=True)

    # backup subparser
    backup_parser = subparsers.add_parser(
        "backup", help="Backup files mounted to /data/ to AWS S3 storage."
    )
    backup_parser.set_defaults(func=backup)
    backup_parser.add_argument(
        "bucket", type=str, help="Select bucket to store backup."
    )
    backup_parser.add_argument(
        "name", type=str, help="Name of file in bucket."
    )

    # restore backup subparser
    restore_parser = subparsers.add_parser(
        "restore", help="Restore files from AWS S3 storage to /data/."
    )
    restore_parser.set_defaults(func=restore)
    restore_parser.add_argument(
        "bucket", type=str, help="Select bucket to restore backupfrom."
    )
    restore_parser.add_argument(
        "name", type=str, help="Name of file in bucket."
    )

    # generate certificate subparser
    gen_cert_parser = subparsers.add_parser(
        "gencert", help="Generate self-signed certificate."
    )
    gen_cert_parser.set_defaults(func=gen_cert)

    # parse
    args = parser.parse_args()

    # setup logging
    root_logger = getLogger()
    loghandler = StreamHandler()
    loghandler.setFormatter(
        Formatter("%(asctime)s %(levelname)s:%(message)s")
    )
    root_logger.addHandler(loghandler)
    root_logger.setLevel(
        DEBUG if args.verbose else INFO
    )

    # run
    args.func(**args.__dict__)


if __name__ == "__main__":
    main()
