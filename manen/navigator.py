import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

from .finder import find
from .helpers import PLATFORM
from .resource import ChromeDriverResource, Version

__all__ = ("ChromeNavigator",)


class NavigatorMixin:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()

    @property
    def cookies(self):
        return self.get_cookies()

    @cookies.setter
    def cookies(self, cookies):
        for cookie in cookies:
            cookie_copy = cookie.copy()
            cookie_copy.pop("expiry", None)
            self.add_cookie(cookie_copy)

    @cookies.deleter
    def cookies(self):
        self.delete_all_cookies()

    def click_with_js(self, element):
        js_script = """arguments[0].click()"""
        self.execute_script(js_script, element)
        return

    def scroll(self, n=3, wait=1, direction="down", with_js=False):
        if with_js:
            func = self.execute_script
            arg = "window.scrollBy({top: %s1000, left: 0, behavior: 'smooth'});" % (
                "-" if direction == "up" else ""
            )
        else:
            body = self.find_element_by_tag_name("body")
            arg = Keys.PAGE_DOWN if direction == "down" else Keys.PAGE_UP
            func = body.send_keys

        for _ in range(n):
            func(arg)
            time.sleep(wait)

        return

    def highlight(self, selector, **kwargs):
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
    def browser_version(self):
        return Version(self.capabilities["browserVersion"])

    @property
    def driver_version(self):
        return Version(self.capabilities["chrome"]["chromedriverVersion"].split(" ")[0])

    @property
    def are_versions_compatible(self):
        return self.browser_version[:3] == self.driver_version[:3]

    def find(self, selector, **kwargs):
        kwargs.setdefault("inside", self)
        return find(selector, **kwargs)

    def lookup(self, *args, **kwargs):
        return find(inside=self, many=False)(*args, **kwargs)


class ChromeNavigator(NavigatorMixin, Chrome):
    @classmethod
    def initialize(  # pylint: disable=bad-continuation
        cls, proxy=None, headless=False, driver_path=None, window_size=None,
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
