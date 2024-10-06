from typing import Annotated

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.selenium_manager import SeleniumManager

from manen.page_object_model.component import Component, Page
from manen.page_object_model.config import CSS, Default
from manen.page_object_model.types import href


class QuotesToScrapePage(Page):
    class Quote(Component):
        text: Annotated[str, CSS("span.text")]
        author: Annotated[str, CSS("small.author")]
        tags: Annotated[list[str], CSS("div.tags a.tag")]

    class Pagination(Component):
        previous_url: Annotated[href, CSS("li.previous a"), Default(None)]
        next_url: Annotated[href, CSS("li.next a"), Default(None)]

    quotes: Annotated[list[Quote], CSS("div.quote")]
    pagination: Annotated[Pagination, CSS("ul.pager")]


if __name__ == "__main__":
    manager = SeleniumManager()
    paths = manager.binary_paths(["--browser", "chrome"])

    options = Options()
    options.binary_location = paths["browser_path"]
    options.add_argument("--disable-search-engine-choice-screen")

    service = Service(executable_path=paths["driver_path"])

    driver = WebDriver(options=options, service=service)

    driver.get("https://quotes.toscrape.com/")

    page = QuotesToScrapePage(driver)