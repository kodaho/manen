from inspect import get_annotations
from typing import cast

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model import dom_value as dom
from manen.page_object_model.config import Config


class Component:
    _config: dict[str, Config] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Inherit configs from parent classes (walk MRO in reverse so the
        # most-specific base wins on conflicts).
        merged: dict[str, Config] = {}
        for base in reversed(cls.__mro__[1:]):
            merged.update(getattr(base, "_config", {}))

        for field, annotation in get_annotations(cls).items():
            config = Config.from_annotation_item(field, annotation)
            merged[field] = config

            if cls.is_component(config.element_type):
                fn = dom.DOMSections if config.many else dom.DOMSection
            elif config.is_input:
                fn = dom.InputDOMValue
            elif config.is_checkbox:
                fn = dom.CheckboxDOMValue
            else:
                fn = dom.DOMValues if config.many else dom.DOMValue

            setattr(cls, field, fn(config))

        cls._config = merged

    def __init__(self, /, scope: WebDriver | WebElement):
        self._scope = scope
        self._driver = scope.parent if isinstance(scope, WebElement) else scope

    @staticmethod
    def is_component(element_type):
        return isinstance(element_type, type) and issubclass(element_type, Component)

    def model_dump(self):
        dump = {}
        for field, config in self._config.items():
            item = getattr(self, field)
            if self.is_component(config.element_type) and config.many:
                dump[field] = [el.model_dump() for el in cast(list[Component], item)]
            elif self.is_component(config.element_type) and not config.many:
                dump[field] = cast(Component, item).model_dump()
            elif config.element_type != WebElement:
                dump[field] = item
        return dump


class Form(Component):
    def submit(self):
        assert isinstance(self._scope, WebElement)
        self._scope.submit()


class Page(Component):
    @property
    def title(self) -> str:
        return self._driver.title

    @property
    def source_code(self) -> str:
        return self._driver.page_source
