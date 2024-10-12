"""
Flexible and highly customizable function to find one or several elements inside one or several
Selenium elements.
"""

from functools import partial
from typing import Any, Literal, overload

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from manen.exceptions import ElementNotFound, PollTimeoutException
from manen.helpers import poll
from manen.typing import DriverOrElement, WebElement

METHODS_MAPPER = {
    "class_name": By.CLASS_NAME,
    "class": By.CLASS_NAME,
    "cls": By.CLASS_NAME,
    "css": By.CSS_SELECTOR,
    "id": By.ID,
    "link_text": By.LINK_TEXT,
    "link": By.LINK_TEXT,
    "name": By.NAME,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "plink": By.PARTIAL_LINK_TEXT,
    "tag_name": By.TAG_NAME,
    "tag": By.TAG_NAME,
    "xp": By.XPATH,
    "xpath": By.XPATH,
}


def parse_selector(selector: str) -> tuple[str, str]:
    """Parse a selector string in the format
    ``{selection_method}:{selector}``. If no selection method is specified,
    it will be inferred from the selector itself, by using the following rule:
    if ``selector`` starts with ``/`` or ``./`` then it is a XPath selector,
    otherwise, it is a CSS selector.

    .. warning:: :py:mod:`~manen` will only try to guess if this is a XPath
        or CSS selectors, no more.

    Example::

        >>> parse_selector('css:h1.title')
        ('css selector', 'h1.title')
        >>> parse_selector('a')
        ('css selector', 'a')
        >>> parse_selector('tag:span')
        ('tag name', 'span')
        >>> parse_selector('/div/p/span[@class="r"]')
        ('xpath', '/div/p/span[@class="r"]')

    Args:
        selector (str): selector in the format ``{selection_method}:{selector}``

    Returns:
        Tuple[str, str]: Selenium selector in the format
        ``(selection_method, selector)``
    """
    if any(selector.startswith(f"{method}:") for method in METHODS_MAPPER):
        selection_method, sel = selector.split(":", 1)
        return METHODS_MAPPER[selection_method], sel
    if selector.startswith("/") or selector.startswith("./"):
        return By.XPATH, selector
    return By.CSS_SELECTOR, selector


@overload
def find(
    selector: None = None,
    *,
    inside: DriverOrElement | list[DriverOrElement] | None,
    many: bool = False,
    default: Any = NotImplemented,
    wait: int = 0,
) -> partial: ...


@overload
def find(
    selector: str | list[str],
    *,
    inside: DriverOrElement,
    many: Literal[False] = False,
    default: Any = NotImplemented,
    wait: int = 0,
) -> WebElement: ...


@overload
def find(
    selector: str | list[str],
    *,
    inside: DriverOrElement,
    many: Literal[True] = True,
    default: Any = NotImplemented,
    wait: int = 0,
) -> list[WebElement]: ...


@overload
def find(
    selector: str | list[str],
    *,
    inside: list[DriverOrElement],
    many: Literal[False] = False,
    default: Any = NotImplemented,
    wait: int = 0,
) -> list[WebElement]: ...


@overload
def find(
    selector: str | list[str],
    *,
    inside: list[DriverOrElement],
    many: Literal[True] = True,
    default: Any = NotImplemented,
    wait: int = 0,
) -> list[list[WebElement]]: ...


