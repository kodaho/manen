"""
:py:mod:`manen` is a module to ease the interaction with Selenium. Its features
are splitted into four (almost) independant modules:

- :py:mod:`~manen.resource` : set of helpers to get the drivers needed by Selenium to work
- :py:mod:`~manen.finder`: define a function :py:func:`~manen.finder.find` in order to
  avoid calling the methods ``find_element_by_*`` or ``find_elements_by_*`` of a Selenium
  :py:class:`~selenium.webdriver.remote.webelement.WebElement`
- :py:mod:`~manen.browser`: a wrapper around
  :py:class:`~selenium.webdriver.remote.webdriver.WebDriver` to more easily create
  instance of web drivers. Only compatible with Chrome and Brave (for now).
- :py:mod:`~manen.page_object_model`: an implementation of the design pattern
  `Page Object Models <https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
  in order to easily interact with the DOM of a webpage.

Each module is built to be quite independant from each other. For example, you can
use the module :py:mod:`~manen.finder` without :py:mod:`~manen.browser` or
:py:mod:`~manen.page_object_model` without :py:mod:`~manen.browser`.
"""

__version__ = "0.1.1"
