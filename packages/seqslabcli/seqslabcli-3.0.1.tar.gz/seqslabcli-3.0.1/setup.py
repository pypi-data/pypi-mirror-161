#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
from typing import Union, Any

from setuptools import setup, find_packages

setup_file_loc: Union[Union[str, bytes], Any] = os.path.abspath(
    os.path.dirname(__file__))
# allow setup.py to be run from any path
os.chdir(setup_file_loc)

extras_require = {
}


def get_requirement():
    requirements = [    # dependency list
        'pip>=22.0.4'
    ]
    with open(os.path.join(setup_file_loc, 'python/requirements.txt'), 'r') as f:
        ori_req = f.read().splitlines()
    requirements.extend(ori_req)
    return requirements


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(setup_file_loc, package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def readme():
    path = os.path.join(setup_file_loc, 'python/seqslab', 'README.md')
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


setup(
    name='seqslabcli',
    version=get_version('python/seqslab'),
    author="Jia-You Lin",
    author_email='jiayou.lin@atgenomix.com',

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        # https://pypi.org/pypi?%3Aaction=list_classifiers
    ],
    description="Seqslab CLI",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/AnomeGAP/seqslab-cli",
    license="MIT license",

    packages=find_packages(where='python'),
    package_dir={'': 'python'},

    include_package_data=True,
    install_requires=get_requirement(),
    extras_require=extras_require,
    python_requires='>=3.8',
    zip_safe=True,

    entry_points={
        'console_scripts': [
            'seqslab = seqslab.cli:main',
            # setting console scripts, you can call seqslab to run cmd
        ],
    }

)
