from functools import partial
from typing import Any, Tuple, Union

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .exceptions import ElementNotFound

METHODS_MAPPER = {
    "class_name": By.CLASS_NAME,
    "class": By.CLASS_NAME,
    "cls": By.CLASS_NAME,
    "css": By.CSS_SELECTOR,
    "id": By.ID,
    "link_text": By.LINK_TEXT,
    "link": By.LINK_TEXT,
    "name": By.NAME,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "plink": By.PARTIAL_LINK_TEXT,
    "tag_name": By.TAG_NAME,
    "tag": By.TAG_NAME,
    "xp": By.XPATH,
    "xpath": By.XPATH,
}


def _parse_selector(selector: str) -> Tuple[str, str]:
    if any(selector.startswith(f"{method}:") for method in METHODS_MAPPER):
        selection_method, sel = selector.split(":", 1)
        return METHODS_MAPPER[selection_method], sel
    if selector.startswith("/") or selector.startswith("./"):
        return By.XPATH, selector
    return By.CSS_SELECTOR, selector


def find(
    selector: str = None,
    *,
    wait: int = 0,
    default: Any = NotImplemented,
    inside: Union[WebDriver, WebElement] = None,
    many: bool = False,
):
    if selector is None:
        return partial(find, wait=wait, default=default, inside=inside, many=many)

    if inside is None:
        raise ValueError("You must specify a value to the parameter `inside`.")

    if isinstance(inside, list):
        return [
            find(selector, inside=element, default=default, wait=wait, many=many)
            for element in inside
        ]

    selectors = [selector] if not isinstance(selector, list) else selector
    driver = inside if isinstance(inside, WebDriver) else inside.parent

    for selector in selectors:
        selenium_selector = _parse_selector(selector)
        if many:
            expected_condition = EC.presence_of_all_elements_located
            finder = inside.find_elements
        else:
            expected_condition = EC.presence_of_element_located
            finder = inside.find_element

        try:
            return (
                WebDriverWait(driver, wait).until(expected_condition(selenium_selector))
                if wait
                else finder(*selenium_selector)
            )
        except (NoSuchElementException, TimeoutException):
            pass

    if default != NotImplemented:
        return default

    raise ElementNotFound(selectors=selectors, inside=inside)
