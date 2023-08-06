#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pathlib import Path

name = 'robusdk'

setup(
    name = name,
    version = '0.0.12',
    keywords = [name],
    description = name,
    long_description=(Path(__file__).parent / 'readme.md').read_text(),
    long_description_content_type='text/markdown',
    license = 'UNLISENCED',
    url = 'http://255.255.255.255/',
    author = name,
    author_email = 'root@localhost.localdomain',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'aiohttp',
        'asyncio',
    ]
)
