#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from ValiotWorker import __version__

requirements = [
    # TODO: put package requirements here
    'pygqlc>=3.0.1',
    'pydash',
    'pytz',
    'tzlocal',
    'colorama',
    'termcolor',
    'python-dateutil',
    'singleton-decorator',
    'redis',
]

setup_requirements = [
    # TODO(alanbato): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
    'pytest',
    'pytest-cov',
]

desc = "Enables running Python functions as standalone jobs based on interaction with valiot-jobs API"
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ValiotWorker',
    version=__version__,
    description=desc,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Valiot",
    author_email="hiring@valiot.io",
    url='https://github.com/valiot/python-gql-worker',
    packages=find_packages(include=['ValiotWorker']),
    entry_points={
        'console_scripts': [
            'ValiotWorker=ValiotWorker.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='ValiotWorker',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
