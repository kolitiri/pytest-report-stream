#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-report-stream',
    version='0.1.0',
    author='Christos Liontos',
    author_email='christos.liontos.pr@gmail.com',
    maintainer='Christos Liontos',
    maintainer_email='christos.liontos.pr@gmail.com',
    license='MIT',
    url='https://github.com/kolitiri/pytest-report-stream',
    description='''
        A pytest plugin which allows to stream test reports at runtime
    ''',
    long_description=read('README.rst'),
    py_modules=['pytest_report_stream'],
    python_requires='>=3.9',
    install_requires=['pytest>=7.0.0', 'pytest_asyncio'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'report-stream = pytest_report_stream',
        ],
    },
)
