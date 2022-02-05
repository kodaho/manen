# pylint: disable=too-few-public-methods
"""
manen.page_object_model
=======================

This module provides an implementation of the `Page Object design pattern
<https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
described in Selenium documentation. By combining the classes
:py:class:`~manen.page_object_model.Page` and :py:class:`~manen.page_object_model.Region`
with the :py:class:`~manen.page_object_model.Element` object (and all its subclasses),
you can easily describe any web pages and access all the DOM elements in a simple
way through a Python class.

Let's say that you want, given a query, to get all the packages information from
the website `PyPi <https://pypi.org/>`_ (e.g.: "selenium"). The first step to
work with :py:mod:`manen.page_object_model` is to define the Python classes which
will describe the web pages you are working on. Here we will define all the
classes in an external file called ``pypi_pom.py``.

.. code-block:: python

    from manen.page_object_model import (Page, Regions, InputElement,
                                         TextElement, LinkElement,
                                         IntegerElement)

    class HomePage(Page):
        query = InputElement("input[id='search']")

    class SearchResultPage(Page):
        class ResultRegions(Regions):
            name = TextElement("h3 span.package-snippet__name")
            version = TextElement("h3 span.package-snippet__version")
            link = LinkElement("a.package-snippet")
            description = TextElement("p.package-snippet__description")

        n_results = IntegerElement("//*[@id='content']//form/div[1]/div[1]/p/strong")
        results = ResultRegions("ul[aria-label='Search results'] li")


Once you have defined all the classes describing the web pages, you can start
interacting by instanciating the :py:class:`~manen.page_object_model.Page` subclass
with an instance of :py:class:`~selenium.webdriver.remote.webdriver.WebDriver`. Here
we will suppose that you have an instance of
:py:class:`~selenium.webdriver.remote.webdriver.WebDriver` stored in the variable
``browser``.

.. code-block:: python

    >>> from pypi_pom import HomePage, SearchResultPage
    >>> home_page = HomePage(browser)
    >>> home_page.query = "selenium"
    >>> home_page.query = Action("submit")
    # This will direct you to a search result page of PyPi.
    >>> browser.current_url
    "https://pypi.org/search/?q=selenium"
    >>> page = SearchResultPage(browser)
    >>> page.n_results
    1600
    >>> len(page.results)
    20
    >>> page.results[0]
    <pypi_pom.ResultRegions>
    >>> page.results[0].name
    "selenium"
    >>> page.results[0].version
    "3.141.0"
    >>> page.results[0].link
    "https://pypi.org/project/selenium/"

This is a glitch of what you can do with :py:mod:`manen.page_object_model`. See the
documentation of each objects to check all the features provided by the module.
"""
from contextlib import contextmanager
from functools import reduce
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

import dateparser
import yaml
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from .exceptions import ManenException, UnsettableElement
from .finder import find
from .helpers import extract_integer

if TYPE_CHECKING:
    from .typing import SeleniumElement, WebElement

    PostProcessingFunction = Callable[[Any], Any]

__all__ = (
    "Action",
    "CheckboxElement",
    "DatetimeElement",
    "DatetimeElements",
    "Element",
    "Elements",
    "Frame",
    "ImageSourceElement",
    "ImageSourceElements",
    "InnerHtmlElement",
    "InnerHtmlElements",
    "InputElement",
    "IntegerElement",
    "IntegerElements",
    "LinkElement",
    "LinkElements",
    "OuterHtmlElement",
    "OuterHtmlElements",
    "Page",
    "RadioButtonElement",
    "Region",
    "Regions",
    "SelectElement",
    "TextElement",
    "TextElements",
    "WebArea",
)


