#!/usr/bin/env python3

from setuptools import setup

from deveba import __version__, DESCRIPTION

setup(
    name="deveba",
    version=__version__,
    description=DESCRIPTION,
    author="Aurélien Gâteau",
    author_email="mail@agateau.com",
    license="GPL3",
    platforms=["any"],
    url="https://github.com/agateau/deveba",
    packages=["deveba"],
    entry_points={
        "console_scripts": [
            "deveba = deveba.main:main",
        ],
    },
    install_requires=[
        "path.py==11.5.0",
        "svn==0.3.46",
    ],
    classifiers=[
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
