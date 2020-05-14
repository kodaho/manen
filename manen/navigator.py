"""Classes which enrich :py:class:`selenium.webdriver.remote.webdriver.WebDriver`."""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

from .finder import find
from .helpers import PLATFORM
from .resource import ChromeDriverResource, Version

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement
    from .helpers import Platform

    SeleniumElement = Union["WebDriver", "WebElement"]

__all__ = ("ChromeNavigator",)


class NavigatorMixin:
    """Mixin to enrich :py:class:`selenium.webdriver.remote.webdriver.WebDriver`
    with a set of features intended to ease the way to work with such an instance.
    """

    @property
    def cookies(self: "WebDriver"):
        """Cookies associated to the current domain."""
        return self.get_cookies()

    @cookies.setter
    def cookies(self: "WebDriver", cookies: List[Dict["str", Any]]):
        for cookie in cookies:
            cookie_copy = cookie.copy()
            cookie_copy.pop("expiry", None)
            self.add_cookie(cookie_copy)

    @cookies.deleter
    def cookies(self: "WebDriver"):
        self.delete_all_cookies()

    def click_with_js(self: "WebDriver", element: "SeleniumElement"):
        """Click on an element using a JavaScript script."""
        js_script = """arguments[0].click()"""
        self.execute_script(js_script, element)
        return

    def scroll(  # pylint: disable=bad-continuation
        self: "WebDriver",
        n_repeat: int = 3,
        wait: int = 1,
        direction: str = "down",
        with_js: bool = False,
    ):
        if with_js:
            func = self.execute_script
            arg = "window.scrollBy({top: %s1000, left: 0, behavior: 'smooth'});" % (
                "-" if direction == "up" else ""
            )
        else:
            body = self.find_element_by_tag_name("body")
            arg = Keys.PAGE_DOWN if direction == "down" else Keys.PAGE_UP
            func = body.send_keys

        for _ in range(n_repeat):
            func(arg)
            time.sleep(wait)

        return

    def highlight(self: "WebDriver", selector: Union[str, List[str]], **kwargs):
        elements = self.find(selector, **kwargs)
        if not isinstance(elements, list):
            elements = [elements]
        highlight_script = "arguments[%d].style.border = '3px solid black';"
        script = "".join([highlight_script % i for i in range(len(elements))])
        return self.execute_script(script, *elements)

    @property
    def current_platform(self):
        return PLATFORM

    @property
    def browser_version(self: "WebDriver"):
        return Version(self.capabilities["browserVersion"])

    @property
    def driver_version(self: "WebDriver"):
        return Version(self.capabilities["chrome"]["chromedriverVersion"].split(" ")[0])

    @property
    def are_versions_compatible(self: "WebDriver"):
        return self.browser_version[:3] == self.driver_version[:3]

    def find(self: "WebDriver", selector: Union[str, List[str]], **kwargs):
        kwargs.setdefault("inside", self)
        return find(selector, **kwargs)

    def lookup(self: "WebDriver", *args, **kwargs):
        return find(inside=self, many=False)(*args, **kwargs)


class ChromeNavigator(NavigatorMixin, Chrome):
    @classmethod
    def initialize(  # pylint: disable=bad-continuation
        cls,
        proxy: Optional[str] = None,
        headless: bool = False,
        driver_path: Optional[str] = None,
        window_size: Optional[Tuple[int, int]] = None,
    ):
        driver_path = driver_path or ChromeDriverResource.find()

        chrome_options = ChromeOptions()
        if window_size:
            chrome_options.add_argument("--window-size=%s,%s" % window_size)

        if headless:
            chrome_options.add_argument("--headless")

        if proxy:
            chrome_options.add_argument("--proxy-server=%s" % proxy)

        return cls(driver_path, chrome_options=chrome_options)
