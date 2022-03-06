#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Storage connector classes."""
# Created on Fri Jan 28 2022 by Merlin Mittelbach.
from pathlib import Path

from boto3 import Session


class AWSBucket:
    """Provide up- and download functionality to AWS S3."""

    session: Session
    bucket: str

    def __init__(self, bucket: str) -> None:
        """AWSBucket constructor.

        Args:
            bucket (str): name of bucket
        """
        self.session = Session()
        self.bucket = bucket
        self._test_credentials()

    def _test_credentials(self) -> None:
        """Test credentials by listing bucket."""
        s3_client = self.session.client("s3")
        s3_client.list_objects_v2(Bucket=self.bucket)

    def upload(self, file_path: Path, uploaded_filename: str) -> None:
        """Upload file to AWS S3 bucket root.

        Args:
            file_path (Path): path to file
            uploaded_filename (str): name of file in bucket
        """
        s3_client = self.session.client("s3")
        s3_client.upload_file(
            str(file_path), self.bucket, uploaded_filename
        )

    def download(self, file_name: str, downloaded_filename: Path):
        """Download file from AWS S3 bucket root.

        Args:
            file_name (str): name of file in bucket
            downloaded_filename (Path): name of local file
        """
        s3_client = self.session.client("s3")
        s3_client.download_file(
            self.bucket,
            file_name,
            str(downloaded_filename)
        )
