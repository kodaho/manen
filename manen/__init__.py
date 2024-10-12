"""
:py:mod:`manen` is a module to aiming to enhance developer experience when working on automation
and scraping project. Its features are splitted into (almost) independent modules:

- :py:mod:`~manen.finder`: define a function :py:func:`~manen.finder.find` in order to
  avoid calling the methods ``find_element`` or ``find_elements`` of a Selenium
  :py:class:`~selenium.webdriver.remote.webelement.WebElement`
- :py:mod:`~manen.browser`: a wrapper around
  :py:class:`~selenium.webdriver.remote.webdriver.WebDriver` to create more easily
  web driver instances. Only compatible with Chrome (for now).
- :py:mod:`~manen.page_object_model`: an implementation of the design pattern
  `Page Object Models <https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_,
  allowing to easily interact with the HTML DOM through classes with attributes and annotations.

Each module is built to be quite independent from each other. For example, you can
use the module :py:mod:`~manen.finder` without :py:mod:`~manen.browser` or
:py:mod:`~manen.page_object_model` without :py:mod:`~manen.browser`.
"""

__version__ = "0.3.0a8"
