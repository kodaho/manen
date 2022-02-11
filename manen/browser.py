"""
manen.browser
===============

Classes which enrich :py:class:`selenium.webdriver.remote.webdriver.WebDriver`.
"""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

from .finder import find
from .helpers import PLATFORM, version
from .resource.brave import application as brave_app
from .resource.chrome import application as chrome_app
from .resource.chrome import driver as chromedriver
from .typing import WebDriverProtocol

if TYPE_CHECKING:
    from .typing import SeleniumElement, Version


__all__ = (
    "BraveBrowser",
    "ChromeBrowser",
)


class BrowserMixin(WebDriverProtocol):  # type: ignore
    """Mixin to enrich :py:class:`selenium.webdriver.remote.webdriver.WebDriver`
    with a set of features intended to ease the way to work with such an
    instance.
    """

    @property
    def cookies(self):
        """Cookies associated to the current domain."""
        return self.get_cookies()

    @cookies.setter
    def cookies(self, cookies: List[Dict["str", Any]]):
        """Install some cookies in the current driver, just by assigning the
        list in the right format.

        Args:
            cookies (List[Dict["str", Any]): cookies as a list of dictionaries
        """
        for cookie in cookies:
            self.add_cookie(cookie)

    @cookies.deleter
    def cookies(self):
        """Easily delete current cookies inside the driver."""
        self.delete_all_cookies()

    def click_with_js(self, element: "SeleniumElement"):
        """Click on an element using a JavaScript script. Can be useful if you
        want to click on an element outside the current frame.
        """
        js_script = """arguments[0].click()"""
        return self.execute_script(js_script, element)

    def scroll(
        self,
        n_repeat: int = 3,
        wait: int = 1,
        direction: str = "DOWN",
        with_js: bool = False,
    ):
        """Perform a scroll action on the page.

        Args:
            n_repeat (int, optional): Number of scroll to perform.
                Defaults to 3.
            wait (int, optional): Number of seconds to wait between each
                scroll. Defaults to 1.
            direction (str, optional): scroll up or down (can only be ``UP`` or
                ``DOWN``, case insensitive). Defaults to "DOWN".
            with_js (bool, optional): perform the action with a JavaScript
                script instead of scrolling by pressing the Key DOWN or UP.
                Defaults to False.

        Raises:
            ValueError: Raised if `direction` (once lowercased) is not
                `UP` or `DOWN`
        """
        if direction.lower() not in ("down", "up"):
            raise ValueError(
                f"`{direction}` is not supported as a scroll direction. "
                "Please choose between `UP` and `DOWN` (case insensitive)."
            )

        if with_js:
            func = self.execute_script
            arg = "window.scrollBy({top: %s1000, left: 0, behavior: 'smooth'});" % (
                "-" if direction.lower() == "up" else ""
            )
        else:
            body: "SeleniumElement" = self.find_element_by_tag_name("body")
            arg = Keys.PAGE_DOWN if direction.lower() == "down" else Keys.PAGE_UP
            func = body.send_keys

        for _ in range(n_repeat):
            func(arg)
            time.sleep(wait)

    def highlight(self, selector: Union[str, List[str]], **kwargs):
        """Highlight an element in the current webpage by drawing a black frame
        around this element. The element will be retrieved using the ``find``
        method and then framed by updating the CSS properties of the retrieved
        element.

        Args:
            selector (Union[str, List[str]]): selector(s) used to find the element.
            **kwargs: Keyword arguments sent to ``find`` method

        Returns:
            Any: Value returned by the JS script updating the CSS properties
        """
        elements = self.find(selector, **kwargs)
        if not isinstance(elements, list):
            elements = [elements]
        highlight_script = "arguments[%d].style.border = '3px solid black';"
        script = "".join([highlight_script % i for i in range(len(elements))])
        return self.execute_script(script, *elements)

    @property
    def current_platform(self):
        """Platform (OS information) on which the driver runs."""
        return PLATFORM

    @property
    def browser_version(self) -> "Version":
        """Version of the browser in used."""
        return version(self.capabilities["browserVersion"])

    @property
    def driver_version(self) -> "Version":
        """Version of the driver in used."""
        return version(self.capabilities["chrome"]["chromedriverVersion"].split(" ")[0])

    @property
    def are_versions_compatible(self):
        """Property telling you if the version of the used driver is compatible
        with the one of the browser.
        """
        return self.browser_version[:3] == self.driver_version[:3]

    def find(self, selector: Union[str, List[str]], **kwargs):
        """This method is basically the same as :py:func:`~manen.finder.find`
        but with the driver instance as default value for the argument
        ``inside`` and True as default value for ``many`` argument.
        See the documentation of :py:func:`~manen.finder.find` for more
        information of what we can do with this method.

        Args:
            selector (Union[str, List[str]]): selector(s) passed to
                :py:func:`~manen.finder.find`
            **kwargs: keyword arguments sent to :py:func:`~manen.finder.find`

        Raises:
            ElementNotFound: Raised if no default value is specified and no
                element matching the selector(s) has been found.

        Returns:
            Any: Outputs of :py:func:`~manen.finder.find`
        """
        kwargs.setdefault("inside", self)
        kwargs.setdefault("many", True)
        return find(selector, **kwargs)

    def lookup(self, *args, **kwargs) -> Any:
        """This method is exactly as the method ``find`` but it will always
        return a default value if an element cannot be found (this defaul
        value is by default `None`.
        To keep it simple, this is the ``find`` method which never raises
        an exception if a selection method returns nothing!

        Args:
            *args: postional arguments sent directly as arguments of the method
                ``find``
            **kwargs: keyword arguments sent directly as arguments of the method
                ``find``

        Returns:
            Any: Outputs of :py:func:`~manen.finder.find`
        """
        return find(inside=self, default=None)(*args, **kwargs)  # type: ignore


