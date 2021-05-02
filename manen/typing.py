"""
manen.typing
============

Describe some common types used by :py:mod:`manen`.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Tuple, Union
    from typing_extensions import Protocol

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    SeleniumElement = Union[WebDriver, WebElement]
    Version = Tuple[int, int, int, int]

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
        def capabilities(self):
            ...

    class WebDriverProtocol(
        CookieProtocol,
        CapabilitiesProtocol,
        ElementFinderProtocol,
        ScriptExecutionProtocol,
        Protocol,
    ):
        """Minimal protocol used by :py:class:`~manen.navigator.NavigatorMixin`"""
