from typing import TYPE_CHECKING, Any, Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing_extensions import Protocol

DriverOrElement = Union[WebDriver, WebElement]
Version = tuple[int, int, int | None, int | None]
Cookie = dict[str, Any]


class CookieProtocol(Protocol):
    def get_cookies(self) -> list[Cookie]: ...

    def add_cookie(self, cookie: Cookie): ...

    def delete_all_cookies(self): ...


class ScriptExecutionProtocol(Protocol):
    def execute_script(self, script: str, *args): ...


class ElementFinderProtocol(Protocol):
    def find_element(self, by: str, value: str) -> WebElement: ...


class CapabilitiesProtocol(Protocol):
    @property
    def capabilities(self) -> dict[str, Any]: ...


if TYPE_CHECKING:

    class WebDriverProtocol(
        CookieProtocol,
        CapabilitiesProtocol,
        ElementFinderProtocol,
        ScriptExecutionProtocol,
        Protocol,
    ): ...

else:

    class WebDriverProtocol: ...
