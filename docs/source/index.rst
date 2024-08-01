.. manen documentation master file, created by
   sphinx-quickstart on Sat Mar 28 20:08:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Manen documentation!
-------------------------------

:py:mod:`manen` is a package built to extend Selenium user experience.
Among the core features, you can find:

- an implementation of the `page object model <https://www.selenium.dev/documentation/en/
  guidelines_and_recommendations/page_object_models/>`_ design pattern
- a class which completes :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`
- a function to easily find and isolate DOM elements inside a page

This package allows you to write more concise, flexible and powerful code compared to
what you would do by using only Selenium. Here is a comparison of the same code written
with and without Manen:

.. tab:: With Manen

   .. code-block:: ipython

      from datetime import datetime
      from typing import Annotated

      from selenium.webdriver.chrome.webdriver import WebDriver

      from manen.page_object_model.config import CSS, Default, Wait, XPath
      from manen.page_object_model.component import Page, Component


      class BlogPage(Page):
         class Article(Component):
            title: Annotated[str, XPath("//h1")]
            n_likes: Annotated[int, CSS("span.n_likes")]
            tags: Annotated[list[str], CSS("span.tag"), Default([])]
            updated_at: Annotated[datetime, CSS("span.updated_at")]

         articles: Annotated[list[Article], CSS('div.article'), Wait(3)]


      driver = WebDriver()

      page = BlogPage(driver)
      article = page.articles[0]

      print(article.model_dump())
      # {
      #   'title': 'Hello, Manen!',
      #   'n_likes': 42,
      #   'tags': ['python', 'selenium'],
      #   'updated_at': datetime.datetime(2021, 1, 1, 0, 0)
      # }


.. tab:: Without Manen

   .. code-block:: ipython

      from dateparser import dateparser
      from selenium.common.exceptions import NoSuchElementException
      from selenium.webdriver.common.by import By
      from selenium.webdriver.support import expected_conditions as EC
      from selenium.webdriver.support.ui import WebDriverWait

      driver = WebDriver()

      articles = WebDriverWait(driver, 3).until(
          EC.presence_of_elements_located((By.CSS, "article"))
      )
      title = articles[0].find_element(By.CSS_SELECTOR, "h1").text
      n_likes = int(articles[0].find_element(By.CSS_SELECTOR, "span.n_likes").text)
      try:
          tags = articles[0].find_element(By.CSS_SELECTOR, "span.tags")
      except NoSuchElementException:
          tags = []
      updated_at = dateparser(articles[0].find_element(By.CSS_SELECTOR, "p.date").text)

      print({'title': title, 'n_likes': n_likes, 'tags': tags, 'updated': updated_at})
      # {
      #   'title': 'Hello, Manen!',
      #   'n_likes': 42,
      #   'tags': ['python', 'selenium'],
      #   'updated_at': datetime.datetime(2021, 1, 1, 0, 0)
      # }


Besides being more concise, the version using Manen is also more verbose, meaning
that it can ease the comprehension of your source code.

You can find a deeper explanation that motivated the development of Manen in the
section :ref:`Why such package?`.


.. toctree::
   :hidden:

   ./about.rst
   ./installation.rst
   ./user_guide.rst
   ./manen/manen.rst
   ./contributing.rst
   ./changelog.rst
