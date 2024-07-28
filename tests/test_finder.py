import pytest
from selenium.webdriver.common.by import By

from manen.finder import parse_selector


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
