.. manen documentation master file, created by
   sphinx-quickstart on Sat Mar 28 20:08:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to manen's documentation!
---------------------------------

.. image:: https://img.shields.io/badge/python-%3E=3.6-informational?style=for-the-badge&logo=python
.. image:: https://img.shields.io/pypi/v/manen?logo=pypi&style=for-the-badge
.. image:: https://img.shields.io/badge/status-in%20development-yellow?style=for-the-badge


:py:mod:`manen` is a package built around Selenium to ....

In simple terms, it will let you design production-ready application based on Selenium.


.. tab:: With manen

   .. code-block:: python

      from manen import page_object_model as pom

      class BlogPage(pom.Page):
         class Article(pom.Regions):
            title = pom.TextElement('h1')
            n_likes = pom.IntegerElement('span.n_likes')
            tags = pom.TextElements('span.tag', default=[])
            updated_at = pom.DateElement('p.date')

         articles = Article('article', wait=3)

      page = BlogPage(driver)
      article = page.articles[0]
      print(article.title, article.n_likes, article.tags, article.updated_at)
      # ('manen, a new tool around Selenium',
      #  100,
      #  [], # Because no tags were found
      #  datetime.date(2021, 1, 1))

.. tab:: Without manen

   .. code-block:: python

      from dateparser import dateparser
      from selenium.common.exceptions import NoSuchElementException
      from selenium.webdriver.common.by import By
      from selenium.webdriver.support import expected_conditions as EC
      from selenium.webdriver.support.ui import WebDriverWait

      articles = WebDriverWait(driver, 3).until(
         EC.presence_of_elements_located((By.CSS, "article"))
      )
      title = articles[0].find_element_by_css('h1').text
      n_likes = int(articles[0].find_element_by_css('span.n_likes').text)
      try:
         tags = articles[0].find_elements_by_css('span.tags')
      except NoSuchElementException:
         tags = []
      updated_at = dateparser(articles[0].find_element_by_css('p.date').text)

      print(title, n_likes, tags, updated_at)
      # ('manen, a new tool around Selenium',
      #  100,
      #  [], # Because no tags were found
      #  datetime.date(2021, 1, 1))


Why ``manen``?
==============

.. todo::

   Add pain points encoutered when working with Selenium


Design to be be simple and speed up your development with Selenium.
Hide complexity to work with Selenium.

Can be used for scraping (legal scraping of course), testing and automatize
heavy process. Goal is to be build a reliable tool which can be used
in production.

Among the features, you will find:

- a helper tool to find and download all drivers needed by Selenium; no need to
  find the right driver compatible with the installed browser, :py:mod:`manen`
  will do it for you!
- a quite complete list of classes you can use to easily interact with the DOM
  structure: it is basically an implementation of the
  `page object model <https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_)
  described in official documentation of Selenium.
- an enhanced WebDriver, build around the one defined by Selenium, allowing you
  to perform some basic actions quite quickly.


Current status and roadmap
==========================

:py:mod:`manen` is still under active development but has been used on some
private projects for quite a time.

Feebacks are more than welcome so don't hesitate to open a Github issue if you
have any questions or concerns about the project!

Because manen uses `semantic versioning <https://semver.org>`_, it will keep 0
as major version until it is ready for the first stable release.

.. note:: There is no guarantee that the API will remain the same. The current
   architecture is probably the definitive one, but some breaking changes can
   be introduced if needed. Any change will be detailed in the ChangeLog page.

No roadmap because it is still a "side project" but you can follow the project through this
documentation and Github's issues.


Table of contents
=================
.. toctree::
   :maxdepth: 3

   ./installation.rst
   ./user_guide.rst
   ./manen/manen.rst
   ./changelog.rst
   ./contributing.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
