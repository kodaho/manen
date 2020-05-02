# pylint: disable=too-few-public-methods
"""This module provides an implementation of the `Page Object design pattern
<https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
described in Selenium documentation. By combining the classes ``Page`` and
``Region`` with the ``Element`` object (and all its subclasses), you can
easily describe any web pages and access all the DOM elements in a simple
way through a Python class.

Let's say you want to work with `manen` on the website `PyPi <https://pypi.org/>`_
to get all the packages informations matching a given query (e.g.: selenium).
The first step to work with `manen.dom` is to define the Python classes which
will describe the web pages you are working on. Here we will define all the
classes in an external file called `pypi_pom.py`.

.. code-block:: python

    from manen.page_object_model import (Page, Regions, InputElement,
                                         TextElement, LinkElement)

    class HomePage(Page):
        query = InputElement("input[id='search']")

    class SearchResultPage(Page):
        class ResultRegions(Regions):
            name = TextElement("h3 span.package-snippet__name")
            version = TextElement("h3 span.package-snippet__version")
            link = LinkElement("a.package-snippet")
            description = TextElement("p.package-snippet__description")

        n_results = FigureElement("//*[@id='content']//form/div[1]/div[1]/p/strong")x
        results = ResultRegions("ul[aria-label='Search results'] li")


Once you have defined all the classes describing the web pages, you can start
interacting by instanciating the `Page` subclasses with an instance of `WebDriver`.
Here we will suppose that you have an instance of `WebDriver` stored in the variable
`browser`.

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

This is a glitch of what you can do with `manen.page_object_model`. See the
documentation of each objects to check all the features provided by the module.
"""
from contextlib import contextmanager
from functools import reduce
from typing import TYPE_CHECKING, Any, Callable, List, Union, Optional

from .exceptions import UnsettableElement
from .finder import find
from .helpers import (  # pylint: disable=unused-import # (see PyCQA/pylint#1603)
    extract_integer,
)

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    PostProcessingFunction = Callable[["SeleniumElement"], Any]
    SeleniumElement = Union["WebDriver", "WebElement"]

__all__ = (
    "Action",
    "Element",
    "Elements",
    "FigureElement",
    "FigureElements",
    "Frame",
    "Frames",
    "InputElement",
    "LinkElement",
    "LinkElements",
    "Page",
    "Region",
    "Regions",
    "TextElement",
    "TextElements",
    "WebArea",
)


class WebArea:
    """A `WebArea` element is a wrapper around a Selenium element which works
    together with an `Element` (and its subclasses). Any class attribute defined
    with the class `Element` in a class which inherits from `WebArea` will be
    accessible as an instance attribute; it will, when accessed, evaluate the
    selector to retrieve the element.

    Example::

        class Area(WebArea):
            body = Element("css:body")
            first_div = Element("css:div")
            links = Elements("css:a")
        >>> area = Area(browser)
        >>> area.body
        <selenium.webdriver.remote.webelement.WebElement id="abcdef-1234">
        >>> div_area = Area(area.first_div)
        >>> div_area.links # Find all the links in the first div element of the body

    .. note:: This class is mainly used by `manen` to build the classes `Page`,
       `Region` and `Frame`. You shouldn't need to use this class to create
       basic page objects (see the documentation of `Page`, `Region` and `Frame`
       which are the main objects for page object modelling).
    """

    def __init__(self, container: "SeleniumElement", _context: str = "PAGE"):
        self._container = container
        self._context = _context
        self._driver: "WebDriver" = getattr(container, "parent", container)

    @property
    def container(self) -> "SeleniumElement":
        """Selenium element where to perform the query in order to retrieve
        some elements with selectors.

        .. warning:: Prefer using the context manager `switch_container()`
            rather than this property."""
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


