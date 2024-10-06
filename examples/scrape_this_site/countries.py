from typing import Annotated

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.selenium_manager import SeleniumManager

from manen.page_object_model.component import Component, Page
from manen.page_object_model.config import CSS
from manen.page_object_model.types import href


class ScrapeThisSiteCountriesPage(Page):
    class CountryInfo(Component):
        name: Annotated[str, CSS("h3")]
        capital: Annotated[str, CSS("span.country-capital")]
        population: Annotated[int, CSS("span.country-population")]
        area: Annotated[float, CSS("span.country-area")]

    source: Annotated[href, CSS("a.data-attribution")]
    nb_countries_label: Annotated[str, CSS("h1 small")]
    countries: Annotated[list[CountryInfo], CSS("div.country")]

    @property
    def nb_countries(self):
        return int(self.nb_countries_label.split()[0])


if __name__ == "__main__":
    manager = SeleniumManager()
    paths = manager.binary_paths(["--browser", "chrome"])

    options = Options()
    options.binary_location = paths["browser_path"]
    options.add_argument("--disable-search-engine-choice-screen")

    service = Service(executable_path=paths["driver_path"])

    driver = WebDriver(options=options, service=service)

    driver.get("https://www.scrapethissite.com/pages/simple/")

    page = ScrapeThisSiteCountriesPage(driver)

    assert page.nb_countries == len(page.countries)
