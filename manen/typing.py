"""Describe some common types used by :py:mod:`manen`."""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    SeleniumElement = Union[WebDriver, WebElement]
