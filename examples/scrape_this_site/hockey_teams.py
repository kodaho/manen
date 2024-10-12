from typing import Annotated
from urllib.parse import parse_qs, urlparse

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.selenium_manager import SeleniumManager

from manen.page_object_model.component import Component, Form, Page
from manen.page_object_model.config import CSS, Default
from manen.page_object_model.types import href, input_value


class ScrapeThisSiteHockeyTeamsPage(Page):
    class SearchForm(Form):
        query: Annotated[input_value, CSS("input#q")]

    class TeamInfo(Component):
        name: Annotated[str, CSS("td.name")]
        year: Annotated[int, CSS("td.year")]
        wins: Annotated[int, CSS("td.wins")]
        losses: Annotated[int, CSS("td.losses")]
        ot_losses: Annotated[str, CSS("td.ot-losses")]
        win_pct: Annotated[float, CSS("td.pct")]
        goals_for: Annotated[int, CSS("td.gf")]
        goals_against: Annotated[int, CSS("td.ga")]
        diff: Annotated[int, CSS("td.diff")]

    class Pagination(Component):
        previous: Annotated[href | None, CSS("a[aria-label='Previous']")]
        available: Annotated[list[href], CSS("a:not([aria-label])")]
        next: Annotated[href | None, CSS("a[aria-label='Next']")]

    source: Annotated[href, CSS("a.data-attribution")]
    nb_results_label: Annotated[str, CSS("h1 small")]
    search_form: Annotated[SearchForm, CSS("form.form-inline")]
    teams: Annotated[list[TeamInfo], CSS("tr.team"), Default([])]
    pagination: Annotated[Pagination, CSS("ul.pagination")]

    @property
    def nb_results(self):
        return int(self.nb_results_label.split()[0])

    @property
    def current_page_num(self):
        query_params = parse_qs(urlparse(self._driver.current_url).query)
        return int(query_params.get("page_num", [1])[0])


if __name__ == "__main__":
    manager = SeleniumManager()
    paths = manager.binary_paths(["--browser", "chrome"])

    options = Options()
    options.binary_location = paths["browser_path"]
    options.add_argument("--disable-search-engine-choice-screen")

    service = Service(executable_path=paths["driver_path"])

    driver = WebDriver(options=options, service=service)

    driver.get("https://www.scrapethissite.com/pages/forms/")

    page = ScrapeThisSiteHockeyTeamsPage(driver)

    page.search_form.query = "New York"
    page.search_form.submit()

    assert page.nb_results == len(page.teams)

    if next_url := page.pagination.next:
        driver.get(next_url)
