#!usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: ZhuravlevDmi
:license: Apache License, version 2.0, see LICENSE file
"""

version = "0.1.1"

long_description = "..."

setup(
    name="wbxSearch",
    version=version,
    author="ZhuravlevDmi",
    author_email="Dima15129@gmail.com",

    description=(u"Удобный инструмент для работы с выдачами"),
    long_description=long_description,
    url="https://github.com/ZhuravlevDmi/wbxSearch",
    download_url="https://github.com/ZhuravlevDmi/wbxSearch/archive/v{}.zip".format(version),

    license="Apache License, version 2.0, see LICENSE file",
    packages=["wbxSearch"],
    install_requires=[],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        # "Programming Language :: Python :: 3",
        # "Programming Language :: Python :: 3.5",
        # "Programming Language :: Python :: 3.6",
        # "Programming Language :: Python :: 3.7",
        # "Programming Language :: Python :: 3.8",
        # "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ]

)
