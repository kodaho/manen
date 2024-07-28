Changelog
=========

.. |s| raw:: html

  ⇲ <span style="border-bottom: 1px dashed grey;padding-bottom: 2px; font-size:85%; margin-right:8px">Release date</span> <span style="font-size:90%">

.. |e| raw:: html

  </span>


0.3.0
-----

|s| (unreleased) |e|

Changed
^^^^^^^
- :py:mod:`~manen.page_object_model` has been entirely rewritten to use type annotation instead of `..Element` objects.

|

0.2.0
-----

|s| 2022-02-19 |e|

**Rename some classes in** :py:mod:`~manen.page_object_model` **and improve CLI**

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

|s| 2022-02-19 |e|

**Fix bug in the download workflow of the CLI**

Fixed
^^^^^

- Fix a ``TypeError`` in the download workflow (variable wrongly named).

|

0.1.1
-----

|s| 2022-02-12 |e|

**Mainly documentation improvements**

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

|s| 2022-01-31 |e|

**First release of the package**

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
- a :py:mod:`~manen.cli` is shipped with the initial release in order to download
  drivers files.
