# pylint: disable-all
"""
manen.typing
============

Describe some common types used by :py:mod:`manen`.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from typing import Any, Dict, Optional, Tuple, TypedDict, Union

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement
    from typing_extensions import Protocol

    SeleniumElement = Union[WebDriver, WebElement]
    Version = Tuple[int, int, Optional[int], int]

    class CookieProtocol(Protocol):
        def get_cookies(self):
            ...

        def add_cookie(self, cookie):
            ...

        def delete_all_cookies(self):
            ...

    class ScriptExecutionProtocol(Protocol):
        def execute_script(self, script: str, *args):
            ...

    class ElementFinderProtocol(Protocol):
        def find_element_by_tag_name(self, tag_name: str) -> WebElement:
            ...

    class CapabilitiesProtocol(Protocol):
        @property
        def capabilities(self) -> Dict[str, Any]:
            ...

    class WebDriverProtocol(
        CookieProtocol,
        CapabilitiesProtocol,
        ElementFinderProtocol,
        ScriptExecutionProtocol,
        Protocol,
    ):
        """Minimal typing protocol used by
        :py:class:`~manen.browser.BrowserMixin`.
        """

    class InstalledVersionInfo(TypedDict):
        channel: str
        os: str
        release_date: date
        version: Version

else:

    class WebDriverProtocol:
        pass
