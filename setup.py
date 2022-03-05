#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup package."""
# Created on Fri Mar 04 2022 by Merlin Mittelbach.

from setuptools import setup, find_packages

setup(
    name='dockerVolumeBackup',
    version='0.1.0',
    packages=find_packages(include=['dockerVolumeBackup']),
    install_requires=[
        "cryptography",
        "boto3"
    ],
    entry_points={
        'console_scripts': ['volumeBackup=dockerVolumeBackup.main:main']
    },
    tests_require=["pytest"]
)
