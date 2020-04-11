from selenium.webdriver import Chrome, ChromeOptions

from ..asset_manager import ChromeDriverResources
from .mixin import NavigatorMixin


class ChromeNavigator(NavigatorMixin, Chrome):
    @classmethod
    def initialize(
        cls, proxy=None, headless=False, driver_path=None,
    ):
        driver_path = driver_path or ChromeDriverResources.find()

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--window-size=1920,1080")

        if headless:
            chrome_options.add_argument("--headless")

        if proxy:
            chrome_options.add_argument("--proxy-server=%s" % proxy)

        return cls(driver_path, chrome_options=chrome_options)
