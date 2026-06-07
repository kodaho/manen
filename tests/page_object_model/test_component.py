"""Tests covering :py:class:`~manen.page_object_model.component.Component` and
:py:class:`~manen.page_object_model.component.Page` instantiation.

These tests exist primarily to guard against a regression where
``self.__annotations__`` would raise ``AttributeError`` on Python 3.14
(see PEP 749 — deferred annotations make instance-level access fail).
"""

from typing import Annotated

import pytest
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model.component import Component, Page
from manen.page_object_model.config import CSS
from manen.page_object_model.dom_value import ConfigurableDOM
from manen.page_object_model.exceptions import MissingAnnotationError


class FakeElement:
    """Minimal stand-in for a Selenium ``WebElement`` for descriptor tests."""

    def __init__(self, text="value", children=None):
        self._text = text
        self._children = children or []
        self.parent = None

    @property
    def text(self):
        return self._text

    def get_attribute(self, name):
        return self._text

    def find_element(self, by, value):
        return FakeElement(self._text)

    def find_elements(self, by, value):
        return self._children or [FakeElement(self._text)]


class FakeDriver(FakeElement):
    title = "Fake Page"
    current_url = "https://example.test/"
    page_source = "<html></html>"


def test_page_instantiation_with_annotations():
    """Regression test: ``Page(driver)`` must work on Python 3.14+.

    Previously the constructor used ``self.__annotations__`` which is no longer
    accessible via instance attribute lookup since PEP 749.
    """

    class HomePage(Page):
        title_text: Annotated[str, CSS("h1")]

    page = HomePage(FakeDriver())
    assert "title_text" in page._config
    assert page._config["title_text"].selectors == ["css:h1"]


def test_component_instantiation_with_annotations():
    class MyComponent(Component):
        name: Annotated[str, CSS("span.name")]

    component = MyComponent(FakeElement())
    assert "name" in component._config


def test_page_with_nested_component():
    class MyPage(Page):
        class Item(Component):
            name: Annotated[str, CSS("h3")]

        items: Annotated[list[Item], CSS("li")]

    driver = FakeDriver()
    page = MyPage(driver)
    assert "items" in page._config
    assert page._config["items"].many
    assert page._config["items"].element_type is MyPage.Item


def test_page_with_no_annotations():
    """A Page with no fields should still instantiate without error."""

    class EmptyPage(Page):
        pass

    page = EmptyPage(FakeDriver())
    assert page._config == {}


def test_page_webelement_field():
    class MyPage(Page):
        button: Annotated[WebElement, CSS("button")]

    page = MyPage(FakeDriver())
    assert page._config["button"].element_type is WebElement


def test_multiple_instances_share_descriptors():
    """Constructing two instances of the same Page class should not error."""

    class MyPage(Page):
        title_text: Annotated[str, CSS("h1")]

    page1 = MyPage(FakeDriver())
    page2 = MyPage(FakeDriver())
    assert page1._config["title_text"].selectors == page2._config["title_text"].selectors


@pytest.mark.parametrize("page_cls_name", ["HomePage", "SearchResultPage", "DashboardPage"])
def test_page_class_instantiation_variants(page_cls_name):
    """Build a Page class dynamically to ensure ``get_annotations`` works
    regardless of the class definition site."""

    page_cls = type(
        page_cls_name,
        (Page,),
        {"__annotations__": {"value": Annotated[str, CSS("div")]}},
    )

    page = page_cls(FakeDriver())
    assert "value" in page._config


# --- Issue #5: descriptors built once per class, not per instance --- #


def test_descriptors_built_at_class_definition_not_instantiation():
    """Regression test: descriptors must be installed when the class is
    defined (via ``__init_subclass__``), not on every ``__init__`` call.

    Verifies that ``MyPage.title_text`` resolves to a descriptor *before*
    any instance is created.
    """

    class MyPage(Page):
        title_text: Annotated[str, CSS("h1")]

    descriptor = MyPage.__dict__["title_text"]
    assert isinstance(descriptor, ConfigurableDOM)
    assert descriptor.config.selectors == ["css:h1"]


def test_class_config_is_not_rebuilt_on_each_instance():
    """The descriptor object on the class must remain identical across
    multiple instantiations (it should be the same object, not a fresh one
    written on each ``__init__`` call)."""

    class MyPage(Page):
        title_text: Annotated[str, CSS("h1")]

    descriptor_before = MyPage.__dict__["title_text"]
    MyPage(FakeDriver())
    MyPage(FakeDriver())
    MyPage(FakeDriver())
    descriptor_after = MyPage.__dict__["title_text"]

    assert descriptor_before is descriptor_after


def test_config_dict_shared_across_instances():
    """``_config`` is now a class attribute set in ``__init_subclass__``;
    all instances of the same class should see the same mapping object."""

    class MyPage(Page):
        title_text: Annotated[str, CSS("h1")]

    page1 = MyPage(FakeDriver())
    page2 = MyPage(FakeDriver())
    assert page1._config is page2._config


def test_sibling_page_classes_have_independent_config():
    """Each subclass must have its own ``_config`` — defining a second Page
    must not leak into the first one's configuration."""

    class PageA(Page):
        a_field: Annotated[str, CSS("h1.a")]

    class PageB(Page):
        b_field: Annotated[str, CSS("h1.b")]

    assert set(PageA._config) == {"a_field"}
    assert set(PageB._config) == {"b_field"}
    assert PageA._config is not PageB._config


