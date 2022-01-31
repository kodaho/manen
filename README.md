<p align="center">
  <h1 align="center"> 🌔  manen</h1>
</p>

----

<p align="center">
  <img src="https://img.shields.io/badge/python-%3E=3.6-informational?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/version-0.1.0-informational?style=for-the-badge">
  <img src="https://img.shields.io/badge/status-in%20development-yellow?style=for-the-badge">
</p>

<p align="center">
  <i><b>A package around <a href="https://pypi.org/project/selenium/"><code>selenium</code></a> to easily construct Python objects which reflect the DOM of any webpages.</b></i>
</p>

----

<p align="center">🚧 </p>

## 📥  Installation

```bash
pip install manen
```

## 🚀 Getting started

```python
import manen.page_object_model as pom

class HomePage(pom.Page):
    query = pom.InputElement("input[id='search']")

class SearchResultPage(pom.Page):
    class ResultRegions(pom.Regions):
        name = pom.TextElement("h3 span.package-snippet__name")
        version = pom.TextElement("h3 span.package-snippet__version")
        link = pom.LinkElement("a.package-snippet")
        description = pom.TextElement("p.package-snippet__description")

    n_results = pom.IntegerElement("//*[@id='content']//form/div[1]/div[1]/p/strong")
    results = ResultRegions("ul[aria-label='Search results'] li")
```

## ✨ Features

- `manen.finder.find` allows to easily get element(s) in a HTML page.
  This function support several very different use cases, mainly parametrized
  with the function arguments.
- `manen.resource` is a module to easily interact with all the assets
  needed by `selenium`. It allows for example to download all the drivers required
  to work with Selenium.
- `manen.browser` defined browsers objects, an enhanced Selenium's webdriver
- `manen.page_object_model` is the implementation of page object modelling,
  described in Selenium documentation. Thanks to that, you can describe the
  DOM structure only with Python objects.
- a CLI is shipped with the initial release in order to perform operations such
  as downloading webdriver
