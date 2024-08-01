"""
This module provides an implementation of the `Page Object design pattern
<https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
described in Selenium documentation. By combining the classes
:py:class:`~manen.page_object_model.component.Page` and :py:class:`~manen.page_object_model.component.Component`,
you can easily describe any web pages and access all the DOM elements in a simple
way through a Python class.

Let's say that you want, given a query, to get all the packages information from
the website `PyPi <https://pypi.org/>`_ (e.g.: "selenium"). The first step to
work with :py:mod:`manen.page_object_model` is to define the Python classes which
will describe the web pages you are working on. Here we will define all the
classes in an external file called ``pypi_pom.py``.

.. code-block:: python

    from datetime import datetime
    from typing import Annotated

    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.webdriver import WebDriver

    from manen.page_object_model.types import input_value
    from manen.page_object_model.component import Page, Component


    class HomePage(Page):
        class SearchForm(Form):
            query: Annotated[input_value, CSS("input[name='q']")]

        search: Annotated[SearchForm, CSS("form.search-form")]


    class SearchResultPage(Page):
        class Result(Component):
            name: Annotated[str, CSS("h3 span.package-snippet__name")]
            version: Annotated[str, CSS("h3 span.package-snippet__version")]
            link: Annotated[href, CSS("a.package-snippet")]
            description: Annotated[str, CSS("p.package-snippet__description")]
            release_date: Annotated[datetime, CSS("span.package-snippet__created")]

        nb_results: Annotated[
            int,
            XPath("//*[@id='content']//form/div[1]/div[1]/p/strong"),
        ]
        results: Annotated[
            list[Result],
            CSS("ul[aria-label='Résultats de recherche'] li"),
        ]


Once you have defined all the classes describing the web pages, you can start
interacting by instantiating the :py:class:`~manen.page_object_model.Page` subclass
with an instance of :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`. Here
we will suppose that you have an instance of
:py:class:`~selenium.webdriver.remote.webdriver.WebDriver` stored in the variable
``driver``.

.. code-block:: python

    >>> from pypi_pom import HomePage, SearchResultPage
    >>> home_page = HomePage(driver)
    >>> home_page.search.query = "selenium"
    >>> home_page.search.submit()
    # This will direct you to a search result page of PyPI.
    >>> page = SearchResultPage(driver)
    >>> page.nb_results
    2571
    >>> len(page.results)
    20
    >>> result = page.results[0]
    <pypi_pom.SearchResultPage.Result>
    >>> result.name
    'selenium'
    >>> result.release_date
    datetime.datetime(2024, 7, 24, 0, 0)}
    >>> result.model_dump()
    {'name': 'selenium',
     'version': '4.23.1',
     'link': 'https://pypi.org/project/selenium/',
     'description': 'Official Python bindings for Selenium WebDriver',
     'release_date': datetime.datetime(2024, 7, 24, 0, 0)}

This is a preview of what you can do with :py:mod:`~manen.page_object_model`. See the
documentation of each objects to check all the features provided by the module.
"""
