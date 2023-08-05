========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/atpt/badge/?style=flat
    :target: https://atpt.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/dinner-group/atpt/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/dinner-group/atpt/actions

.. |requires| image:: https://requires.io/github/dinner-group/atpt/requirements.svg?branch=release
    :alt: Requirements Status
    :target: https://requires.io/github/dinner-group/atpt/requirements/?branch=release

.. |codecov| image:: https://codecov.io/gh/dinner-group/atpt/branch/release/graphs/badge.svg?branch=release
    :alt: Coverage Status
    :target: https://codecov.io/github/dinner-group/atpt

.. |version| image:: https://img.shields.io/pypi/v/atpt.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/atpt

.. |wheel| image:: https://img.shields.io/pypi/wheel/atpt.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/atpt

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/atpt.svg
    :alt: Supported versions
    :target: https://pypi.org/project/atpt

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/atpt.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/atpt

.. |commits-since| image:: https://img.shields.io/github/commits-since/dinner-group/atpt/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/dinner-group/atpt/compare/v0.0.0...release



.. end-badges

Implementation of augmented transition path theory.

* Free software: MIT license

Installation
============

::

    pip install atpt

You can also install the in-development version with::

    pip install https://github.com/dinner-group/atpt/archive/release.zip


Documentation
=============


https://atpt.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
