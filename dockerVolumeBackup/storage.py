#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Storage connector classes."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.
from pathlib import Path

from boto3 import client


def upload(bucket: str, file_path: Path, uploaded_filename: str) -> None:
    """Upload file to AWS S3 bucket root.

    Args:
        bucket (str): bucket name
        file_path (Path): path to file
        uploaded_filename (str): name of file in bucket
    """
    s3_client = client("s3")
    s3_client.upload_file(str(file_path), bucket, uploaded_filename)


def download(bucket: str, file_name: str, downloaded_filename: Path):
    """Download file from AWS S3 bucket root.

    Args:
        bucket (str): bucket name
        file_name (str): name of file in bucket
        downloaded_filename (Path): name of local file
    """
    s3_client = client("s3")
    s3_client.download_file(
        bucket,
        file_name,
        str(downloaded_filename)
    )
