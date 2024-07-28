"""
Classes which inherits from :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`, and add
useful methods for driver interactions.
"""

import time
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from manen.finder import find
from manen.helpers import PLATFORM, version
from manen.typing import WebDriverProtocol

if TYPE_CHECKING:
    from .typing import DriverOrElement, Version, WebElement


__all__ = ("ChromeBrowser",)


class ScrollDirection(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class HeadlessMode(str, Enum):
    NEW = "new"
    OLD = "old"


class BrowserMixin(WebDriverProtocol):
    """
    Mixin to enhance :py:class:`~selenium.webdriver.remote.webdriver.WebDriver` with a set of
    features intended to ease the way to work with a WebDriver instance.
    """

    @property
    def cookies(self):
        """Cookies associated to the current domain"""
        return self.get_cookies()

    @cookies.setter
    def cookies(self, cookies: list[dict[str, Any]]):
        """
        Inject some cookies in the current driver.

        Args:
            cookies (list[dict[str, Any]): cookies as a list of dictionaries
        """
        for cookie in cookies:
            self.add_cookie(cookie)

    @cookies.deleter
    def cookies(self):
        """Delete current cookies inside the driver."""
        self.delete_all_cookies()

    def click_with_js(self, element: "WebElement"):
        """
        Click on an element using JavaScript (useful to click on an element outside the current
        frame).
        """
        js_script = """arguments[0].click()"""
        return self.execute_script(js_script, element)

    def scroll(
        self,
        n: int = 1,
        wait: int = 0,
        direction: ScrollDirection = ScrollDirection.DOWN,
        with_js: bool = False,
    ):
        """Scroll the page, in a given direction.

        Args:
            n (int, optional): Number of scroll to perform. Defaults to 1.
            wait (int, optional): Number of seconds to wait between each scroll. Defaults to 0.
            direction (str, optional): scroll up or down (can only be ``UP`` or ``DOWN``).
                Defaults to ``DOWN``.
            with_js (bool, optional): perform the action with a JavaScript script instead of
                scrolling by pressing the keys down or up. Defaults to False.

        Raises:
            ValueError: Raised if `direction` is not `UP` or `DOWN`
        """
        if direction not in list(ScrollDirection):
            raise ValueError(
                f"`{direction}` is not supported as a scroll direction. "
                "Please choose between `UP` and `DOWN`."
            )

        if with_js:
            func = self.execute_script
            arg = "window.scrollBy({top: %s1000, left: 0, behavior: 'smooth'});" % (
                "-" if direction == ScrollDirection.UP else "+"
            )
        else:
            body: "DriverOrElement" = self.find_element(By.TAG_NAME, "body")
            arg = Keys.PAGE_DOWN if direction == ScrollDirection.DOWN else Keys.PAGE_UP
            func = body.send_keys

        for _ in range(n):
            func(arg)
            time.sleep(wait)

    def highlight(self, selector: str | list[str], **kwargs):
        """
        Highlight an element in the current page by drawing a black frame around it.

        Args:
            selector (str | list[str]): selector(s) used to find the element.
            **kwargs: Keyword arguments sent to ``find`` method
        """
        elements = self.find(selector, **kwargs)
        if not isinstance(elements, list):
            elements = [elements]
        script = "\n".join(
            [
                f"arguments[{i}].style.border = '3px solid black';"
                for i in range(len(elements))
            ]
        )
        self.execute_script(script, *elements)

    @property
    def current_platform(self):
        """Current platform of the webdriver"""
        return PLATFORM

    @property
    def browser_version(self) -> "Version":
        """Version of the browser"""
        return version(self.capabilities["browserVersion"])

    @property
    def driver_version(self) -> "Version":
        """Version of the driver"""
        return version(self.capabilities["chrome"]["chromedriverVersion"].split(" ")[0])

    @property
    def is_browser_compatible_with_driver(self):
        """Is the browser version compatible with the driver version?"""
        return self.browser_version[:3] == self.driver_version[:3]

    def find(self, selector: str | list[str], **kwargs):
        """
        Find elements matching selectors using :py:func:`~manen.finder.find`, with the driver
        instance as scope for the search. Returns all elements by default.

        Args:
            selector (str | list[str]): selector(s) passed to :py:func:`~manen.finder.find`
            **kwargs: keyword arguments sent to :py:func:`~manen.finder.find`

        Raises:
            ElementNotFound: Raised if no default value is specified and no element matching the
                selector(s) has been found.

        Returns:
            Any: Outputs of :py:func:`~manen.finder.find`
        """
        kwargs.setdefault("inside", self)
        kwargs.setdefault("many", True)
        return find(selector, **kwargs)

    def lookup(self, *args, **kwargs) -> Any:
        """
        Same as the method :py:meth:`~.BrowserMixin.find` with the difference that this
        method never raises error. If the element is not found, it returns a default value
        (``None`` by default).

        Args:
            *args: positional arguments passed to :py:func:`~manen.finder.find`
            *kwargs: keyword arguments passed to :py:func:`~manen.finder.find`

        Returns:
            Any: Outputs of :py:func:`~manen.finder.find`
        """
        return find(inside=cast("DriverOrElement", self), default=None)(*args, **kwargs)


class ChromeBrowser(BrowserMixin, Chrome):
    """Wrapper around Selenium ChromeWebDriver providing methods to improve its operability."""

    @classmethod
    def initialize(
        cls,
        options: ChromeOptions | None = None,
        service: ChromeService | None = None,
        driver_path: str | None = None,
        headless_mode: HeadlessMode | None = None,
        proxy: str | None = None,
        window_size: tuple[int, int] | None = None,
    ):
        """
        Launch an enhanced web driver for the browser Chrome.

        Args:
            options (ChromeOptions, optional): Options to configure the driver. Defaults to None.
            service (ChromeService, optional): Service to configure the driver. Defaults to None.

        Returns:
            WebDriver: An enhanced Chrome driver
        """
        if driver_path and service:
            raise ValueError(
                "You cannot specify both `driver_path` and `service`. "
                "Set `driver_path` in the Service with `Service(executable_path=driver_path)`."
            )

        options = options or ChromeOptions()
        service = service or ChromeService()

        if driver_path:
            service = ChromeService(executable_path=driver_path)

        if headless_mode:
            options.add_argument(f"--headless={headless_mode}")

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        if window_size:
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

        return cls(options=options, service=service)