# --- Issue #6: clear error when a field is not Annotated --- #


def test_missing_annotation_raises_meaningful_error():
    """Regression test: declaring a field without ``Annotated[...]`` must
    raise :class:`MissingAnnotationError` (not a cryptic
    ``AttributeError: 'str' object has no attribute '__origin__'``)."""

    with pytest.raises(MissingAnnotationError) as exc_info:
        class BrokenPage(Page):  # noqa: F841
            title_text: str

    assert exc_info.value.field == "title_text"
    assert exc_info.value.annotation is str
    assert "Annotated" in str(exc_info.value)
    assert "title_text" in str(exc_info.value)


def test_missing_annotation_error_is_typeerror():
    """``MissingAnnotationError`` must subclass ``TypeError`` so users who
    catch the standard exception type still catch it."""

    with pytest.raises(TypeError):
        class BrokenPage(Page):  # noqa: F841
            value: int


@pytest.mark.parametrize(
    "annotation",
    [int, str, list[str], dict[str, int], None],
)
def test_non_annotated_field_types_all_rejected(annotation):
    """A variety of non-``Annotated`` field types must all be rejected
    with the same meaningful error."""

    with pytest.raises(MissingAnnotationError):
        type(
            "TmpPage",
            (Page,),
            {"__annotations__": {"field": annotation}},
        )


# --- Issue #3: DOMSection/DOMSections preserve the original element_type --- #


def test_dom_section_isinstance_preserves_user_type():
    """Regression test: a single nested Component returned by ``DOMSection``
    must be an instance of the user-declared class, not a structurally-cloned
    look-alike with different identity."""

    class MyPage(Page):
        class Sidebar(Component):
            title: Annotated[str, CSS("h2")]

        sidebar: Annotated[Sidebar, CSS("aside")]

    page = MyPage(FakeDriver())
    assert isinstance(page.sidebar, MyPage.Sidebar)
    assert isinstance(page.sidebar, Component)


def test_dom_sections_isinstance_preserves_user_type():
    """Same as above for the list-valued ``DOMSections`` descriptor."""

    class MyPage(Page):
        class Item(Component):
            name: Annotated[str, CSS("h3")]

        items: Annotated[list[Item], CSS("li")]

    page = MyPage(FakeDriver())
    items = page.items
    assert len(items) > 0
    for item in items:
        assert isinstance(item, MyPage.Item)
        assert isinstance(item, Component)


def test_dom_section_returns_same_class_object():
    """The returned component's type must be the exact class the user
    defined (``is`` comparison), not a freshly-built clone with the
    same qualname."""

    class MyPage(Page):
        class Sidebar(Component):
            title: Annotated[str, CSS("h2")]

        sidebar: Annotated[Sidebar, CSS("aside")]

    page = MyPage(FakeDriver())
    assert type(page.sidebar) is MyPage.Sidebar


# --- Issue #4: subclasses inherit annotations from their parents --- #


def test_subclass_inherits_parent_annotations():
    """Regression test: a Page that subclasses another Page must also
    register the parent's annotated fields, not just its own."""

    class BasePage(Page):
        title_text: Annotated[str, CSS("h1")]

    class ChildPage(BasePage):
        body: Annotated[str, CSS("p")]

    assert "title_text" in ChildPage._config
    assert "body" in ChildPage._config


def test_subclass_inherits_descriptor_behaviour():
    """A field declared on the parent must still be accessible (via
    descriptor lookup) on instances of the child class."""

    class BasePage(Page):
        title_text: Annotated[str, CSS("h1")]

    class ChildPage(BasePage):
        body: Annotated[str, CSS("p")]

    page = ChildPage(FakeDriver())
    assert page.title_text == "value"
    assert page.body == "value"


def test_subclass_can_override_parent_annotation():
    """A child redeclaring a parent's field must take precedence in the
    merged ``_config``."""

    class BasePage(Page):
        title_text: Annotated[str, CSS("h1.base")]

    class ChildPage(BasePage):
        title_text: Annotated[str, CSS("h1.child")]

    assert ChildPage._config["title_text"].selectors == ["css:h1.child"]
    assert BasePage._config["title_text"].selectors == ["css:h1.base"]


def test_deep_inheritance_chain():
    """Annotations declared at each level of a multi-level chain must all
    end up in the leaf class's config."""

    class Level1(Page):
        a: Annotated[str, CSS(".a")]

    class Level2(Level1):
        b: Annotated[str, CSS(".b")]

    class Level3(Level2):
        c: Annotated[str, CSS(".c")]

    assert set(Level3._config) == {"a", "b", "c"}
    assert set(Level2._config) == {"a", "b"}
    assert set(Level1._config) == {"a"}


def test_parent_config_not_mutated_by_child():
    """Defining a child class must not modify the parent's ``_config``."""

    class BasePage(Page):
        title_text: Annotated[str, CSS("h1")]

    parent_fields_before = set(BasePage._config)

    class ChildPage(BasePage):  # noqa: F841
        extra: Annotated[str, CSS(".extra")]

    assert set(BasePage._config) == parent_fields_before
