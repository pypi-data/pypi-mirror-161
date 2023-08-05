#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(join(dirname(__file__), *names), encoding=kwargs.get('encoding', 'utf8')) as fh:
        return fh.read()


setup(
    name='atpt',
    version='0.0.0',
    license='MIT',
    description='Implementation of augmented transition path theory.',
    long_description='{}\n{}'.format(
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst')),
    ),
    author='Chatipat Lorpaiboon',
    author_email='chatipat@uchicago.edu',
    url='https://github.com/dinner-group/atpt',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
    ],
    project_urls={
        'Documentation': 'https://atpt.readthedocs.io/',
        'Changelog': 'https://atpt.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/dinner-group/atpt/issues',
    },
    keywords=[],
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'scipy',
    ],
    extras_require={},
)