class WebArea:
    """Wrapper around a Selenium element which works together with an
    :py:class:`~manen.page_object_model.Element` (and its subclasses). Any class
    attribute instanciated with :py:class:`~manen.page_object_model.Element`
    will be accessible as an instance attribute; it will, when accessed, evaluate
    the selector to retrieve the element.

    Example::

        >>> class Area(WebArea):
        ...    body = Element("css:body")
        ...    first_div = Element("css:div")
        ...    links = Elements("css:a")
        >>> area = Area(browser)
        >>> area.body
        <selenium.webdriver.remote.webelement.WebElement id="abcdef-1234">
        >>> div_area = Area(area.first_div)
        >>> div_area.links # Find all the links in the first div element of the body

    .. note:: This class is mainly used internally to build the classes
      :py:class:`~manen.page_object_model.Page`,
      :py:class:`~manen.page_object_model.Region` and
      :py:class:`~manen.page_object_model.Frame`. You shouldn't need to use this
      class to create basic page objects (see the documentation of each object to
      see how to efficiently used page object modelling).
    """

    class Meta:
        """Metadata for a webarea."""

        selectors_path: str = ""
        selectors: Dict[str, Any] = {}
        url: Optional[str] = None

    def __init__(
        self,
        container: "SeleniumElement",
        _context: str = "PAGE",
    ):
        """
        Args:
            container ("SeleniumElement"): Parent element in which all the
                elements will be searched.
        """
        self._container = container
        self._context = _context
        if isinstance(container, WebDriver):
            self._driver = container
        else:
            self._driver = container.parent
        if getattr(self.Meta, "selectors_path", None):
            self.Meta.selectors = load_selector_config(self.Meta.selectors_path)

    @property
    def container(self) -> "SeleniumElement":
        """Selenium element where to perform the query in order to retrieve
        some elements with selectors.

        .. warning:: Prefer using the context manager `switch_container()`
            rather than this property.
        """
        if self._context == "FRAME":
            return self._driver
        return self._container

    @contextmanager
    def switch_container(self):
        """Context manager which returns the container where to perform the query.
        In most cases, it is the container used to instanciate `WebArea` but some
        additional computing may be needed in some cases (for example, when working
        with frame element). The additional computation will occur based on the
        value of the attribute `_context`, entered at instanciation.

        Yields:
            container (:py:class:`selenium.webdriver.remote.webelement.WebElement`):
                Selenium element where to evaluate a selector
        """
        try:
            if self._context == "FRAME":
                self._driver.switch_to.frame(self._container)
            yield self.container
        finally:
            if self._context == "FRAME":
                self._driver.switch_to.default_content()

    @classmethod
    def _selectors_from_meta(cls, name):
        if name not in cls.Meta.selectors["elements"]:
            raise ManenException("No selectors defined for element `%s`." % name)
        selectors = cls.Meta.selectors["elements"][name]
        return (
            selectors["selectors"]
            if isinstance(selectors, dict)
            else selectors
            if isinstance(selectors, list)
            else [selectors]
        )


