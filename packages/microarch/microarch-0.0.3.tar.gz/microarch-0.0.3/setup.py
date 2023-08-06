#!/usr/bin/env python
#
# Copyright (c) 2019-2022 Knuth Project
#

from setuptools import setup
from setuptools.command.install import install
import subprocess
import os

__title__ = "microarch"
__summary__ = "Knuth Microarchitecture Management (CPUID)"
__uri__ = "https://github.com/k-nuth/microarch"
__version__ = "0.0.3"
__author__ = "Fernando Pelliccioni"
__email__ = "fpelliccioni@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2019-2022 Knuth Project"


install_requires = [
    "cpuid >= 0.0.9",
]

class PostInstallCommand(install):
    """Override Install
    """
    def run(self):
        install.run(self)


setup(
    name = __title__,
    version = __version__,
    description = __summary__,
    long_description=open("./README.rst").read(),
    license = __license__,
    url = __uri__,
    author = __author__,
    author_email = __email__,

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],

    # What does your project relate to?
    keywords='knuth kth crypto bitcoin btc bch cash build tool',

    py_modules=["microarch"],

    install_requires=install_requires,
    # setup_requires=setup_requires,


    dependency_links=[
        'https://testpypi.python.org/pypi',
        # 'https://testpypi.python.org/pypi/cpuid-native/',
    ],

    cmdclass={'install': PostInstallCommand},

    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
)

