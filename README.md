<p align="center">
  <h1 align="center"> 🌔  manen</h1>
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/python-%3E=3.6-informational?style=for-the-badge&logo=python">
  <img alt="PyPI" src="https://img.shields.io/pypi/v/manen?logo=pypi&style=for-the-badge">
  <img src="https://img.shields.io/badge/status-in%20development-yellow?style=for-the-badge">
</p>

<p align="center">
  <i><b>A package around <a href="https://pypi.org/project/selenium/"><code>selenium</code></a> to easily construct Python objects which reflect the DOM of any webpages.</b></i>
</p>

---

<p align="center">
  <a href="https://pypi.org/project/manen">PyPI package</a>
  ・
  <a href="https://kodaho.github.io/manen/">Documentation</a>
  ・
  <a href="https://github.com/kodaho/manen/issues">Issue tracking</a>
</p>

`manen` is a package built to extend Selenium user experience.
Among the core features, you can find:

- an implementation of the [page object model](https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/)
- a class which completes `selenium.webdriver.remote.webdriver.WebDriver`
- a function to easily find and isolate DOM elements inside a page

This package will allow you to write more concise, flexible and powerful code compared to
what you could do by using only Selenium.

## 📥 Installation

The package can be installed using the official package manager `pip`.

```bash
pip install manen
```

## ✨ Features

- `manen.finder.find` allows to easily get element(s) in a HTML page. This function support
  several very different use cases, to help reduce your code complexity when fecthing for
  elements.
- `manen.browser` defined `Browser` objects, an enhanced Selenium's `WebDriver`.
- `manen.page_object_model` is the implementation of page object model described in Selenium
  documentation. Thanks to that, you can wrap a HTML page inside Python class and so provides
  readability and stability to your code.

## 🚀 Getting started

`manen` offers several features described in the [User Guide](https://kodaho.github.io/manen/user_guide.html)
of the documentation. We will give here a minimal example of what can be done with it; the goal will be to use
Selenium to explore the PyPI page of `manen` and extract some information from it.

The first step is to create an instance of a Selenium `WebDriver` or Manen `WebBrowser` that will be
used to browse the Internet.

```python
from manen.browser import ChromeBrowser

browser = ChromeBrowser.initialize(proxy=None, headless=True)
browser.get("https://pypi.org")
```

![PyPI home page](./docs/assets/screenshot_pypi_home.png)

We are now on the home page of PyPI. What we are going to do now is interact with the webpage
using a manen `Page`. It will essentially use the package
[`manen.page_object_model`](https://kodaho.github.io/manen/manen/manen.page_object_model.html), that
stores all the classes used to do the interface with each web element.

```python
from manen.page_object_model.webarea import Page, WebArea
from manen.page_object_model import dom

class HomePage(Page):
    query: Annotated[Input, dom.CSS("input[id='search']")]


class SearchResultPage(Page):
    class Result(WebArea):
        name: Annotated[str, dom.CSS("h3 span.package-snippet__name")]
        version: Annotated[str, dom.CSS("h3 span.package-snippet__version")]
        link: Annotated[dom.HRef, dom.CSS("a.package-snippet")]
        description: Annotated[str, dom.CSS("p.package-snippet__description")]

    nb_results: Annotated[int, dom.XPath("//*[@id='content']//form/div[1]/div[1]/p/strong")]
    results: Annotated[list[Result], dom.CSS("ul[aria-label='Search results'] li")]
```

The `Page` class is used to modelize a whole WebDriver page; all elements defined inside the class
should modelize a given element on the page, identified with the selectors (XPath, CSS or else).
For example, the class `TextElement` will extract the text from a HTML element, `LinkElement` will
extract the `href` attribute from an `a` tag. A lot of different classes exist, all of them in charge
of a special extraction; they are defined and documented in the module
[`manen.page_object_model`](https://kodaho.github.io/manen/manen/manen.page_object_model.html).

The class `Region` is used to modelize a sub-part of a webpage. Each region can have its own inner
elements. You can have as many imbricated levels as wanted.

For example, the class `HomePage` defines an `InputElement` that do the link with the search bar.
To fill a value in this search bar, you can simply assign a value to the attribute `query` of
the instance of an `HomePage`, initialized with `browser` as argument.

```python
from manen.page_object_model import Action

page = HomePage(browser)
page.query = "manen"
page.query = Action("submit")
```

Submitting the form will refer to a page with the results of our query. Let's use the class
`SearchResultPage` to retrieve the results.

![PyPI home page](./docs/assets/screenshot_pypi_search_results.png)

```python
page = SearchResultPage(browser)

print(page.nb_results)
# 1

print(page.results)
# [<__main__.SearchResultPage.ResultRegions at 0x1058e97c0>]

print(page.results[0].model_dump())
```

Last step is to close the browser to avoid any remaining running application once we close Python.

```python
browser.quit()
```

## 🦾 Going further

The best way to have full knowledge of the package is to read
[the documentation of the project](https://kodaho.github.io/manen/)!

If you want to have the exhaustive list of improvements of the package, check the
[Changelog](https://kodaho.github.io/manen/changelog.html) page.

Looking to contribute to fix or add new features? Just read
[this page](https://kodaho.github.io/manen/contributing.html),
fork the official repository and start doing the modifications you want.