class DomAccessor:
    """Main interface of a DOM element."""

    _post_processing: List["PostProcessingFunction"] = []
    _many = False

    def __init_subclass__(
        cls,
        many: Optional[bool] = None,
        post_processing: Optional[List["PostProcessingFunction"]] = None,
    ):
        super().__init_subclass__()
        cls._post_processing = (
            cls._post_processing
            if post_processing is None
            else cls._post_processing + post_processing
        )
        cls._many = cls._many if many is None else many

    def __init__(
        self,
        selectors: Optional[Union[str, List[str]]] = None,
        *,
        default: Any = NotImplemented,
        wait: int = 0,
        post_processing: Optional["PostProcessingFunction"] = None,
    ):
        """Main interface with a DOM element.

        Args:
            selectors (Union[str, List[str]]): Selector or sets of selectors
                used to identify the DOM element(s). Each selector must be in
                form of {selection_method}:{selector} where {selection_method}
                is in .... Note that if no selection method is specified, it
                will be inferred from the selector (but only the CSS and XPath
                method can be inferred).
            default (Any, optional): Default value to returned if no element
                matching the selector(s) is found. Defaults to NotImplemented.
            wait (int, optional): Time to wait before throwing an error.
                Defaults to 0.
            post_processing (Callable[[Any], Any]): Callable called after
                getting the element from the DOM. Defaults to None.
        """
        self._selectors = (
            selectors
            if selectors is None or isinstance(selectors, list)
            else [selectors]
        )
        self._default = default
        self._wait = wait
        self._post_processing = [post_processing] if post_processing else []
        self._name: str
        self._path: Tuple[str, ...]

    def __set_name__(self, owner, name: str):
        if name.startswith("_"):
            raise ManenException(
                "To prevent any side effect, the element name cannot start with '_'."
            )
        self._name = name
        self._path = tuple(addr for addr in owner.__qualname__.split(".")[1:] if addr)

    def _apply_post_processing(self, element: "WebElement") -> Any:
        return reduce(
            lambda x, f: f(x) if x else x,
            self.__class__._post_processing  # pylint: disable=protected-access
            + self._post_processing,
            element,
        )

    def _get_from(self, area: WebArea, area_class) -> Any:
        if area is None:
            return self

        selectors = (
            self._selectors
            if self._selectors is not None
            else area_class._selectors_from_meta(  # pylint: disable=protected-access
                self._name
            )
        )

        with area.switch_container() as container:
            lookup = find(
                inside=container,
                many=getattr(self, "_many", False),
                wait=self._wait,
                default=self._default,
            )

            elements = lookup(selectors)

            if elements == self._default:
                return elements

            if isinstance(elements, list):
                return [self._apply_post_processing(element) for element in elements]

            return self._apply_post_processing(elements)

    def _build_elements(self, elements, context, area) -> Union[WebArea, List[WebArea]]:
        name = f"{area.__class__.__qualname__}.{self.__class__.__name__}"
        base = (WebArea,)
        metadata = dict(area.Meta.__dict__) if area else {}
        metadata.update(
            selectors=getattr(area.Meta, "selectors", {})
            .get("elements", {})
            .get(self._name, {})
        )
        base_dict = {
            **dict(self.__class__.__dict__),
            "Meta": type("Meta", (), metadata),
        }
        if self._many:
            return [
                type(name, base, base_dict)(element, _context=context)
                for element in elements
            ]
        return type(name, base, base_dict)(elements, _context=context)


class Page(WebArea):
    """Modelize a HTML page in the Page Object Model design pattern. The attributes of
    :py:class:`~manen.page_object_model.Page` should be an instance of
    :py:class:`~manen.page_object_model.Element` (or any subclass) or an instance of
    :py:class:`~manen.page_object_model.Region`.

    Example::

        >>> class QueryPage(Page):
        ...     main_title = TextElement("h1")
        ...     search = InputElement("input[name='query']")
        ...     button_validate = Element("button#validate")
        >>> page = QueryPage(browser)
        >>> page.search = "python manen"
        >>> button_validate.click()
    """

    @classmethod
    def from_object(
        cls,
        page_objects: Dict[str, "Element"],
        bases: Tuple = (),
        name: str = "Page",
    ):
        """Build a Page class from a dictionary."""
        base = (*bases, cls)
        return type(name, base, page_objects)  # type: ignore

    @classmethod
    def from_yaml(cls, filepath: Union[str, Path]):
        """Build a Page class from a YAML file."""
        path = Path(filepath) if isinstance(filepath, str) else filepath
        with path.open(mode="r", encoding="utf-8") as page_file:
            page_definition = yaml.load(page_file, Loader=PageObjectLoader)

        base_pages = page_definition.get("extends", [])
        bases = (Page.from_yaml(path.parent / base_page) for base_page in base_pages)

        name = page_definition.get("name", f"{path.stem.capitalize()}Page")

        page_objects = page_definition.get("elements")
        metadata = page_definition.get("meta", {})
        page_objects.update(Meta=type("Meta", (), metadata))

        return cls.from_object(page_objects, bases=tuple(bases), name=name)

    @property
    def title(self) -> str:
        """Title of the page."""
        return self._driver.title

    @property
    def page_source(self) -> str:
        """Code source of the page."""
        return self._driver.page_source

    def click_with_js(self, element: "WebElement"):
        """Click on an element using a JavaScript script."""
        js_script = """arguments[0].click()"""
        return self._driver.execute_script(js_script, element)

    def open(self, **kwargs):
        """Go to the URL specified in the Meta class associated to a Page. Any
        keywords arguments will be passed to the URL to format it.
        """
        url = self.__class__.Meta.url
        if url is not None:
            return self._driver.get(url.format(**kwargs))
        raise ManenException("No URL specified.")


