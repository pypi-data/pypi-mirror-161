#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

VERSION = '0.0.1'
DESCRIPTION = '-'
LONG_DESCRIPTION = '-'

# Setting up
setup(
    name="xmc",
    version=VERSION,
    author="k-moussa (Karim Moussa)",
    author_email="<karimmoussa91@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ]
)
