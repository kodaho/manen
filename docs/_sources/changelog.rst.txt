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

|released_on| 2026-05-07 |end|

.. warning::

  Even if it's a minor release, this version represents a major change for the project; the
  package has been mostly rewritten in order to implement the page object model design pattern in
  a more efficient way (using type annotation).

  Besides, some functionalities have been removed with the aim of limiting the number of features
  during the beta phase.


Changed
^^^^^^^
- :py:mod:`~manen.page_object_model` has been completely rewritten around type annotations. Pages
  are described by annotating attributes with native Python types (``str``, ``int``, ``float``,
  ``date``, ``datetime``, ``bool``, ``list``, ...) instead of the former ``Element`` subclasses.
  The public API is now split into three submodules:

  - ``manen.page_object_model.component``: :py:class:`~manen.page_object_model.component.Page`,
    :py:class:`~manen.page_object_model.component.Component` (replacing ``WebArea``) and
    :py:class:`~manen.page_object_model.component.Form` (replacing ``Action``).
  - ``manen.page_object_model.config``: selectors and modifiers ``CSS``, ``XPath``, ``LinkText``,
    ``PartialLinkText``, ``Attribute``, ``Wait``, ``Default``, ``DateFormat`` and
    ``DatetimeFormat``.
  - ``manen.page_object_model.types``: type aliases such as ``href``, ``src``, ``inner_html``,
    ``outer_html``, ``input_value`` and ``checkbox``.

- :py:class:`~manen.browser.BrowserMixin.is_browser_compatible_with_driver` replaces the former
  ``are_versions_compatible``.
- :py:func:`~manen.finder.find` is now fully typed through overloads.
- Manen no longer has optional dependencies, and ``selenium`` is now its only runtime dependency.
- The minimal supported version of Python is now 3.10.
- Most of the documentation has been rewritten and improved.

Added
^^^^^
- :py:class:`~manen.browser.ScrollDirection` and :py:class:`~manen.browser.HeadlessMode` enums to
  configure the browser.
- :py:class:`~manen.exceptions.PollTimeoutException`, raised when an element is not found within
  the configured waiting time.

Removed
^^^^^^^
- The module ``manen.resource`` and everything related (including the ``manen`` CLI) have been
  removed. The `official Selenium manager <https://www.selenium.dev/documentation/selenium_manager/>`_
  now provides the same functionalities.
- ``manen.browser.BraveBrowser`` has been removed; it depended on ``manen.resource`` and was not
  tested enough to be exposed publicly.
- The selector-as-string elements (``Element``, ``TextElement``, ``LinkElement``,
  ``IntegerElement``, ``DateTimeElement``, ...) as well as ``Region``/``Regions`` and the
  YAML page loaders have been dropped in favour of the new type-annotation based API.

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
