# pylint: disable=too-few-public-methods
"""This module provides an implementation of the `Page Object design pattern
<https://www.selenium.dev/documentation/en/guidelines_and_recommendations/page_object_models/>`_
described in Selenium documentation. By combining the classes
:py:class:`manen.page_object_model.Page` and :py:class:`manen.page_object_model.Region`
with the :py:class:`manen.page_object_model.Element` object (and all its subclasses),
you can easily describe any web pages and access all the DOM elements in a simple
way through a Python class.

Let's say you want, given a query, to get all the packages information from
the website `PyPi <https://pypi.org/>`_ (e.g.: "selenium"). The first step to
work with :py:mod:`manen.page_object_model` is to define the Python classes which
will describe the web pages you are working on. Here we will define all the
classes in an external file called ``pypi_pom.py``.

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

        n_results = FigureElement("//*[@id='content']//form/div[1]/div[1]/p/strong")
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
    "Frame",
    "InputElement",
    "IntegerElement",
    "IntegerElements",
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
    """Wrapper around a Selenium element which works together with an
    :py:class:`~manen.page_object_model.Element` (and its subclasses). Any class
    attribute instanciated with :py:class:`~manen.page_object_model.Element`
    will be accessible as an instance attribute; it will, when accessed, evaluate
    the selector to retrieve the element.

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

    .. note:: This class is mainly used internally to build the classes
      :py:class:`~manen.page_object_model.Page`,
      :py:class:`~manen.page_object_model.Region` and
      :py:class:`~manen.page_object_model.Frame`. You shouldn't need to use this
      class to create basic page objects (see the documentation of each object to
      see how to efficiently used page object modelling).
    """

    def __init__(self, container: "SeleniumElement", _context: str = "PAGE"):
        """
        Args:
            container ("SeleniumElement"): Parent element in which all the
                elements will be searched.
        """
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
    """Main interface of a DOM element."""

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
    """Modelize a HTML page in the Page Object Model design pattern. The attributes of
    :py:class:`~manen.page_object_model.Page` should be an instance of
    :py:class:`~manen.page_object_model.Element` (or any subclass) or an instance of
    :py:class:`~manen.page_object_model.Region`.

    Example::

        class QueryPage(Page):
            main_title = TextElement("h1")
            search = InputElement("input[name='query']")
            button_validate = Element("button#validate")

        >>> page = QueryPage(browser)
        >>> page.search = "python manen"
        >>> button_validate.click()
    """

    @property
    def title(self) -> str:
        """Title of the page."""
        return self._container.title

    @property
    def page_source(self) -> str:
        """Code source of the page."""
        return self._container.page_source

    def click_with_js(self, element: "WebElement"):
        """Click on an element using a JavaScript script."""
        return self._container.click_with_js(element)


class Region(DomAccessor):
    """Modelize a region of a webpage. A region is a set of elements contained
    in the same container.

    .. note:: Contrary to :py:class:`~manen.page_object_model.Page`, this class
       should not be instanciated with an instance of WebDriver. This class is
       closer to an :py:class:`~manen.page_object_model.Element` than a
       :py:class:`~manen.page_object_model.Element`.

    Example::

        class LoginPage(Page):
            class FormRegion(Region):
                email = InputElement("input#email")
                password = InputElement("input#password")

            form_region = FormRegion("div#form-container")

        >>> page = LoginPage(browser)
        >>> page.form_region.email = "hello@manen.com"
        >>> page.form_region.password = "strong_password"
        >>> page.form_region.password = Action("submit")
    """

    def __get__(self, area: WebArea, area_cls) -> WebArea:
        element = super()._get_from(area, area_cls)
        element = self._build_elements(element, context="REGION")
        assert isinstance(element, WebArea)  # For mypy
        return element

    def __set__(self, area: WebArea, value: Any):
        raise UnsettableElement(self.__class__.__name__)


class Regions(Region, many=True):
    """Pluralized version of :py:class:`manen.page_object_model.Region`."""


class Frame(DomAccessor):
    """Enable to work with <iframe> element."""

    def __get__(self, area, area_cls) -> WebArea:
        element = super()._get_from(area, area_cls)
        element = self._build_elements(element, context="FRAME")
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
    :py:class:`manen.page_object_model.Page`, :py:class:`manen.page_object_model.Region`
    or :py:class:`manen.page_object_model.Frame` (or any subtypes of
    :py:class:`manen.page_object_model.WebArea`)
    """

    def __get__(self, area: WebArea, area_cls: type) -> "WebElement":
        return super()._get_from(area, area_cls)

    def __set__(self, area: WebArea, value: Any):
        raise UnsettableElement(self.__class__.__name__)


class Elements(Element, many=True):
    """Pluralized version of :py:class:`manen.page_object_model.Element`."""


class LinkElement(Element, post_processing=[lambda x: x.get_attribute("href")]):
    """Extract the link from an element matching one or several selectors."""


class LinkElements(  # pylint: disable=bad-continuation
    LinkElement, many=True, post_processing=[lambda x: x.get_attribute("href")],
):
    """Pluralized version of :py:class:`manen.page_object_model.LinkElement`."""


class TextElement(Element, post_processing=[lambda x: x.text]):
    """Extract text from an element matching one or several selectors."""


class TextElements(TextElement, many=True, post_processing=[lambda x: x.text]):
    """Pluralized version of :py:class:`manen.page_object_model.TextElement`."""


class IntegerElement(Element, post_processing=[lambda x: x.text, extract_integer]):
    """Extract the integer from a text element matching a selector or set of selectors.
    """


class IntegerElements(  # pylint: disable=bad-continuation
    Element, many=True, post_processing=[lambda x: x.text, extract_integer]
):
    """Get elements from a HTML page matching a set of selectors and extract a
    integer from each text element.
    Pluralized version of :py:class:`manen.page_object_model.IntegerElement`
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

    def __set__(self, area: WebArea, value: Any):
        with area.switch_container() as container:
            input_ = find(self.selectors, inside=container)
            if isinstance(value, Action):
                getattr(input_, value.method)(*value.args, **value.kwargs)
            else:
                input_.clear()
                input_.send_keys(value)
