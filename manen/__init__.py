""":py:mod:`manen` is a module to ease the interaction with Selenium. Its features
are splitted into four modules, where each module is independant:

- :py:mod:`manen.resource` : set of helpers to get the drivers needed by Selenium to work
- :py:mod:`manen.finder`: define a function :py:func:`~manen.finder.find` in order to
  avoid calling the methods ``find_element`` or ``find_elements`` of a
  :py:class:`Selenium WebElement <selenium.webdriver.remote.webelement.WebElement>`
- :py:mod:`manen.navigator`: a wrapper around
  :py:class:`~selenium.webdriver.remote.webdriver.WebDriver` to more easily create
  instance of web drivers. Onyl compatible with Chrome (for now).
- :py:mod:`manen.page_object_model`: an implementation of the design pattern Page
  Objects Model in order to easily interact with the DOM of a webpage.

Each module are built to be quite independant from each other. For example, you can
use the module :py:mod:`manen.finder` without :py:mod:`manen.navigator` or
:py:mod:`manen.page_object_model` without :py:mod:`manen.navigator`.
"""

__version__ = "0.1.0"
