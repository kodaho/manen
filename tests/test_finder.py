from functools import partial

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from manen.exceptions import ElementNotFound
from manen.finder import find, parse_selector


@pytest.mark.parametrize(
    "selector,expected_selection_method",
    [
        ("class_name:article-body", (By.CLASS_NAME, "article-body")),
        ("class:article-body", (By.CLASS_NAME, "article-body")),
        ("cls:article-body", (By.CLASS_NAME, "article-body")),
        ("css:div.article", (By.CSS_SELECTOR, "div.article")),
        ("id:username", (By.ID, "username")),
        ("link_text:Next Page", (By.LINK_TEXT, "Next Page")),
        ("link:pypi.org", (By.LINK_TEXT, "pypi.org")),
        ("name:search-bar", (By.NAME, "search-bar")),
        ("partial_link_text:Next P", (By.PARTIAL_LINK_TEXT, "Next P")),
        ("plink:Next P", (By.PARTIAL_LINK_TEXT, "Next P")),
        ("tag_name:span", (By.TAG_NAME, "span")),
        ("tag:span", (By.TAG_NAME, "span")),
        ("xp:/body/div/span", (By.XPATH, "/body/div/span")),
        ("xpath:/body/div/span", (By.XPATH, "/body/div/span")),
    ],
)
def test_parse_selector(selector, expected_selection_method):
    selection_method = parse_selector(selector)
    assert selection_method == expected_selection_method


@pytest.mark.parametrize(
    "selector,expected_selection_method",
    [
        ("/body/div/span", (By.XPATH, "/body/div/span")),
        ("./body/div/span", (By.XPATH, "./body/div/span")),
        ("div.article", (By.CSS_SELECTOR, "div.article")),
        (".article", (By.CSS_SELECTOR, ".article")),
    ],
)
def test_parse_selector_with_inference(selector, expected_selection_method):
    selection_method = parse_selector(selector)
    assert selection_method == expected_selection_method


# --- find ---


class FakeElement:
    """Stand-in for a Selenium element with scriptable lookup behaviour.

    ``found_for`` maps a (by, value) pair to the list returned for
    ``find_elements`` / the first element returned for ``find_element``.
    Any selector not present in the mapping raises ``NoSuchElementException``
    (mirroring real Selenium).
    """

    def __init__(self, found_for=None, label="element"):
        self.found_for = found_for or {}
        self.label = label
        self.parent = None

    def find_element(self, by, value):
        matches = self.found_for.get((by, value))
        if not matches:
            raise NoSuchElementException(f"No element for ({by!r}, {value!r})")
        return matches[0]

    def find_elements(self, by, value):
        return self.found_for.get((by, value), [])

    def __repr__(self):
        return f"FakeElement({self.label!r})"


class FakeDriver(FakeElement, WebDriver):
    """Bypasses ``WebDriver.__init__`` (which would try to open a real
    session) while still satisfying ``isinstance(x, WebDriver)`` checks."""

    def __init__(self, found_for=None, label="driver"):
        FakeElement.__init__(self, found_for=found_for, label=label)
        # Intentionally skip WebDriver.__init__.

    title = "Fake page"
    current_url = "https://example.test/"


def test_find_without_selector_returns_partial():
    """Calling ``find`` with no selector must return a ``functools.partial``
    that can be invoked later with a selector."""
    looked_up = find(inside=FakeDriver(found_for={(By.CSS_SELECTOR, "a"): [FakeElement()]}))
    assert isinstance(looked_up, partial)
    result = looked_up("a", many=True)
    assert len(result) == 1


def test_find_without_inside_raises_value_error():
    """If a selector is given but ``inside`` is None, ``find`` must raise
    ``ValueError`` rather than silently returning something meaningless."""
    with pytest.raises(ValueError, match="inside"):
        find("h1", inside=None)


