#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config file for installing/publishing cmpdisktree
"""

# For a fully annotated version of this file and what it does, see
# https://github.com/pypa/sampleproject/blob/master/setup.py

import ast
import io
import os
import re

from setuptools import find_packages, setup

DEPENDENCIES = ['click','tqdm']
EXCLUDE_FROM_PACKAGES = ['contrib', 'docs', 'tests*']
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, 'README.md'), 'r', encoding='utf-8') as f:
    README = f.read()


def get_version():
    """Version for setup function"""
    main_file = os.path.join(CURDIR, 'cmpdisktree', '__init__.py')
    _version_re = re.compile(r'__version__\s+=\s+(?P<version>.*)')
    with open(main_file, 'r', encoding='utf8') as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


setup(
    name='cmpdisktree',
    version=get_version(),
    author='halloleo',
    author_email='cmpdisktree@halloleo.hailmail.net',
    description="Compare Directories as macOS Disk Structures",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/halloleo/cmpdisktree',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    keywords=['system', 'man', 'help'],
    scripts=[],
    entry_points={'console_scripts': ['cmpdisktree=cmpdisktree.main:main']},
    zip_safe=False,
    install_requires=DEPENDENCIES,
    test_suite='tests.test_project',
    python_requires='>=3.6',
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license='License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
