Changelog
=========


[0.1.0] - 2022-02-??
--------------------

This is the first release of :py:mod:`manen`. The package is still under development
and so the public API might changed in the future.

Added
^^^^^

- :py:func:`~manen.finder.find` allows to easily get element(s) in a WebDriver
  page. This function support several very different use cases, mainly parametrized
  with the function arguments.
- :py:mod:`~manen.resource` is a module to easily interact with all the assets
  needed by Selenium. Thanks to that, all the drivers required by Selenium to work
  will no longer causes issues.
- :py:mod:`~manen.browser` defined :py:class:`~manen.browser.ChromeBrowser`
  and :py:class:`~manen.browser.BraveBrowser`, an enhanced Selenium's WebDriver.
- :py:mod:`~manen.page_object_model` is the implementation of `page object
  modelling described in Selenium documentation <https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/>`_.
  Thanks to that, you can describe the DOM structure only with Python objects.
- a :py:mod:`~manen.cli` is shipped with the initial release in order to download
  webdrivers.
