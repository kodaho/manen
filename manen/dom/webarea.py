from .element import Element
from ..exceptions import BadConfiguration, UnsettableElement
from ..finder import find


class WebArea:
    def __init__(self, container):
        self._container = container


class Page(WebArea):
    class Meta:
        pass

    body = Element("css:body")

    @property
    def title(self):
        return self._container.title

    @property
    def page_source(self):
        return self._container.page_source

    @property
    def is_active(self):
        meta_url = getattr(self.Meta, "url", None)
        if meta_url is None:
            raise BadConfiguration(
                "A page instance should a value for `url` defined in Meta."
            )
        return meta_url.match(self._container.current_url) is not None

    def click_with_js(self, element):
        return self._container.click_with_js(element)


class Region:
    def __init__(self, region_selector, wait=0, default=NotImplemented):
        self.region_selector = region_selector
        self.wait = wait
        self.many = False
        self.default = default

    def __get__(self, page, class_):
        lookup = find(
            inside=page._container,
            many=self.many,
            wait=self.wait,
            default=self.default,
        )
        elements = lookup(self.region_selector)

        region_name = self.__class__.__name__
        bases = (WebArea,)
        base_dict = dict(self.__class__.__dict__)

        if self.many:
            return [
                type(region_name, bases, base_dict)(element) for element in elements
            ]
        return type(region_name, bases, base_dict)(elements)

    def __set__(self, instance, value):
        raise UnsettableElement(self.__class__.__name__)


class Regions(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.many = True
