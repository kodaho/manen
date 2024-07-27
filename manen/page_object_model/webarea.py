from typing import cast

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model.dom import Config
from manen.page_object_model.element import Element, Elements, Region, Regions


class WebArea:
    def __init__(self, /, parent: WebDriver | WebElement):
        self._parent = parent
        self._driver = parent.parent if isinstance(parent, WebElement) else parent
        self._config: dict[str, Config] = {}

        for field in self.__annotations__:
            config = Config.from_annotation_item(field, self.__annotations__[field])
            self._config[field] = config

            if self.is_web_area(config.element_type):
                fn = Regions if config.many else Region
            else:
                fn = Elements if config.many else Element
            setattr(
                self.__class__,
                field,
                fn(config),
            )

    @classmethod
    def is_web_area(cls, element_type):
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


class Page(WebArea):
    @property
    def title(self) -> str:
        """Title of the page."""
        return self._driver.title

    @property
    def source_code(self) -> str:
        """Source code of the page."""
        return self._driver.page_source
