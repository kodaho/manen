from collections import namedtuple
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import yaml
from selenium.webdriver.common.by import By

import pytest
from manen.exceptions import ManenException
from manen.page_object_model import (
    DatetimeElement,
    DatetimeElements,
    Element,
    ImageSourceElement,
    ImageSourceElements,
    InnerHtmlElement,
    InputElement,
    IntegerElement,
    IntegerElements,
    LinkElement,
    LinkElements,
    Page,
    PageObjectLoader,
    Region,
    TextElement,
    TextElements,
)

ExpectedResult = namedtuple("ExpectedResult", ("attr", "strategy", "selector"))


@pytest.mark.parametrize(
    "element_class",
    [Element, TextElement, LinkElement, ImageSourceElement, InnerHtmlElement],
)
@pytest.mark.parametrize(
    "manen_selector,strategy,selector",
    [
        ("css:div", By.CSS_SELECTOR, "div"),
        ("div", By.CSS_SELECTOR, "div"),
        ("xpath://div", By.XPATH, "//div"),
        ("xp://div", By.XPATH, "//div"),
        ("//div", By.XPATH, "//div"),
        (".//div", By.XPATH, ".//div"),
        ("./div", By.XPATH, "./div"),
        ("class_name:my-class", By.CLASS_NAME, "my-class"),
        ("class:my-class", By.CLASS_NAME, "my-class"),
        ("cls:my-class", By.CLASS_NAME, "my-class"),
        ("tag_name:a", By.TAG_NAME, "a"),
        ("tag:a", By.TAG_NAME, "a"),
        ("partial_link_text:a", By.PARTIAL_LINK_TEXT, "a"),
        ("plink:a", By.PARTIAL_LINK_TEXT, "a"),
        ("id:a", By.ID, "a"),
    ],
)
def test_choose_right_selection_method_for_element(
    element_class, manen_selector, strategy, selector
):
    class ManenTestPage(Page):
        attr = element_class(manen_selector)

    browser = MagicMock()
    page = ManenTestPage(browser)
    _ = page.attr
    browser.find_element.assert_called_once_with(strategy, selector)


@pytest.mark.parametrize(
    "element_class,text_value,expected_value",
    [
        (TextElement, "this is a text", "this is a text"),
        (IntegerElement, "3 values", 3),
        (DatetimeElement, "2020/05/01 at 12:00", datetime(2020, 5, 1, 12, 00)),
    ],
)
def test_post_processing_of_text_element(element_class, text_value, expected_value):
    class ManenTestPage(Page):
        attr = element_class("selector")

    browser = MagicMock()
    mock_element, mock_text = MagicMock(), PropertyMock(return_value=text_value)
    type(mock_element).text = mock_text
    browser.find_element = MagicMock(return_value=mock_element)
    page = ManenTestPage(browser)
    assert page.attr == expected_value


@pytest.mark.parametrize(
    "element_class,values,expected_values",
    [
        (
            TextElements,
            ["this is a text", "this is an other one", "and a last one"],
            ["this is a text", "this is an other one", "and a last one"],
        ),
        (
            IntegerElements,
            ["3 values", "2 values", "just 1 value", "and 10,000 others"],
            [3, 2, 1, 10000],
        ),
        (DatetimeElements, ["2020/05/01 at 12:00"], [datetime(2020, 5, 1, 12, 00)]),
    ],
)
def test_post_processing_of_text_elements(element_class, values, expected_values):
    class ManenTestPage(Page):
        attr = element_class("selector")

    browser = MagicMock()
    find_elements_returned_value = []
    for value in values:
        mock_element, mock_text = MagicMock(), PropertyMock(return_value=value)
        type(mock_element).text = mock_text
        find_elements_returned_value.append(mock_element)
    browser.find_elements = MagicMock(return_value=find_elements_returned_value)
    page = ManenTestPage(browser)
    assert page.attr == expected_values


@pytest.mark.parametrize(
    "element_class,attribute,value",
    [
        (ImageSourceElement, "src", "http://www.example.com/assets/img.jpg"),
        (LinkElement, "href", "http://www.example.com"),
        (InputElement, "value", "email@manen.co"),
    ],
)
def test_post_processing_of_element_with_attribute(element_class, attribute, value):
    class ManenTestPage(Page):
        attr = element_class("selector")

    browser = MagicMock()
    browser.find_element.return_value.get_attribute.return_value = value
    page = ManenTestPage(browser)
    assert page.attr == value
    browser.find_element.return_value.get_attribute.assert_called_once_with(attribute)


@pytest.mark.parametrize(
    "element_class,attribute,values",
    [
        (ImageSourceElements, "src", ["http://www.example.com/assets/img.jpg"]),
        (LinkElements, "href", ["http://www.example.com"]),
    ],
)
def test_post_processing_of_elements_with_attribute(element_class, attribute, values):
    class ManenTestPage(Page):
        attr = element_class("selector")

    browser = MagicMock()
    browser.find_elements.return_value = []
    for value in values:
        element = MagicMock()
        element.get_attribute.return_value = value
        browser.find_elements.return_value.append(element)
    page = ManenTestPage(browser)
    assert page.attr == values
    for element in browser.find_elements.return_value:
        element.get_attribute.assert_called_once_with(attribute)


class TestElementInPage:
    def test_can_set_input_in_page(self):
        class ManenTestPage(Page):
            email = InputElement("css:input[name='email']")

        browser = MagicMock()
        page = ManenTestPage(browser)
        page.email = "this is a test"

        browser.find_element.assert_called_with(By.CSS_SELECTOR, "input[name='email']")
        browser.find_element.return_value.send_keys.assert_called_with("this is a test")


def test_load_page_objects_from_yaml():
    page_path = Path(__file__).parent / "assets/page.yaml"
    with page_path.open(mode="r") as page_file:
        page = yaml.load(page_file, Loader=PageObjectLoader)
    page_objects = page["elements"]
    assert isinstance(page_objects["name"], TextElement)
    assert page_objects["name"]._selectors == ["p.name", "span.name"]
    assert isinstance(page_objects["links"], LinkElements)
    assert isinstance(page_objects["description"], TextElement)
    assert isinstance(page_objects["age"], IntegerElement)
    assert isinstance(page_objects["button_validate"], Element)
    assert isinstance(page_objects["login"], InputElement)


def test_page_with_external_selectors():
    class MyPage(Page):
        class Meta:
            selectors = {
                "elements": {
                    "h1_title": "h1.title",
                    "button": ".//button",
                    "my_region": {
                        "selectors": "div.region",
                        "elements": {
                            "name": "span.name",
                            "my_subregion": {
                                "selectors": ["div.subregion", "div.other-choice"],
                                "elements": {"description": "p"},
                            },
                        },
                    },
                }
            }

        class MyRegion(Region):
            class MySubRegion(Region):
                description = TextElement()

            name = Element()
            subtitle = TextElement()
            my_subregion = MySubRegion()

        h1_title = TextElement()
        button = Element()
        my_region = MyRegion()

    browser = MagicMock()
    page = MyPage(browser)

    _ = page.h1_title
    browser.find_element.assert_called_once_with(By.CSS_SELECTOR, "h1.title")
    browser.reset_mock()

    _ = page.button
    browser.find_element.assert_called_with(By.XPATH, ".//button")
    browser.reset_mock()

    _ = page.my_region
    browser.find_element.assert_called_with(By.CSS_SELECTOR, "div.region")

    _ = page.my_region.name
    _ = page.my_region.my_subregion.description

    with pytest.raises(ManenException):
        assert page.my_region.subtitle
