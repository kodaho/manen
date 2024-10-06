<p align="center">
  <h1 align="center"> 🌔  Manen</h1>
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/python-%3E=3.10-informational?style=for-the-badge&logo=python">
  <img alt="PyPI" src="https://img.shields.io/pypi/v/manen?logo=pypi&style=for-the-badge">
  <img src="https://img.shields.io/badge/status-beta-yellow?style=for-the-badge">
</p>

<p align="center">
  <i>
    An implementation of the Page Object Model design pattern, and other utilities for web
    scraping and automation.
  </i>
</p>

---

<p align="center">
  <a href="https://pypi.org/project/manen">PyPI</a>
  ・
  <a href="https://kodaho.github.io/manen/">Documentation</a>
  ・
  <a href="https://kodaho.github.io/manen/changelog.html">Changelog</a>
  ・
  <a href="https://github.com/kodaho/manen/issues">Issue tracker</a>
</p>

Manen is a package built to enhance developer experience when using Selenium. Among the core
features, you can find:

- an implementation of the [Page Object Model](https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/)
  design pattern
- a class which improves the operability of a Selenium WebDriver
- a function to easily find and isolate DOM elements inside a Selenium page

This package aims to provide you the tools to write more concise, flexible and powerful code
compared to what you would do by using only Selenium.

> [!NOTE]
> For now, only Selenium Chrome WebDriver is supported. Other browsers will be supported in the
> future, as well as other automation tools such as Playwright or Scrapy.

## 📥 Installation

The package can be installed using the official Python package manager `pip`.

```bash
pip install manen
```

## ✨ Features

- `manen.finder.find` allows to easily get element(s) in a HTML page. This function support
  several very different use cases, to help reduce your code complexity when fetching for
  elements (example: using default values, trying different selectors, iterating over several
  elements).
- `manen.browser` defines an enhanced Selenium `WebDriver` called `Browser`
- `manen.page_object_model` is an implementation of the Page Object Model design pattern. It will
  wrap a HTML page, component and DOM values inside Python classes and objects, providing a better
  way to interact with a web page.

## 🚀 Getting started

Manen features will be explored by a simple example: going to the PyPI page, searching for a
specific package and extracting some information from the search results.

First thing to do is to initialize a WebDriver instance. It can be done using the usual way
provided by Selenium, but an alternative is to use the `Browser` class provided by Manen. Note
that both ways are equivalent, but `Browser` provides some additional features, that won't be
explored here.

```python
from manen.browser import ChromeBrowser

browser = ChromeBrowser.initialize()
browser.get("https://pypi.org")
```

![PyPI home page](https://raw.githubusercontent.com/kodaho/manen/main/docs/assets/screenshot_pypi_home.png)

We are now on the home page of PyPI. What we are going to do now is building a class that will
inherit from `Page` from the `manen.page_object_model.component` module. This Python class will be
a reflect of the HTML page, allowing us to access DOM elements in the same way we access
attributes. Note the whole page object model design pattern is implemented with type hints (a bit
like in `Pydantic` model).

```python
from manen.page_object_model.types import href, input_value
from manen.page_object_model.config import CSS, Attribute, DatetimeFormat, XPath
from manen.page_object_model.component import Page, Component


class HomePage(Page):
    query: Annotated[input_value, CSS("input[name='q']")]


class SearchResultPage(Page):
    class Result(Component):
        name: Annotated[str, CSS("h3 span.package-snippet__name")]
        version: Annotated[str, CSS("h3 span.package-snippet__version")]
        link: Annotated[href, CSS("a.package-snippet")]
        description: Annotated[str, CSS("p.package-snippet__description")]
        release_datetime: A[
            datetime,
            DatetimeFormat("%Y-%m-%dT%H:%M:%S%z"),
            Attribute("datetime"),
            CSS("span.package-snippet__created time"),
        ]

    nb_results: Annotated[
        int,
        XPath("//*[@id='content']//form/div[1]/div[1]/p/strong"),
    ]
    results: Annotated[
        list[Result],
        CSS("ul[aria-label='Search results'] li"),
    ]
```

The `Page` class encapsulates the whole current HTML page available through the driver. Each DOM
value we want to extract is then represented by a class attribute, with a type (what to extract)
and a selector (where to extract it). Depending on the type of the value, Manen will automatically
execute the appropriate DOM content extraction on the HTML element (for example, it will extract
the inner text for a `str` type, the HTML attribute `href` for a `HRef` , or the property
`innerHTML` for `InnerHTML`).

A `Component` captures a sub-part of an HTML page. All the elements defined under this will be
fetched inside the HTML element represented by the `Component` class.

Here the class `HomePage` defines an `Input` element, that will be linked to the search bar.
Filling the search bar is done by assigning a value to the attribute `query`.

```python
from selenium.webdriver.common.keys import Keys

page = HomePage(browser) # A Page object is initialized only with a WebDriver instance

page.query = "manen"
page.query += Keys.ENTER
```

After submitting the form, we are redirected to the search results page.

![PyPI home page](https://raw.githubusercontent.com/kodaho/manen/main/docs/assets/screenshot_pypi_search_results.png)

The `SearchResultPage` will then be used to extract the results.

```python
page = SearchResultPage(browser)

print(page.nb_results)
# 3

print(page.results[0])
# <__main__.SearchResultPage.Result at 0x1058e97c0>
```

Manen provides a `model_dump` method, quite similar to the one in Pydantic to easily get all the
attributes of a component or a page.

```python
print(page.results[0].model_dump())
# {'name': 'manen',
#  'version': '0.2.0',
#  'link': 'https://pypi.org/project/manen/',
#  'description': 'A package around Selenium with an implementation of the page object model, an enhanced WebDriver and a CLI.',
#  'release_datetime': datetime.datetime(2022, 2, 19, 12, 10, 31, tzinfo=datetime.timezone.utc)}
```

> [!TIP]
> Other DOM elements are also implemented, such as `ImageSrc`, `Input`, `Checkbox`... Each one of
> them is used to target a specific attribute from a DOM value and can enable interaction with it,
> in a flawless Pythonic way. Check the [documentation](https://kodaho.github.io/manen/user_guide/page_object_model.html#List-of-available-elements)
> for the list of available elements.

Let's finally close the Selenium WebDriver to avoid any remaining running applications once we
exit the Python program.

```python
browser.quit()
```

## 🦾 Going further

[The documentation](https://kodaho.github.io/manen/) provides an extensive overview of the
possibilities offered by the package. It also contains several user guides to help you get
started with the package.

A [set of examples](https://github.com/kodaho/manen/tree/main/examples) is also available in the
`examples/` directory of the source code repository. They are designed to show you how to use the
package in a real-world context.

Don't hesitate to open an issue if you have any question or concern about this project!

Looking to contribute to fix or add new features? Just read
[this page](https://kodaho.github.io/manen/contributing.html),
fork the repository and start doing the modifications you want.
