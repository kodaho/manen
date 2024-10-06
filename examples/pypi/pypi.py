from datetime import datetime
from typing import Annotated as A

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.selenium_manager import SeleniumManager
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model.component import Component, Form, Page
from manen.page_object_model.config import CSS, Attribute, DatetimeFormat, XPath
from manen.page_object_model.types import checkbox, href, input_value


class HomePage(Page):
    class SearchForm(Form):
        query: A[input_value, CSS("input[name='q']")]

    search: A[SearchForm, CSS("form.search-form")]


class SearchResultPage(Page):
    class Result(Component):
        name: A[str, CSS("span.package-snippet__name")]
        version: A[str, CSS("h3 span.package-snippet__version")]
        link: A[href, CSS("a.package-snippet")]
        description: A[str, CSS("p.package-snippet__description")]
        release_datetime: A[
            datetime,
            DatetimeFormat("%Y-%m-%dT%H:%M:%S%z"),
            Attribute("datetime"),
            CSS("span.package-snippet__created time"),
        ]

    nb_results: A[
        int,
        XPath("//*[@id='content']//form/div[1]/div[1]/p/strong"),
    ]
    results: A[
        list[Result],
        CSS("ul[aria-label='Search results'] li"),
        CSS("ul[aria-label='Résultats de recherche'] li"),
    ]


class SearchPage(Page):
    class CheckboxListItem(Component):
        label: A[WebElement, CSS("label")]
        is_checked: A[checkbox, CSS("input")]

    items: A[list[CheckboxListItem], CSS("div.checkbox-tree ul li")]


if __name__ == "__main__":
    manager = SeleniumManager()
    paths = manager.binary_paths(["--browser", "chrome"])

    options = Options()
    options.binary_location = paths["browser_path"]
    options.add_argument("--disable-search-engine-choice-screen")

    service = Service(executable_path=paths["driver_path"])

    driver = WebDriver(options=options, service=service)

    driver.get("https://pypi.org/")

    page = HomePage(driver)
    page.search.query = "manen"
    page.search.query += Keys.RETURN

    page = SearchResultPage(driver)
