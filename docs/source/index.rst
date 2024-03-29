.. manen documentation master file, created by
   sphinx-quickstart on Sat Mar 28 20:08:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to manen's documentation!
---------------------------------

.. image:: https://img.shields.io/badge/python-%3E=3.6-informational?style=for-the-badge&logo=python
   :alt: Python Version
.. image:: https://img.shields.io/pypi/v/manen?logo=pypi&style=for-the-badge
   :alt: Package Version
   :target: https://pypi.org/project/manen
.. image:: https://img.shields.io/badge/status-in%20development-yellow?style=for-the-badge
   :alt: Status


:py:mod:`manen` is a package built to extend Selenium user experience.
Among the core features, you can find:

- an implementation of the `page object model <https://www.selenium.dev/documentation/en/
  guidelines_and_recommendations/page_object_models/>`_
- a class which completes :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`
- some helpers to manage resources usually required by Selenium
- a function to easily find and isolate DOM elements inside a page

This package will allow you to write more concise, flexible and powerful code compared to
what you could do by using only Selenium. For example, here is a comparison of the same
code with and without ``manen``:

.. tab:: With manen

   .. code-block:: ipython

      In [1]: from manen import page_object_model as pom
         ...:
         ...: class BlogPage(pom.Page):
         ...:     class Article(pom.Regions):
         ...:         title = pom.TextElement("h1")
         ...:         n_likes = pom.IntegerElement("span.n_likes")
         ...:         tags = pom.TextElements("span.tag", default=[])
         ...:         updated_at = pom.DateElement("p.date")
         ...:
         ...:     articles = Article("article", wait=3)
         ...:
         ...: page = BlogPage(driver)
         ...: article = page.articles[0]

      In [2]: article.title, article.n_likes, article.tags, article.updated_at
      Out[2]: ('manen, a new tool around Selenium', 100, [], datetime.date(2021, 1, 1))

.. tab:: Without manen

   .. code-block:: ipython

      In [1]: from dateparser import dateparser
         ...: from selenium.common.exceptions import NoSuchElementException
         ...: from selenium.webdriver.common.by import By
         ...: from selenium.webdriver.support import expected_conditions as EC
         ...: from selenium.webdriver.support.ui import WebDriverWait
         ...:
         ...: articles = WebDriverWait(driver, 3).until(
         ...:     EC.presence_of_elements_located((By.CSS, "article"))
         ...: )
         ...: title = articles[0].find_element_by_css("h1").text
         ...: n_likes = int(articles[0].find_element_by_css("span.n_likes").text)
         ...: try:
         ...:     tags = articles[0].find_elements_by_css("span.tags")
         ...: except NoSuchElementException:
         ...:     tags = []
         ...: updated_at = dateparser(articles[0].find_element_by_css("p.date").text)

      In [2]: title, n_likes, tags, updated_at
      Out[2]: ('manen, a new tool around Selenium', 100, [], datetime.date(2021, 1, 1))

Besides being more concise, the version using ``manen`` is also more verbose, meaning
that it can ease the comprehension of your source code.

You can find a deeper explanation that motivated the development of ``manen`` in the
section :ref:`Why such package?`.

Table of contents
=================
.. toctree::
   :maxdepth: 3

   ./about.rst
   ./installation.rst
   ./user_guide.rst
   ./manen/manen.rst
   ./changelog.rst
   ./contributing.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
