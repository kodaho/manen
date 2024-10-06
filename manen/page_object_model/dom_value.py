from datetime import date, datetime
from typing import TYPE_CHECKING, Callable, TypeVar, cast

from selenium.webdriver.remote.webelement import WebElement

from manen.finder import find
from manen.page_object_model.config import Config

if TYPE_CHECKING:
    from manen.page_object_model.component import Component

T = TypeVar("T")
TTransformers = dict[type[T], Callable[[str, Config], T]]


def parse_datetime(value: str, cfg: Config) -> datetime:
    if not cfg.format:
        raise ValueError(f"A {cfg.element_type.__name__} format is required")
    return datetime.strptime(value, cfg.format)


GET_TRANSFORMERS: TTransformers = {
    date: lambda value, cfg: parse_datetime(value, cfg).date(),
    datetime: parse_datetime,
    float: lambda value, cfg: float(value),
    int: lambda value, cfg: int(value),
    str: lambda value, cfg: value,
}


class ConfigurableDOM:
    def __init__(self, config: Config):
        self.config = config


class ImmutableDOMValueMixin:
    def __set__(self, component: "Component", value):
        raise Exception("Cannot set component")

    def __delete__(self, component: "Component"):
        raise Exception("Cannot delete component")


class DOMValue(ImmutableDOMValueMixin, ConfigurableDOM):
    def __get__(self, component: "Component", component_class: type["Component"]):
        element = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        if element == self.config.default:
            return element
        if self.config.element_type == WebElement:
            return element
        value = (
            element.get_attribute(self.config.attribute)
            if self.config.attribute
            else element.text
        )
        return GET_TRANSFORMERS[self.config.element_type](value or "", self.config)


class DOMValues(ImmutableDOMValueMixin, ConfigurableDOM):
    def __get__(self, component: "Component", component_class: type["Component"]):
        elements = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=True,
            default=self.config.default,
            wait=self.config.wait,
        )
        if elements == self.config.default:
            return elements
        if self.config.element_type == WebElement:
            return elements
        values = [
            (
                element.get_attribute(self.config.attribute)
                if self.config.attribute
                else element.text
            )
            for element in elements
        ]
        return [
            GET_TRANSFORMERS[self.config.element_type](value or "", self.config)
            for value in values
        ]


class InputDOMValue:
    def __init__(self, config: Config):
        if config.many:
            raise ValueError("Cannot use InputElement with many=True")
        self.config = config

    def __get__(self, component: "Component", component_class: type["Component"]):
        element = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        return element.get_attribute("value")

    def __set__(self, component: "Component", value):
        element = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        element.clear()
        element.send_keys(value)


class CheckboxDOMValue:
    def __init__(self, config: Config):
        self.config = config

    def __get__(self, component: "Component", component_class: type["Component"]):
        element = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        return element.get_attribute("checked") == "true"

    def __set__(self, component: "Component", value: bool):
        element = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        if value != (element.get_attribute("checked") == "true"):
            element.click()


class DOMSection(ImmutableDOMValueMixin, ConfigurableDOM):
    def __get__(
        self,
        component: "Component",
        component_class: type["Component"],
    ) -> "Component":
        element = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        cls = type(
            self.config.element_type.__qualname__,
            self.config.element_type.__bases__,
            {**self.config.element_type.__dict__},
        )
        return cast("Component", cls(element))


class DOMSections(ImmutableDOMValueMixin, ConfigurableDOM):
    def __get__(self, component: "Component", component_class: type["Component"]):
        elements = find(
            selector=self.config.selectors,
            inside=component._scope,
            many=True,
            default=self.config.default,
            wait=self.config.wait,
        )
        cls = type(
            self.config.element_type.__qualname__,
            self.config.element_type.__bases__,
            {**self.config.element_type.__dict__},
        )
        return [cls(element) for element in elements]
