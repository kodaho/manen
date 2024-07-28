from typing import cast

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model import element
from manen.page_object_model.dom import Config


class WebArea:
    def __init__(self, /, scope: WebDriver | WebElement):
        self._scope = scope
        self._driver = scope.parent if isinstance(scope, WebElement) else scope
        self._config: dict[str, Config] = {}

        for field in self.__annotations__:
            config = Config.from_annotation_item(field, self.__annotations__[field])
            self._config[field] = config

            if self.is_web_area(config.element_type):
                fn = element.Regions if config.many else element.Region
            elif config.is_input:
                fn = element.InputElement
            else:
                fn = element.Elements if config.many else element.Element
            setattr(
                self.__class__,
                field,
                fn(config),
            )

    @staticmethod
    def is_web_area(element_type):
        return type(element_type) is type and issubclass(element_type, WebArea)

    def model_dump(self):
        dump = {}
        for field, config in self._config.items():
            item = getattr(self, field)
            if self.is_web_area(config.element_type) and config.many:
                dump[field] = [el.model_dump() for el in cast(list[WebArea], item)]
            elif self.is_web_area(config.element_type) and not config.many:
                dump[field] = cast(WebArea, item).model_dump()
            else:
                dump[field] = item
        return dump


class Form(WebArea):
    def submit(self):
        assert isinstance(self._scope, WebElement)
        self._scope.submit()

    @staticmethod
    def is_form(element_type):
        return type(element_type) is type and issubclass(element_type, Form)


class Page(WebArea):
    @property
    def title(self) -> str:
        """Title of the page."""
        return self._driver.title

    @property
    def source_code(self) -> str:
        """Source code of the page."""
        return self._driver.page_source
