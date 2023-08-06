#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

name = 'robusdk'

setup(
    name = name,
    version = '0.0.10',
    keywords = [name],
    description = name,
    long_description = name,
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
