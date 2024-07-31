Changelog
=========

.. |topic| raw:: html

  <span style="display: inline-block; width: 110px; font-size:85%; font-weight: 600;">Topic</span> <span style="font-size:85%">

.. |released_on| raw:: html

  <span style="display: inline-block; width: 110px; font-size:85%; font-weight: 600;">Release date</span> <span style="font-size:85%">

.. |end| raw:: html

  </span>


0.3.0
-----

|topic| Page object model implementation revamp & other major changes |end|

|released_on| (unreleased) |end|

.. warning::

  Even if it's a minor release, this version represents a major change for the project; the
  package has been mostly rewritten in order to implement the page object model design pattern in
  a more efficient way (using type annotation).

  Besides, some functionalities have been removed with the aim of limiting the number of features
  during the beta phase.

  All previous versions should be considered as deprecated.


Changed
^^^^^^^
- The module :py:mod:`~manen.page_object_model` has been rewritten to use type annotation instead
  of ``Element``. Note that some elements like select or radio button haven't been implemented in
  this new version yet (but will be in the future).
- Most of the documentation pages have been rewritten and improved.
- Most modules have better typing annotations and documentation. Besides, the code has been
  improved to be more "Pythonic".
- Manen no longer has optional dependencies (which were in fact development dependencies).
- The minimal version of Python required is now 3.10.
- Internally, Manen is now using `rye <https://rye.astral.sh/guide/>`_ as project manager, and
  `ruff <https://docs.astral.sh/ruff/>`_ for the linting and formatting.

Removed
^^^^^^^
- The module ``manen.resource`` and everything related (like the CLI) have been removed. Indeed,
  the `official Selenium manager <https://www.selenium.dev/documentation/selenium_manager/>`_
  (available as a CLI tool and in recent versions of Python bindings for Selenium) provides the
  same functionalities.
- ``manen.browser.BraveBrowser`` has been removed because it had a dependency on the module
  ``manen.resource``. Besides, it was considered as not enough tested internally to make it
  available publicly.

|

0.2.0
-----

|topic| Rename some classes in :py:mod:`~manen.page_object_model` and improve CLI |end|

|released_on| 2022-02-19 |end|

Added
^^^^^
- Specify link to changelog in documentation in package metadata.
- Introduce new options in ``manen driver download`` to set the specifications of the drivers
  to be downloaded directly from the command line.
- Add exhaustibility in documentation of :py:mod:`~manen.page_object_model` to describe
  private/special methods and classes other than the ones in ``__all__``.

Changed
^^^^^^^

- Improve CLI command to download drivers executable (now launched with ``manen driver download``).
- Rename :py:class:`~manen.page_object_model.DateTimeElement` (previously ``DatetimeElement``).
- Rename :py:class:`~manen.page_object_model.DOMAccessor` (previously ``DomAccessor``).

Fixed
^^^^^
- Fix link to notebooks in the info section of :ref:`User Guide`

|

0.1.2
-----

|topic|  Fix bug in the download workflow of the CLI |end|

|released_on| 2022-02-19 |end|

Fixed
^^^^^

- Fix a ``TypeError`` in the download workflow (variable wrongly named).

|

0.1.1
-----

|topic| Mainly documentation improvements |end|

|released_on| 2022-02-12 |end|

Changed
^^^^^^^

- Make documentation publicly available under
  `kodaho.github.io/manen <https://kodaho.github.io/manen/>`_.
- Complete README page.
- Add the section `About the project` in the documentation (moved from home page).
- Complete user guides.
- Rewording and reformatting of several sections.

|

0.1.0
-----

|topic| First release of the package |end|

|released_on| 2022-01-31 |end|

Added
^^^^^

- :py:func:`~manen.finder.find` allows to easily get element(s) in a WebDriver
  page. This function support several very different use cases, thanks to several
  arguments that can be passed to the function.
- :py:mod:`~manen.resource` is a module to easily interact with all the assets
  needed by Selenium. It allows for example to download the drivers, executable
  required to launch a WebDriver.
- :py:mod:`~manen.browser` defined :py:class:`~manen.browser.ChromeBrowser`
  and :py:class:`~manen.browser.BraveBrowser`, an enhanced Selenium WebDriver.
- :py:mod:`~manen.page_object_model` is the implementation of `page object
  model <https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/>`_
  described in Selenium documentation. Thanks to that, you can describe and
  interact with the DOM structure through Python classes.
- A :py:mod:`~manen.cli` is shipped with the initial release in order to download
  drivers files.