def find(
    selector: str | list[str] | None = None,
    *,
    inside: DriverOrElement | list["DriverOrElement"] | None = None,
    many: bool = False,
    default: Any = NotImplemented,
    wait: int = 0,
):
    """Retrieve DOM elements from Selenium WebElements matching selector.
    The function is highly customizable in order to match the different
    scenarios you may have when retrieving elements from HTML source code.
    For example, you can:

    - try with one or multiple selectors, with several selection methods (XPath,
      CSS, tag...)
    - return one or several elements
    - wait to an element appears
    - return a default value or raises an error
    - search in the whole page or in one or several specific areas

    The supported selection methods are:

    +--------------------------------------+-------------------------------------------------------------+
    | Selection Method                     | Selection Engine                                            |
    +======================================+=============================================================+
    | ``xpath``, ``xp``                    | XPath (can be inferred if no selection method is specified) |
    +--------------------------------------+-------------------------------------------------------------+
    | ``css``                              | CSS                                                         |
    +--------------------------------------+-------------------------------------------------------------+
    | ``class_name``, ``class``, ``cls``   | Class Name (but Selenium is the CSS method behind)          |
    +--------------------------------------+-------------------------------------------------------------+
    | ``id``                               | ID (but Selenium is the CSS method behind)                  |
    +--------------------------------------+-------------------------------------------------------------+
    | ``link_text``, ``link``              | Link Text                                                   |
    +--------------------------------------+-------------------------------------------------------------+
    | ``name``                             | Name attribute                                              |
    +--------------------------------------+-------------------------------------------------------------+
    | ``tag_name``, ``tag``                | Tag Name                                                    |
    +--------------------------------------+-------------------------------------------------------------+
    | ``partial_link_text``, ``plink``     | Partial Link Text                                           |
    +--------------------------------------+-------------------------------------------------------------+

    The selector should use the pattern ``{selection_method}:{selector}`` to be
    correctly understood. Because it uses behind the scene
    :py:func:`~manen.finder.parse_selector`, :py:mod:`~manen` will infer the
    selection method if none is specified (if the selector starts with ``/`` or
    ``./`` then XPath is inferred otherwise it will be seen as a CSS selector).

    Another feature of this function is that it offers a way to use functional
    programming to re-use the function with some parameters. If ``selector``
    is not specified, it will return a partial function which can be used
    later. See example below for better understanding.

    Example::

        >>> divs = find(['div.tryClass1', 'div.tryClass2'], many=True, wait=3, inside=driver)
        [<selenium.webdriver.remote.webelement.WebElement (session: "1", element: "a1")>,
         <selenium.webdriver.remote.webelement.WebElement (session: "1", element: "a3")>,
         <selenium.webdriver.remote.webelement.WebElement (session: "1", element: "a3")>]
        >>> links = find('a', many=False, default=None, inside=divs)
        [<selenium.webdriver.remote.webelement.WebElement (session: "1", element: "b1")>,
         None,
         <selenium.webdriver.remote.webelement.WebElement (session: "1", element: "b2")>]
        >>> lookup = find(inside=driver, default=None, many=True)
        >>> lookup(['p.tryMe', 'p.orTryMe'])
        [<selenium.webdriver.remote.webelement.WebElement (session: "1", element: "b1")>,
         <selenium.webdriver.remote.webelement.WebElement (session: "1", element: "b2")>,
         <selenium.webdriver.remote.webelement.WebElement (session: "1", element: "b3")>,
         <selenium.webdriver.remote.webelement.WebElement (session: "1", element: "b4")>]


    Args:
        selector (str or List[str], optional): Selectors to be used to find the
            element(s). If it is a list, it will try each selector until at
            least one element is found. If it is ``None``, it returns a partial
            function which can be used later to find the elements. Defaults to
            ``None``.
        wait (int, optional): If ``wait`` > 0 and no element is currently found,
            the function will retry every 500ms, for ``wait`` seconds maximum.
            Defaults to 0.
        default (Any, optional): default value to return if no element is found.
            Specifying this value will prevent the function to raise
            :py:exc:`manen.exceptions.ElementNotFound` if no element matching
            the selectors are found.
            Defaults to ``NotImplemented``.
        inside (SeleniumElement, optional): where to find the element(s).
            Specifying this argument will restrict the search area. If
            ``None``, it will search the whole page. If it's a list, the
            function will map over each element of that list. Defaults to
            ``None``.
        many (bool, optional): Whether to return a single element or all the
            elements matching the selectors. Defaults to ``False``.

    Raises:
        ValueError: raised if the function is called with ``selector`` but
            without ``inside``.
        ElementNotFound: raised if no default value is specified and no element
            matching the selector(s) has been found

    Returns:
        Any: as explained in the Arguments description, the return value(s) will
        depend of the type of the arguments. Here is a recap of what will be
        returned based on the arguments types (``ans_elt`` is a Selenium
        element).

        +--------------------+---------------------+-----------+------------------------------------------------+
        | `default`          | `inside`            | `many`    | Examples                                       |
        +====================+=====================+===========+================================================+
        | ``NotImplemented`` | ``None``            | ``False`` | ``ans_elt``                                    |
        +--------------------+---------------------+-----------+------------------------------------------------+
        | ``NotImplemented`` | ``None``            | ``True``  | ``[ans_elt1, ans_elt2]``                       |
        +--------------------+---------------------+-----------+------------------------------------------------+
        | ``None``           | ``[el1, el2, el3]`` | ``False`` | ``[ans_elt11, None, ans_elt_31]``              |
        +--------------------+---------------------+-----------+------------------------------------------------+
        | ``[]``             | ``[el1, el2, el3]`` | ``True``  | ``[[ans_elt11, ans_elt12], [], [ans_elt_31]]`` |
        +--------------------+---------------------+-----------+------------------------------------------------+
    """
    if selector is None:
        return partial(find, wait=wait, default=default, inside=inside, many=many)

    if inside is None:
        raise ValueError("You must specify `inside` if you specify `selector`")

    if isinstance(inside, list):
        return [
            find(selector, inside=element, default=default, wait=wait, many=many)  # type: ignore
            for element in inside
        ]

    selectors = [selector] if not isinstance(selector, list) else selector
    finder = inside.find_elements if many else inside.find_element

    def try_several_selectors(selectors, fn_find):
        for selector in selectors:
            selenium_selector = parse_selector(selector)
            try:
                elements = fn_find(*selenium_selector)
            except NoSuchElementException:
                elements = None
            if elements:
                return elements
        return None

    if wait:
        try:
            found_elements = poll(
                try_several_selectors,
                args=(selectors, finder),
                step=0.5,
                timeout=wait,
            )
        except PollTimeoutException:
            found_elements = None
    else:
        found_elements = try_several_selectors(selectors, finder)

    if found_elements:
        return found_elements

    if default != NotImplemented:
        return default

    driver = inside if isinstance(inside, WebDriver) else inside.parent
    raise ElementNotFound(selectors=selectors, driver=driver)
