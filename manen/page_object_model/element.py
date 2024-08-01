from datetime import datetime
from typing import TYPE_CHECKING, Callable, TypeVar

import dateparser
from selenium.webdriver.remote.webelement import WebElement

from manen.finder import find
from manen.helpers import extract_integer
from manen.page_object_model import dom as dom
from manen.page_object_model.config import Config

if TYPE_CHECKING:
    from manen.page_object_model.webarea import WebArea

T = TypeVar("T")
TTransformers = dict[type[T], Callable[[WebElement], T]]


GET_TRANSFORMERS: TTransformers = {
    datetime: lambda element: dateparser.parse(element.text),
    dom.HRef: lambda element: element.get_attribute("href"),
    dom.ImageSrc: lambda element: element.get_attribute("src"),
    dom.InnerHTML: lambda element: element.get_attribute("innerHTML"),
    int: lambda element: extract_integer(element.text),
    dom.OuterHTML: lambda element: element.get_attribute("outerHTML"),
    str: lambda element: element.text,
    WebElement: lambda element: element,
}


class ImmutableDomComponent:
    def __init__(self, config: Config):
        self.config = config

    def __set__(self, webarea: "WebArea", value):
        raise Exception("Cannot set element")

    def __delete__(self, webarea: "WebArea"):
        raise Exception("Cannot delete element")


class Element(ImmutableDomComponent):
    def __get__(self, webarea: "WebArea", unused_cls_webarea: type["WebArea"]):
        element = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        if element == self.config.default:
            return element
        return GET_TRANSFORMERS[self.config.element_type](element)


class Elements(ImmutableDomComponent):
    def __get__(self, webarea: "WebArea", unused_cls_webarea: type["WebArea"]):
        elements = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=True,
            default=self.config.default,
            wait=self.config.wait,
        )
        if elements == self.config.default:
            return elements
        return [
            GET_TRANSFORMERS[self.config.element_type](element) for element in elements
        ]


class InputElement:
    def __init__(self, config: Config):
        if config.many:
            raise ValueError("Cannot use InputElement with many=True")
        self.config = config

    def __get__(self, webarea: "WebArea", unused_cls_webarea: type["WebArea"]):
        element = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        return element.get_attribute("value")

    def __set__(self, webarea: "WebArea", value):
        element = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=False,
            default=NotImplemented,
            wait=self.config.wait,
        )
        element.clear()
        element.send_keys(value)


class CheckboxElement:
    def __init__(self, config: Config):
        self.config = config

    def __get__(self, webarea: "WebArea", unused_cls_webarea: type["WebArea"]):
        element = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=False,
            default=self.config.default,
            wait=self.config.wait,
        )
        return element.get_attribute("checked") == "true"

    def __set__(self, webarea: "WebArea", value: bool):
        element = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=False,
            default=NotImplemented,
            wait=self.config.wait,
        )
        if value != (element.get_attribute("checked") == "true"):
            element.click()


class Region(ImmutableDomComponent):
    def __get__(self, webarea: "WebArea", cls_webarea: type["WebArea"]) -> "WebArea":
        from manen.page_object_model.webarea import Form, WebArea

        element = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=False,
            default=NotImplemented,
            wait=self.config.wait,
        )
        name = self.config.element_type.__qualname__
        base = (Form,) if Form.is_form(self.config.element_type) else (WebArea,)
        cls = type(name, base, {**self.config.element_type.__dict__})
        return cls(element)


class Regions(ImmutableDomComponent):
    def __get__(self, webarea: "WebArea", cls_webarea: type["WebArea"]):
        from manen.page_object_model.webarea import WebArea

        elements = find(
            selector=self.config.selectors,
            inside=webarea._scope,
            many=True,
            default=NotImplemented,
            wait=self.config.wait,
        )
        name = self.config.element_type.__qualname__
        cls = type(name, (WebArea,), {**self.config.element_type.__dict__})
        return [cls(element) for element in elements]
