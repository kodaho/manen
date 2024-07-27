"""
manen.page_object_model
=======================

This module provides an implementation of the `Page Object design pattern
<https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
described in Selenium documentation. By combining the classes
:py:class:`~manen.page_object_model.Page` and :py:class:`~manen.page_object_model.Region`
with the :py:class:`~manen.page_object_model.Element` object (and all its subclasses),
you can easily describe any web pages and access all the DOM elements in a simple
way through a Python class.

Let's say that you want, given a query, to get all the packages information from
the website `PyPi <https://pypi.org/>`_ (e.g.: "selenium"). The first step to
work with :py:mod:`manen.page_object_model` is to define the Python classes which
will describe the web pages you are working on. Here we will define all the
classes in an external file called ``pypi_pom.py``.

.. code-block:: python

    from manen.page_object_model import (Page, Regions, InputElement,
                                         TextElement, LinkElement,
                                         IntegerElement)

    class HomePage(Page):
        query = InputElement("input[id='search']")

    class SearchResultPage(Page):
        class ResultRegions(Regions):
            name = TextElement("h3 span.package-snippet__name")
            version = TextElement("h3 span.package-snippet__version")
            link = LinkElement("a.package-snippet")
            description = TextElement("p.package-snippet__description")

        n_results = IntegerElement("//*[@id='content']//form/div[1]/div[1]/p/strong")
        results = ResultRegions("ul[aria-label='Search results'] li")


Once you have defined all the classes describing the web pages, you can start
interacting by instanciating the :py:class:`~manen.page_object_model.Page` subclass
with an instance of :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`. Here
we will suppose that you have an instance of
:py:class:`~selenium.webdriver.remote.webdriver.WebDriver` stored in the variable
``browser``.

.. code-block:: python

    >>> from pypi_pom import HomePage, SearchResultPage
    >>> home_page = HomePage(browser)
    >>> home_page.query = "selenium"
    >>> home_page.query = Action("submit")
    # This will direct you to a search result page of PyPi.
    >>> browser.current_url
    "https://pypi.org/search/?q=selenium"
    >>> page = SearchResultPage(browser)
    >>> page.n_results
    1600
    >>> len(page.results)
    20
    >>> page.results[0]
    <pypi_pom.ResultRegions>
    >>> page.results[0].name
    "selenium"
    >>> page.results[0].version
    "3.141.0"
    >>> page.results[0].link
    "https://pypi.org/project/selenium/"

This is a glitch of what you can do with :py:mod:`manen.page_object_model`. See the
documentation of each objects to check all the features provided by the module.
"""
