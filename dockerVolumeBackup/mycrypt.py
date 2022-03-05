#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crypto."""
# Created on Sun Feb 06 2022 by Merlin Mittelbach.

from datetime import datetime
from getpass import getpass
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import Optional, Tuple

from cryptography.fernet import Fernet
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.hashes import SHA256

RSA_PUBLIC_EXPONENT = 65537
RSA_KEY_SIZE = 4*2**10
PADDING = OAEP(
    mgf=MGF1(SHA256()),
    algorithm=SHA256(),
    label=None
)
BLOCK_SIZE = 2**20
logger = getLogger(__file__)


class AsymmetricFernetError(Exception):
    """Asymmetric fernet related error."""


def load_public_key(certificate_pem: BytesIO) -> rsa.RSAPublicKey:
    """Load RSA certificate.

    Args:
        certificate_pem (BytesIO): PEM encoded x.509 certificate byte stream

    Raises:
        AsymmetricFernetError: Public key other than RSA used.

    Returns:
        rsa.RSAPublicKey: public key
    """
    certificate = x509.load_pem_x509_certificate(certificate_pem.read())
    public_key = certificate.public_key()
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise AsymmetricFernetError(
            f"Only RSA public key supported, not '{type(public_key)}'"
        )
    else:
        return public_key


def load_private_key(
    key_pem: BytesIO,
    password: Optional[bytes]
) -> rsa.RSAPublicKey:
    """Load RSA private key.

    Args:
        key_pem (BytesIO): PEM encoded RSA private key byte stream
        password (Optional[bytes]): password to decrypt private key

    Raises:
        AsymmetricFernetError: Private key other than RSA used.

    Returns:
        rsa.RSAPublicKey: public key
    """
    private_key: rsa.RSAPrivateKey = \
        serialization.load_pem_private_key(
            key_pem.read(), password
        )
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise AsymmetricFernetError(
            f"Only RSA private key supported, not '{type(private_key)}'"
        )
    else:
        return private_key


def encrypt(
    file_path: Path,
    public_key: rsa.RSAPublicKey,
    block_size: int = BLOCK_SIZE
) -> None:
    """Encrypt procedure.

    Args:
        file_path (Path): file to be encrypted
        public_key (rsa.RSAPublicKey): public key to encrypt fernet key
        block_size (int, optional): Size of encryption blocks.
            Defaults to BLOCK_SIZE.
    """
    key = Fernet.generate_key()
    fernet = Fernet(key)
    key_encrypted = public_key.encrypt(
        plaintext=key,
        padding=PADDING
    )
    with open(
        file_path.with_suffix(
            file_path.suffix + ".crypt"
        ),
        "wb"
    ) as bytesio_out:
        # first 512 bytes are the fernet key
        bytesio_out.write(key_encrypted)

        with open(file_path, "rb") as bytesio_in:
            while block := bytesio_in.read(block_size):
                block_crypt = fernet.encrypt(block)
                # 4 bytes block length
                bytesio_out.write(
                    int.to_bytes(
                        len(block_crypt),
                        length=4, byteorder="big", signed=False
                    )
                )
                # encrypted block
                bytesio_out.write(block_crypt)
    logger.debug(
        "Successfully encrypted '%s'.",
    )


def decrypt(
    private_key: rsa.RSAPrivateKey,
    file_path: Path,
    file_path_out: Path = None
):
    """Decrypt method.

    Args:
        private_key (rsa.RSAPrivateKey): Private key used for encryption.
        file_path (Path): encrypted file
        file_path_out (Path, optional): Name of decrypted file.
            Defaults to file_path without '.crypt' if that is the
            file extension. Otherwise file_path_out will be file_path
            with '.decrypt' extension.
    """
    # prepare output file name
    if file_path_out is None:
        if file_path.name.endswith(".crypt"):
            file_path_out = file_path.with_name(
                file_path.name.removesuffix(".crypt")
            )
        else:
            file_path_out = file_path.with_name(
                file_path.name + ".decrypt"
            )
    if file_path_out.exists():
        raise FileExistsError(
            f"Decryption output file '{file_path_out}' already exists."
        )

    # start decrypting
    with open(file_path, "rb") as bytesio_in:
        fernet = Fernet(
            private_key.decrypt(
                bytesio_in.read(512),
                PADDING
            )
        )
        with open(file_path_out, "wb") as bytesio_out:
            while block_size := bytesio_in.read(4):
                encrypted_block = bytesio_in.read(
                    int.from_bytes(
                        block_size,
                        byteorder="big", signed=False
                    )
                )
                bytesio_out.write(
                    fernet.decrypt(encrypted_block)
                )
    logger.debug(
        "Successfully decrypted '%s'",
        file_path_out
    )


def gen_certificate(password: str = None) -> Tuple[bytes, bytes]:
    """Generate self signed certificate.

    Args:
        password (str, optional): Use password on private key.
            Defaults to None.

    Returns:
        Tuple[bytes, bytes]: private and public key in pem format
    """
    key = rsa.generate_private_key(
        public_exponent=RSA_PUBLIC_EXPONENT,
        key_size=RSA_KEY_SIZE
    )

    # issuer equals subject in self signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "file"),
    ])
    cert_builder = x509.CertificateBuilder(
        serial_number=x509.random_serial_number(),
        issuer_name=issuer,
        subject_name=subject,
        public_key=key.public_key(),
        not_valid_before=datetime(1980, 1, 1, 0),
        not_valid_after=datetime(2100, 1, 1, 0)
    )
    cert = cert_builder.sign(key, SHA256())
    key_encryption = serialization.BestAvailableEncryption(
        password.encode()
    ) if password else serialization.NoEncryption()
    return (
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=key_encryption
        ),
        cert.public_bytes(encoding=serialization.Encoding.PEM)
    )


def prompt_private_key(public_key: rsa.RSAPublicKey) -> rsa.RSAPrivateKey:
    """Prompt for private key.

    Args:
        public_key (rsa.RSAPublicKey): corresponding public key

    Raises:
        AsymmetricFernetError: Could not load private key.

    Returns:
        rsa.RSAPrivateKey: private key
    """
    for _ in range(3):
        key = getpass("Paste private key:")
        password = getpass("Password:")
        password = password.encode() if password else None
        try:
            private_key = load_private_key(BytesIO(key.encode()), password)
        except Exception as error:
            logger.warning("Failed to load private key: %s", repr(error))
        if private_key.public_key().public_numbers() == \
                public_key.public_numbers:
            return private_key
        else:
            logger.warning("Private key does not fit public key.")
            continue
    raise AsymmetricFernetError("Could not load private key.")
