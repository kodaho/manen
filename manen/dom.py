from contextlib import contextmanager
from functools import reduce

from .exceptions import UnsettableElement
from .finder import find
from .helpers import extract_integer


__all__ = (
    "Action",
    "Element",
    "Elements",
    "FigureElement",
    "FigureElements",
    "TextElement",
    "TextElements",
    "LinkElement",
    "LinkElements",
    "InputElement",
    "Page",
    "Region",
    "Regions",
    "Frame",
    "Frames",
)


class WebArea:
    def __init__(self, container, _context="PAGE"):
        self._container = container
        self._context = _context
        self._driver = getattr(container, "parent", container)

    @property
    def container(self):
        if self._context == "FRAME":
            return self._driver
        return self._container

    @contextmanager
    def switch_container(self):
        try:
            if self._context == "FRAME":
                self._driver.switch_to.frame(self._container)
            yield self.container
        finally:
            if self._context == "FRAME":
                self._driver.switch_to.default_content()


class DomAccessor:
    def __init_subclass__(cls, many=False, post_processing=None):
        cls._post_processing = post_processing or []
        cls._many = many
        return super().__init_subclass__()

    def _apply_post_processing(self, element):
        return reduce(lambda x, f: f(x) if x else x, self.post_processing, element)

    def __init__(self, selectors, default=NotImplemented, wait=0, post_processing=None):
        self.selectors = selectors if isinstance(selectors, list) else [selectors]
        self.default = default
        self.wait = wait
        self.post_processing = self._post_processing + (
            [post_processing] if post_processing else []
        )

    def _get_elements(self, area: WebArea, area_cls):
        if area is None:
            return self

        with area.switch_container() as container:
            lookup = find(
                inside=container,
                many=getattr(self, "_many", False),
                wait=self.wait,
                default=self.default,
            )

            elements = lookup(self.selectors)

            if elements == self.default:
                return elements

            if isinstance(elements, list):
                return [self._apply_post_processing(element) for element in elements]

            return self._apply_post_processing(elements)

    def _build_elements(self, elements, context):
        name = self.__class__.__name__
        base = (WebArea,)
        base_dict = dict(self.__class__.__dict__)

        if getattr(self, "_many", False):
            return [
                type(name, base, base_dict)(element, _context=context)
                for element in elements
            ]
        return type(name, base, base_dict)(elements, _context=context)


class Page(WebArea):
    @property
    def title(self):
        return self._container.title

    @property
    def page_source(self):
        return self._container.page_source

    def click_with_js(self, element):
        return self._container.click_with_js(element)


class Region(DomAccessor):
    def __init__(self, selector, wait=0, default=NotImplemented):
        self.selectors = selector
        self.wait = wait
        self.default = default

    def __get__(self, area, area_cls):
        elements = super()._get_elements(area, area_cls)
        return self._build_elements(elements, context="REGION")

    def __set__(self, instance, value):
        raise UnsettableElement(self.__class__.__name__)


class Regions(Region, many=True):
    pass


class Frame(DomAccessor):
    def __get__(self, area, area_cls):
        elements = super()._get_elements(area, area_cls)
        return self._build_elements(elements, context="FRAME")

    def __set__(self, instance, value):
        raise UnsettableElement(self.__class__.__name__)


class Frames(Frame, many=True):
    pass


class Action:
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs


class Element(DomAccessor):
    def __get__(self, area, area_cls):
        return super()._get_elements(area, area_cls)

    def __set__(self, page, value):
        raise UnsettableElement(self.__class__.__name__)


class Elements(Element, many=True):
    pass


class LinkElement(Element, post_processing=[lambda x: x.get_attribute("href")]):
    pass


class LinkElements(LinkElement, many=True):
    pass


class TextElement(Element, post_processing=[lambda x: x.text]):
    pass


class TextElements(TextElement, many=True):
    pass


class FigureElement(Element, post_processing=[lambda x: x.text, extract_integer]):
    pass


class FigureElements(Element, many=True):
    pass


class InputElement(Element, post_processing=[lambda x: x.get_attribute("value")]):
    def __set__(self, area, value):
        with area.switch_container() as container:
            input_ = find(self.selectors, inside=container)
            if isinstance(value, Action):
                getattr(input_, value.method_to_call)(*value.args, **value.kwargs)
            else:
                input_.clear()
                input_.send_keys(value)
