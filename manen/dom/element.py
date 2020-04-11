from functools import reduce
from typing import Callable, List

from ..exceptions import UnsettableElement
from ..finder import find
from ..helpers import extract_integer

__all__ = (
    "Action",
    "Element",
    "Elements",
    "FigureElement",
    "TextElement",
    "TextElements",
    "LinkElement",
    "LinkElements",
    "InputElement",
)


class Action:
    def __init__(self, method, *args, **kwargs):
        self.method_to_call = method
        self.args = args
        self.kwargs = kwargs


class Element:
    _post: List[Callable] = []

    def __init__(self, selector, default=NotImplemented, wait=0, post=None):
        selectors = selector if isinstance(selector, list) else [selector]
        self.selectors = selectors
        self.default = default
        self.wait = wait
        self.transformer = self._post + ([post] if post else [])
        self.many = False

    def __set__(self, page, value):
        raise UnsettableElement(self.__class__.__name__)

    def __get__(self, page, page_cls):
        if page is None:
            return self

        finder = find(
            inside=page._container,
            default=self.default,
            wait=self.wait,
            many=self.many,
        )
        elements = finder(self.selectors)

        if elements == self.default:
            return elements

        if isinstance(elements, list):
            return [
                reduce(lambda x, f: f(x) if x else x, self.transformer, element)
                for element in elements
            ]

        return reduce(lambda x, f: f(x) if x else x, self.transformer, elements)


class Elements(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.many = True


class LinkElement(Element):
    _post = [lambda x: x.get_attribute("href")]


class LinkElements(LinkElement, Elements):
    pass


class TextElement(Element):
    _post = [lambda x: x.text]


class TextElements(TextElement, Elements):
    pass


class FigureElement(Element):
    _post = [lambda x: x.text, extract_integer]


class InputElement(Element):
    _post = [lambda x: x.get_attribute("value")]

    def __set__(self, page, value):
        input_ = find(self.selectors, inside=page._container)
        if isinstance(value, Action):
            getattr(input_, value.method_to_call)(*value.args, **value.kwargs)
        else:
            input_.clear()
            input_.send_keys(value)
        return
