"""``manen`` is a module to ease the interaction with Selenium. Its features
are splitted into four modules, where each module is independant:

- ``manen.resource`` : set of helpers to get the drivers needed by Selenium to work
- ``manen.finder``: define a function `find` in order to avoid calling the methods
  ``find_element`` or ``find_elements`` of a
  :py:class:`Selenium WebElement <selenium.webdriver.remote.webelement.WebElement>`
- ``manen.navigator``: a wrapper around `selenium.webdriver.remote.webdriver.WebDriver`
  to create more easily instance of web drivers. Compatible with Chrome and Firefox
- ``manen.page_object_model``: an implementation of Page Objects Model in order to easily
  interact with the DOM of a webpage of the DOM structure

Given that each module are independant, you can use one of the module without another one.
"""

__version__ = "0.1.0"
