#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup package."""
# Created on Fri Mar 04 2022 by Merlin Mittelbach.

from pathlib import Path
from setuptools import setup, find_packages

with open(
    Path(__file__).parent/"requirements.txt",
    encoding="utf-8"
) as textio:
    # skip empty lines
    requirements = [
        package
        for package in textio.readlines()
        if package
    ]

setup(
    name='dockerVolumeBackup',
    version='0.1.0',
    packages=find_packages(include=['dockerVolumeBackup']),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['volumeBackup=dockerVolumeBackup.main:main']
    },
    tests_require=["pytest"]
)