class ChromeBrowser(BrowserMixin, Chrome):
    """Wrapper around Selenium ChromeWebDriver providing additional methods in
    order to give more abilities and flexibilities when controlling the browser.
    For example, it defines a method ``find`` to easily retrieve elements,
    ``highlight`` to put an emphasis on elements or cookies property. Go check
    the documentation of methods inherited from
    :py:class:`~manen.browser.BrowserMixin` for further information.
    """

    BINARIES = chrome_app.BINARIES

    @classmethod
    def initialize(
        cls,
        proxy: Optional[str] = None,
        headless: bool = False,
        driver_path: Optional[str] = None,
        window_size: Optional[Tuple[int, int]] = None,
    ):
        """Class method to easily launch an enhanced new driver based on the
        browser Chrome. Here you can specify directly if the browser should run
        headless or not, if a proxy should be used and many more options.

        Args:
            proxy (str, optional): proxy to use. Defaults to ``None``.
            headless (bool, optional): whether the browser should be launched
                headless. Defaults to ``False``.
            driver_path (str, optional): path of the driver program to use. If
                `None`, `manen` will use functions defined in the package
                :py:mod:`~manen.resources` to find one (and download one if
                needed). Defaults to ``None``.
            window_size (Tuple[int, int], optional): size of the browser window
                to be launched. Defaults to ``None``.

        Returns:
            WebDriver: An enhanced Chrome driver
        """
        driver_path = driver_path or chromedriver.get()

        chrome_options = ChromeOptions()
        chrome_options.binary_location = cls.BINARIES[PLATFORM.system]
        if window_size:
            chrome_options.add_argument("--window-size=%s,%s" % window_size)

        if headless:
            chrome_options.add_argument("--headless")

        if proxy:
            chrome_options.add_argument("--proxy-server=%s" % proxy)

        return cls(driver_path, options=chrome_options)


class BraveBrowser(ChromeBrowser):
    """Enhanced ChromeWebDriver that will launch a Brave browser instead of
    Google Chrome.
    """

    BINARIES = brave_app.BINARIES