class Region(DomAccessor):
    """Modelize a region of a webpage. A region is a set of elements contained
    in the same container.

    .. note:: Contrary to :py:class:`~manen.page_object_model.Page`, this class
       should not be instanciated with an instance of WebDriver. This class is
       closer to an :py:class:`~manen.page_object_model.Element` than a
       :py:class:`~manen.page_object_model.Element`.

    Example::

        >>> from manen.page_object_model import Page, Region, InputElement, Action
        >>> class LoginPage(Page):
        ...     class FormRegion(Region):
        ...         email = InputElement("input#email")
        ...         password = InputElement("input#password")
        ...     form_region = FormRegion("div#form-container")
        >>> page = LoginPage(browser)
        >>> page.form_region.email = "hello@manen.com"
        >>> page.form_region.password = "strong_password"
        >>> page.form_region.password = Action("submit")
    """

    def __get__(self, area: WebArea, area_cls) -> Union[WebArea, List[WebArea]]:
        element = super()._get_from(area, area_cls)
        element = self._build_elements(element, context="REGION", area=area)
        return element

    def __set__(self, area: WebArea, value: Any):
        raise UnsettableElement(self.__class__.__name__)

    @classmethod
    def _yaml_loader(cls, loader: yaml.Loader, node: yaml.Node):
        if not isinstance(node, yaml.nodes.MappingNode):
            raise Exception
        region = loader.construct_mapping(node, deep=True)
        elements = region.pop("elements")
        name = region.pop("name", cls.__name__)
        return type(name, (cls,), elements)(**region)


