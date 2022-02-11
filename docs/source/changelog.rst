Changelog
=========

[0.1.1] - 2022-02-12
--------------------

**Mainly documentation improvements**

Changed
^^^^^^^

- Make documentation publicly available under
  `kodaho.github.io/manen <https://kodaho.github.io/manen/>`_.
- Complete `README.md` page.
- Add the section `About the project` in the documentation (moved from home page).
- Complete User Guide section.
- Rewording and reformatting of several sections.

[0.1.0] - 2022-01-31
--------------------

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
