from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Callable, TypeVar, cast

import dateparser
from selenium.webdriver.remote.webelement import WebElement

from manen.finder import find
from manen.helpers import extract_integer
from manen.page_object_model import types
from manen.page_object_model.config import Config

if TYPE_CHECKING:
    from manen.page_object_model.component import Component

T = TypeVar("T")
TTransformers = dict[type[T], Callable[[WebElement, Config], T]]


GET_TRANSFORMERS: TTransformers = {
    datetime: lambda elt, cfg: dateparser.parse(elt.text),
    int: lambda elt, cfg: extract_integer(elt.text),
    str: lambda elt, cfg: elt.text,
    types.href: lambda elt, cfg: elt.get_attribute(cfg.attribute),
    types.inner_html: lambda elt, cfg: elt.get_attribute(cfg.attribute),
    types.outer_html: lambda elt, cfg: elt.get_attribute(cfg.attribute),
    types.src: lambda elt, cfg: elt.get_attribute(cfg.attribute),
    WebElement: lambda elt, cfg: elt,
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
        key = (
            Annotated[str, types.Attribute(self.config.attribute)]
            if self.config.attribute
            else self.config.element_type
        )
        return GET_TRANSFORMERS[key](element, self.config)


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
        key = (
            Annotated[str, types.Attribute(self.config.attribute)]
            if self.config.attribute
            else self.config.element_type
        )
        return [GET_TRANSFORMERS[key](element, self.config) for element in elements]


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
            default=NotImplemented,
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
            default=NotImplemented,
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
            default=NotImplemented,
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
            default=NotImplemented,
            wait=self.config.wait,
        )
        cls = type(
            self.config.element_type.__qualname__,
            self.config.element_type.__bases__,
            {**self.config.element_type.__dict__},
        )
        return [cls(element) for element in elements]