class DomAccessor:
    _post_processing: List["PostProcessingFunction"] = []
    _many = False

    def __init_subclass__(  # pylint: disable=bad-continuation
        cls,
        many: bool = False,
        post_processing: Optional[List["PostProcessingFunction"]] = None,
    ):
        super().__init_subclass__()
        cls._post_processing = post_processing or []
        cls._many = many

    def __init__(  # pylint: disable=bad-continuation
        self,
        selectors: Union[str, List[str]],
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
        self.selectors = selectors if isinstance(selectors, list) else [selectors]
        self.default = default
        self.wait = wait
        self.post_processing = self._post_processing + (
            [post_processing] if post_processing else []
        )

    def _apply_post_processing(self, element: "WebElement") -> Any:
        return reduce(lambda x, f: f(x) if x else x, self.post_processing, element)

    def _get_from(self, area: WebArea, _) -> Any:
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

    def _build_elements(self, elements, context) -> Union[WebArea, List[WebArea]]:
        name = self.__class__.__name__
        base = (WebArea,)
        base_dict = dict(self.__class__.__dict__)

        if self._many:
            return [
                type(name, base, base_dict)(element, _context=context)
                for element in elements
            ]
        return type(name, base, base_dict)(elements, _context=context)


class Page(WebArea):
    @property
    def title(self) -> str:
        return self._container.title

    @property
    def page_source(self) -> str:
        return self._container.page_source

    def click_with_js(self, element):
        return self._container.click_with_js(element)


class Region(DomAccessor):
    def __get__(self, area, area_cls) -> WebArea:
        element = super()._get_from(area, area_cls)
        element = self._build_elements(element, context="REGION")
        assert isinstance(element, WebArea)  # For mypy
        return element

    def __set__(self, instance, value):
        raise UnsettableElement(self.__class__.__name__)


class Regions(Region, many=True):
    pass


class Frame(DomAccessor):
    def __get__(self, area, area_cls) -> WebArea:
        element = super()._get_from(area, area_cls)
        element = self._build_elements(element, context="FRAME")
        assert isinstance(element, WebArea)  # For mypy
        return element

    def __set__(self, instance, value):
        raise UnsettableElement(self.__class__.__name__)


class Frames(Frame, many=True):
    pass


class Action:
    def __init__(self, method: Callable, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs


class Element(DomAccessor):
    """Must be placed in a class based on WebArea.
    Returned a Selenium WebElement.
    """

    def __get__(self, area, area_cls) -> "WebElement":
        return super()._get_from(area, area_cls)

    def __set__(self, page, value):
        raise UnsettableElement(self.__class__.__name__)


class Elements(Element, many=True):
    pass


class LinkElement(Element, post_processing=[lambda x: x.get_attribute("href")]):
    pass


class LinkElements(  # pylint: disable=bad-continuation
    LinkElement, many=True, post_processing=[lambda x: x.get_attribute("href")],
):
    pass


class TextElement(Element, post_processing=[lambda x: x.text]):
    pass


class TextElements(TextElement, many=True, post_processing=[lambda x: x.text]):
    pass


class FigureElement(Element, post_processing=[lambda x: x.text, extract_integer]):
    pass


class FigureElements(  # pylint: disable=bad-continuation
    Element, many=True, post_processing=[lambda x: x.text, extract_integer]
):
    """Get elements from a HTML page matching a set of selectors and extract a
    figure from each text element.
    """


class InputElement(Element, post_processing=[lambda x: x.get_attribute("value")]):
    """Interface with an <input> element of a DOM. Setting the variable of the
    InputElement will also set the value of the DOM.

    Example::

        class LoginPage(Page):
            email = InputElement("input[type='email']")
            password = InputElement("input[type='password']")
        >>> from manen.page_object_model import Action
        >>> login_page = LoginPage(browser)
        >>> login_page.email = "username@manen.co"
        >>> login_page.password = "dummypassword"
        >>> login_page.password = Action("submit")
    """

    def __set__(self, area, value):
        with area.switch_container() as container:
            input_ = find(self.selectors, inside=container)
            if isinstance(value, Action):
                getattr(input_, value.method_to_call)(*value.args, **value.kwargs)
            else:
                input_.clear()
                input_.send_keys(value)