def test_find_with_list_of_containers_maps_over_each():
    """When ``inside`` is a list, ``find`` should return one result per
    container (mapped lookup)."""
    el1 = FakeElement(found_for={(By.CSS_SELECTOR, "span"): [FakeElement(label="a")]})
    el2 = FakeElement(found_for={(By.CSS_SELECTOR, "span"): [FakeElement(label="b")]})
    result = find("span", inside=[el1, el2], many=False)
    assert len(result) == 2
    assert result[0].label == "a"
    assert result[1].label == "b"


def test_find_tries_each_selector_until_match():
    """Given a list of selectors, ``find`` must try them in order and
    return the first non-empty match."""
    target = FakeElement(label="target")
    inside = FakeElement(
        found_for={(By.CSS_SELECTOR, "div.real"): [target]},
    )
    # First two selectors miss, third matches.
    result = find(["css:div.missing-1", "css:div.missing-2", "css:div.real"], inside=inside)
    assert result is target


def test_find_returns_default_when_nothing_found():
    """When no selector matches and ``default`` is set, ``find`` returns
    the default value (instead of raising)."""
    inside = FakeElement()
    sentinel = object()
    assert find("css:not-there", inside=inside, default=sentinel) is sentinel


def test_find_returns_default_when_no_such_element_raised():
    """``find_element`` raising ``NoSuchElementException`` must be caught
    so the default value is returned for non-list lookups."""
    inside = FakeElement()  # any lookup will raise
    assert find("css:missing", inside=inside, default=None, many=False) is None


def test_find_raises_element_not_found_when_no_default():
    """If no selector matches and no default is provided, ``find`` must
    raise :class:`ElementNotFound` with the attempted selectors and the
    driver as context."""
    driver = FakeDriver()
    with pytest.raises(ElementNotFound) as exc_info:
        find("css:missing", inside=driver)
    assert exc_info.value.selectors == ["css:missing"]
    assert exc_info.value.context["current_url"] == "https://example.test/"


def test_find_resolves_driver_from_element_parent_for_error():
    """When ``inside`` is a WebElement (not a WebDriver), the
    ``ElementNotFound`` error must reach back to ``element.parent`` to
    record the driver context."""
    driver = FakeDriver()
    nested = FakeElement()
    nested.parent = driver
    with pytest.raises(ElementNotFound) as exc_info:
        find("css:missing", inside=nested)
    assert exc_info.value.context["title"] == "Fake page"


def test_find_with_wait_returns_when_element_appears():
    """If the element appears within the wait window, ``find`` must return
    it without raising."""
    attempts = {"n": 0}
    target = FakeElement(label="late")

    class DelayedElement(FakeElement):
        def find_element(self, by, value):
            attempts["n"] += 1
            if attempts["n"] < 2:
                raise NoSuchElementException("not yet")
            return target

        def find_elements(self, by, value):
            attempts["n"] += 1
            return [target] if attempts["n"] >= 2 else []

    result = find("css:late", inside=DelayedElement(), wait=2, many=False)
    assert result is target
    assert attempts["n"] >= 2


def test_find_with_wait_timeout_returns_default():
    """When the wait elapses without a match and a default is set,
    ``find`` returns the default rather than raising."""
    inside = FakeElement()  # never matches
    sentinel = object()
    result = find(
        "css:never",
        inside=inside,
        wait=1,
        default=sentinel,
    )
    assert result is sentinel


def test_find_with_wait_timeout_and_no_default_raises():
    """When the wait elapses without a match and no default is set,
    ``find`` must raise :class:`ElementNotFound`."""
    driver = FakeDriver()
    with pytest.raises(ElementNotFound):
        find("css:never", inside=driver, wait=1)


def test_find_many_returns_list():
    """With ``many=True``, ``find`` should return the underlying list
    returned by ``find_elements``."""
    elements = [FakeElement(label=f"e{i}") for i in range(3)]
    inside = FakeElement(found_for={(By.CSS_SELECTOR, "li"): elements})
    result = find("li", inside=inside, many=True)
    assert result == elements
