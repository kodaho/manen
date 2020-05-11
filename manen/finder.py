"""Find inside a Selenium element some DOM elements based on selectors."""

from functools import partial
from typing import Any, List, Tuple, Union

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
    """Parse a selector string ({selection_method}:{selector}). If no selection
    method is specified, infer it from the selector (XPath or CSS).

    Args:
        selector (str): [description]

    Returns:
        Tuple[str, str]: [description]
    """
    if any(selector.startswith(f"{method}:") for method in METHODS_MAPPER):
        selection_method, sel = selector.split(":", 1)
        return METHODS_MAPPER[selection_method], sel
    if selector.startswith("/") or selector.startswith("./"):
        return By.XPATH, selector
    return By.CSS_SELECTOR, selector


def find(  # pylint: disable=bad-continuation
    selector: Union[str, List[str]] = None,
    *,
    wait: int = 0,
    default: Any = NotImplemented,
    inside: Union[WebDriver, WebElement] = None,
    many: bool = False,
):
    """Retrieve DOM elements from Selenium WebElements. Highly customizable.

    Available selection methods:

    +--------------------------+-------------------------------------------------------------+
    | Selection Method         | Selection Engine                                            |
    +==========================+=============================================================+
    | xpath, xp                | XPath (can be inferred if no selection method is specified) |
    +--------------------------+-------------------------------------------------------------+
    | css                      | CSS                                                         |
    +--------------------------+-------------------------------------------------------------+
    | class_name, class, cls   | Class Name (but Selenium is the CSS method behind)          |
    +--------------------------+-------------------------------------------------------------+
    | id                       | ID (but Selenium is the CSS method behind)                  |
    +--------------------------+-------------------------------------------------------------+
    | link_text, link          | Link Text                                                   |
    +--------------------------+-------------------------------------------------------------+
    | name                     | Name attribute                                              |
    +--------------------------+-------------------------------------------------------------+
    | tag_name, tag            | Tag Name                                                    |
    +--------------------------+-------------------------------------------------------------+
    | partial_link_text, plink | Partial Link Text                                           |
    +--------------------------+-------------------------------------------------------------+

    Args:
        selector (str or List[str], optional): [description]. Defaults to None.
        wait (int, optional): [description]. Defaults to 0.
        default (Any, optional): [description]. Defaults to NotImplemented.
        inside (Union[WebDriver, WebElement], optional): [description]. Defaults to None.
        many (bool, optional): [description]. Defaults to False.

    Raises:
        ValueError: [description]
        ElementNotFound: [description]

    Returns:
        [type]: [description]
    """
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

    for sel in selectors:
        selenium_selector = _parse_selector(sel)
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
