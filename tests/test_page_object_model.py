from collections import namedtuple
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import yaml
from selenium.webdriver.common.by import By

from manen.page_object_model import (
    Element,
    Elements,
    InputElement,
    IntegerElement,
    LinkElements,
    Page,
    TextElement,
    TextElements,
    PageObjectLoader,
)

ExpectedResult = namedtuple("ExpectedResult", ("attr", "strategy", "selector"))


class TestElementInPage:
    @staticmethod
    def get_test_context(element_class):
        class ManenTestPage(Page):
            css = element_class("css:div")
            xpath = element_class("xpath://div")
            post_processing = element_class(
                "css:div", post_processing=lambda x: x.extract()
            )

        expected_results = (
            ExpectedResult(attr="css", strategy=By.CSS_SELECTOR, selector="div"),
            ExpectedResult(attr="xpath", strategy=By.XPATH, selector="//div"),
        )

        return ManenTestPage, expected_results

    def test_can_access_element_in_page(self):
        browser = MagicMock()
        page_class, expected_results = self.get_test_context(Element)
        page = page_class(browser)

        for attribute, strategy, selector in expected_results:
            _ = getattr(page, attribute)
            browser.find_element.assert_called_with(strategy, selector)
            browser.reset_mock()

    def test_can_access_elements_in_page(self):
        browser = MagicMock()
        page_class, expected_results = self.get_test_context(Elements)
        page = page_class(browser)

        for attribute, strategy, selector in expected_results:
            _ = getattr(page, attribute)
            browser.find_elements.assert_called_with(strategy, selector)
            browser.reset_mock()

    def test_can_acess_text_element_in_page(self):
        browser = MagicMock()
        mock_element, mock_text = MagicMock(), PropertyMock()
        type(mock_element).text = mock_text
        browser.find_element = MagicMock(return_value=mock_element)

        page_class, expected_results = self.get_test_context(TextElement)
        page = page_class(browser)

        for attribute, strategy, selector in expected_results:
            _ = getattr(page, attribute)
            browser.find_element.assert_called_with(strategy, selector)
            mock_text.assert_called_once()
            browser.reset_mock()
            mock_text.reset_mock()

    def test_can_acess_text_elements_in_page(self):
        browser = MagicMock()
        mock_element, mock_text = MagicMock(), PropertyMock()
        type(mock_element).text = mock_text
        browser.find_elements = MagicMock(return_value=mock_element)

        page_class, expected_results = self.get_test_context(TextElements)
        page = page_class(browser)

        for attribute, strategy, selector in expected_results:
            _ = getattr(page, attribute)
            browser.find_elements.assert_called_with(strategy, selector)
            mock_text.assert_called_once()
            browser.reset_mock()
            mock_text.reset_mock()

    def test_can_set_input_in_page(self):
        class ManenTestPage(Page):
            email = InputElement("css:input[name='email']")

        browser = MagicMock()
        page = ManenTestPage(browser)
        page.email = "this is a test"

        browser.find_element.assert_called_with(By.CSS_SELECTOR, "input[name='email']")
        browser.find_element.return_value.send_keys.assert_called_with("this is a test")

    def test_can_get_input_in_page(self):
        class ManenTestPage(Page):
            email = InputElement("css:input[name='email']")

        browser = MagicMock()
        page = ManenTestPage(browser)
        _ = page.email

        browser.find_element.assert_called_with(By.CSS_SELECTOR, "input[name='email']")
        browser.find_element.return_value.get_attribute.assert_called_with("value")


class TestLoadPage:
    def test_load_page_objects_from_yaml(self):
        page_path = Path(__file__).parent / "assets/page.yaml"
        with page_path.open(mode="r") as page_file:
            page = yaml.load(page_file, Loader=PageObjectLoader)
        page_objects = page["elements"]
        assert isinstance(page_objects["name"], TextElement)
        assert page_objects["name"].selectors == ["p.name", "span.name"]
        assert isinstance(page_objects["links"], LinkElements)
        assert isinstance(page_objects["description"], TextElement)
        assert isinstance(page_objects["age"], IntegerElement)
        assert isinstance(page_objects["button_validate"], Element)
        assert isinstance(page_objects["login"], InputElement)
