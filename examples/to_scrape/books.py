from typing import Annotated

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.selenium_manager import SeleniumManager
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model.component import Component, Page
from manen.page_object_model.config import CSS, Attribute
from manen.page_object_model.types import href, src


class BooksToScrapePage(Page):
    class Category(Component):
        name: Annotated[str, CSS("a")]
        link: Annotated[href, CSS("a")]
        element: Annotated[WebElement, CSS("a")]

    class Information(Component):
        total: Annotated[int, CSS("strong:nth-of-type(1)")]
        showing_from: Annotated[int, CSS("strong:nth-of-type(2)")]
        showing_to: Annotated[int, CSS("strong:nth-of-type(3)")]

    class Book(Component):
        title: Annotated[str, Attribute("title"), CSS("h3 a")]
        image: Annotated[src, CSS("img.thumbnail")]
        price: Annotated[str, CSS("p.price_color")]
        in_stock: Annotated[str, CSS("p.instock.availability")]

    class Pagination(Component):
        previous_url: Annotated[href | None, CSS("li.previous a")]
        next_url: Annotated[href | None, CSS("li.next a")]

    categories: Annotated[list[Category], CSS("ul.nav-list li ul li")]
    current_category: Annotated[str, CSS("h1")]
    information: Annotated[Information, CSS(".form-horizontal")]
    books: Annotated[list[Book], CSS("article.product_pod")]
    pagination: Annotated[Pagination, CSS("ul.pager")]

    def go_to_category(self, category: str):
        for category_component in self.categories:
            if category_component.name == category:
                category_component.element.click()
                return
        raise ValueError(f"Category {category} not found")


if __name__ == "__main__":
    manager = SeleniumManager()
    paths = manager.binary_paths(["--browser", "chrome"])

    options = Options()
    options.binary_location = paths["browser_path"]
    options.add_argument("--disable-search-engine-choice-screen")

    service = Service(executable_path=paths["driver_path"])

    driver = WebDriver(options=options, service=service)

    driver.get("https://books.toscrape.com/catalogue/category/books_1/index.html")

    page = BooksToScrapePage(driver)