class Regions(Region, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.Region`."""


class Frame(DomAccessor):
    """Enable to work with <iframe> element."""

    def __get__(self, area, area_cls) -> WebArea:
        element = super()._get_from(area, area_cls)
        element = self._build_elements(element, context="FRAME", area=area)
        assert isinstance(element, WebArea)  # For mypy
        return element

    def __set__(self, instance, value):
        raise UnsettableElement(self.__class__.__name__)


class Action:
    """Enable to interact with an input by calling a method of the WebElement. This is
    intended to be used by a subtype of :py:class:`~manen.page_object_model.Element`
    which can be set.

    Example::

        >>> page.query = "python manen"
        >>> page.query = Action("submit")
    """

    def __init__(self, method: str, *args, **kwargs):
        """
        Args:
            method (str): name of the method to call. This should be a method ones
                of a method of :py:class:`selenium.webdriver.remote.webelement.WebElement`
            *args (Any): positional arguments called with the method
            **kwargs : keyword arguments called with the method
        """
        self.method = method
        self.args = args
        self.kwargs = kwargs


class Element(DomAccessor):
    """Based on one or several selectors, extract a
    :py:class:`selenium.webdriver.remote.webelement.WebElement` from a region or page.

    An element should be used to initialize a class attribute of a subclass of
    :py:class:`~manen.page_object_model.Page`, :py:class:`~manen.page_object_model.Region`
    or :py:class:`~manen.page_object_model.Frame` (or any subtypes of
    :py:class:`~manen.page_object_model.WebArea`)
    """

    def __get__(self, area: WebArea, area_cls: type) -> "WebElement":
        return super()._get_from(area, area_cls)

    def __set__(self, area: WebArea, value: Any):
        raise UnsettableElement(self.__class__.__name__)

    @classmethod
    def _yaml_loader(cls, loader: yaml.Loader, node: yaml.Node):
        if isinstance(node, yaml.nodes.SequenceNode):
            return cls(selectors=loader.construct_sequence(node))
        if isinstance(node, yaml.nodes.MappingNode):
            return cls(**loader.construct_mapping(node))
        if isinstance(node, yaml.nodes.ScalarNode):
            return cls(selectors=[loader.construct_scalar(node)])  # type: ignore
        raise TypeError(
            "Unexpected node type encoutered while loading node `%s`" % node
        )


class Elements(Element, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.Element`."""


class LinkElement(Element, post_processing=[lambda x: x.get_attribute("href")]):
    """Extract the link from an element matching one or several selectors."""


class LinkElements(LinkElement, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.LinkElement`."""


class TextElement(Element, post_processing=[lambda x: x.text]):
    """Extract text from an element matching one or several selectors."""


class TextElements(TextElement, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.TextElement`."""


class ImageSourceElement(Element, post_processing=[lambda x: x.get_attribute("src")]):
    """Extract the source URL of an image."""


class ImageSourceElements(ImageSourceElement, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.ImageSourceElement`."""


class InnerHtmlElement(
    Element,
    post_processing=[lambda x: x.get_property("innerHTML")],
):
    """Extract the inner HTML from an element."""


class InnerHtmlElements(InnerHtmlElement, many=True):
    """Pluralized version of :py:class:`manen.page_object_model.InnerHtmlElement`."""


class IntegerElement(TextElement, post_processing=[extract_integer]):
    """Extract the integer from a text element matching a selector or set of selectors."""


class IntegerElements(IntegerElement, many=True):
    """Get elements from a HTML page matching a set of selectors and extract a
    integer from each text element.
    Pluralized version of :py:class:`~manen.page_object_model.IntegerElement`
    """


class DatetimeElement(TextElement, post_processing=[dateparser.parse]):
    """Extract a datetime from a text element matching a set of selectors."""


class DatetimeElements(DatetimeElement, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.DatetimeElement`."""


class OuterHtmlElement(
    Element,
    post_processing=[lambda x: x.get_property("outerHTML")],
):
    """Extract the outer HTML of an element."""


class OuterHtmlElements(OuterHtmlElement, many=True):
    """Pluralized version of :py:class:`~manen.page_object_model.OuterHtmlElement`."""


class InputElement(Element, post_processing=[lambda x: x.get_attribute("value")]):
    """Interface with an <input> element of a DOM. Setting the variable of the
    InputElement will also set the value of the DOM.

    Example::

        >>> from manen.page_object_model import Page, InputElement
        >>> class LoginPage(Page):
        ...     email = InputElement("input[type='email']")
        ...     password = InputElement("input[type='password']")

        >>> from manen.page_object_model import Action
        >>> login_page = LoginPage(browser)
        >>> login_page.email = "username@manen.co"
        >>> login_page.password = "dummypassword"
        >>> login_page.password = Action("submit")
    """

    def __set__(self, area: WebArea, value: Any):
        with area.switch_container() as container:
            input_ = find(self._selectors, inside=container)
            if isinstance(value, Action):
                getattr(input_, value.method)(*value.args, **value.kwargs)
            else:
                input_.clear()
                input_.send_keys(value)


class CheckboxElement(
    Element,
    post_processing=[lambda x: x.get_attribute("checked") == "true"],
):
    """Get the status of a checkbox element directly as a boolan. Setting a
    boolean value to a checkbox element will directly change the value of
    the DOM element.
    """

    def __set__(self, area: WebArea, value: bool):
        with area.switch_container() as container:
            if not isinstance(value, bool):
                raise ValueError(
                    f"The value {value} is not a boolean and so cannot be "
                    "assigned to a checkox element."
                )
            element = find(self._selectors, inside=container)
            if (element.get_attribute("checked") == "true") != value:
                element.click()


class RadioButtonElement(Element):
    """Mapper to a set of choices controlled by a radio element in the page.
    Setting the value of the radio button element will directly update the
    DOM element with the specified value.
    """

    def __get__(self, area, area_class):
        elements = self._get_from(area, area_class)
        right_element = [
            element
            for element in elements
            if element.get_attribute("checked") == "true"
        ]
        return right_element[0].get_attribute("value") if right_element else None

    def __set__(self, area: WebArea, value: bool):
        with area.switch_container() as container:
            elements = find(self._selectors, inside=container, many=True)
            right_element = [
                element
                for element in elements
                if element.get_attribute("value") == value
            ]
            if not right_element:
                raise ValueError(
                    f"The value {value} is not allowed for the radio button element."
                )
            right_element[0].click()


class SelectElement(Element):
    """A shortcut to get an instance of :py:class:`~selenium.webdriver.support.select.Select`
    for a select element. See guide to work with ``Select`` element from
    `official documentation <https://www.selenium.dev/documentation/en/support_packages/working_with_select_elements/>`_.  # pylint: disable=line-too-long
    """

    def __get__(self, area, area_class):
        element = self._get_from(area, area_class)
        return Select(element)


class PageObjectLoader(yaml.Loader):  # pylint: disable=too-many-ancestors
    """Loader used to build page from a YAML file. This loader automatically
    registers all classes in the current module having a method ``_yaml_loader``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        this_module = import_module(".".join([__package__, Path(__file__).stem]))
        for name in __all__:
            class_ = getattr(this_module, name)
            if hasattr(class_, "_yaml_loader"):
                self.add_constructor("!%s" % class_.__name__, class_._yaml_loader)


class IgnorePageObjectLoader(yaml.Loader):  # pylint: disable=too-many-ancestors
    """Loader used to build page from a YAML file. This loader automatically
    registers all classes in the current module having a method ``_yaml_loader``.
    """

    def ignore(self, loader: yaml.Loader, node: yaml.Node) -> Any:
        """Prevent loading a YAML file with special classes when a tag is
        specified. This is useful when you want to a Manen YAML page without
        loading the element but only a regular Python object.

        Args:
            loader (yaml.Loader): instance of YAML Loader which describe how to
                build an element.
            node (yaml.Node): node to construct

        Raises:
            TypeError: Raised if the special tag is set on something different
                from a SequenceNode or a MappingNode

        Returns:
            Any: Python object as it should be loaded with a regular YAML
                Loader
        """
        if isinstance(node, yaml.nodes.SequenceNode):
            return {"selectors": loader.construct_sequence(node)}
        if isinstance(node, yaml.nodes.MappingNode):
            return loader.construct_mapping(node)
        if isinstance(node, yaml.nodes.ScalarNode):
            return loader.construct_scalar(node)
        raise TypeError(f"Unexpected node type encoutered while loading node `{node}`")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        this_module = import_module(".".join([__package__, Path(__file__).stem]))
        for name in __all__:
            class_ = getattr(this_module, name)
            if hasattr(class_, "_yaml_loader"):
                self.add_constructor("!%s" % class_.__name__, self.ignore)


def load_selector_config(path: str, to_element=False) -> Dict[str, Any]:
    """Load the Manen YAML page from a specified path. You can choose whether
    or not the element of a Manen page should return Manen elements or just the
    a regular Python object.

    Args:
        path (str): filepath of the Manen YAML page
        to_element (bool, optional): whether or not to return Manen elements if
            custom tags are specified in the YAML. Defaults to False.

    Returns:
        Dict[str, Any]: Manen page loaded a Python mapping
    """
    with open(path, mode="r", encoding="utf-8") as file:
        return yaml.load(
            file, PageObjectLoader if to_element else IgnorePageObjectLoader
        )
