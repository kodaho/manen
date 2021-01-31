.. manen documentation master file, created by
   sphinx-quickstart on Sat Mar 28 20:08:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to manen's documentation!
-------------------------------------

.. image:: https://img.shields.io/badge/python-%3E=3.6-informational?style=for-the-badge&logo=python
.. image:: https://img.shields.io/badge/version-0.1.0-informational?style=for-the-badge
.. image:: https://img.shields.io/badge/status-in%20development-yellow?style=for-the-badge


:py:mod:`manen` is a package built around Selenium to ....

In simple terms, it will let you design production-ready application based on Selenium.


.. tab:: Before

   du code


.. tab:: After

   du code


Why manen?
==========

.. todo::

   Add pain points encoutered when working with Selenium


Design to be be simple and speed up your development with Selenium.

Can be used for scraping (legal scraping of course), testing and automatize
heavy process. Goal is to be build a reliable tool which can be used
in production.

List of features include :

- find and download all drivers needed by Selenium; no need to find the right
  version of the assets: :py:mod:`manen` will do it for you
- easy interaction with the DOM structure through an implementation of
  `Page Object Model`
- a lot more to be discovered and to come...


Current status and roadmap
==========================

Still under active development but used internally for quite a time.

Feebacks are welcomed.

Keep 0 as major version (because manen uses `semantic versioning <https://semver.org>`_)
until it is ready for the first stable release. No guarantee that the API will remain the
same but no intention to change it for now.

No roadmap because it is still a "side project" but you can follow the project through this
documentation and Github's issues.


Table of contents
=================
.. toctree::
   :maxdepth: 2

   ./installation.rst
   ./user_guide.rst
   ./manen/manen.rst
   ./changelog.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
