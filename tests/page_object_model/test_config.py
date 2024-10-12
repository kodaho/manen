from datetime import date, datetime
from typing import Annotated

import pytest
from selenium.webdriver.remote.webelement import WebElement

from manen.page_object_model.component import Component
from manen.page_object_model.config import (
    CSS,
    Attribute,
    Config,
    DatetimeFormat,
    Default,
    LinkText,
    Wait,
    XPath,
)
from manen.page_object_model.exceptions import SelectorConfigError
from manen.page_object_model.types import checkbox, href, inner_html, outer_html, src


@pytest.mark.parametrize(
    "attribute,expected",
    [
        (href, "href"),
        (src, "src"),
        (inner_html, "innerHTML"),
        (outer_html, "outerHTML"),
    ],
)
def test_config_builtin_attribute(attribute, expected):
    config = Config.from_annotation_item("field", Annotated[attribute, CSS("a")])
    assert config.attribute == expected


@pytest.mark.parametrize(
    "attribute",
    ["title", "alt", "data-foo", "data-bar", "aRandom_attributeWeirdly_form@tte3d"],
)
def test_config_custom_attribute(attribute):
    config = Config.from_annotation_item(
        "field",
        Annotated[str, Attribute(attribute), CSS("a")],
    )
    assert config.attribute == attribute


@pytest.mark.parametrize("type_", [str, int, float, datetime, date, WebElement])
def test_config_type(type_):
    config = Config.from_annotation_item("field", Annotated[type_, CSS("a")])
    assert config.element_type == type_
    assert not config.many
    assert config.default is NotImplemented

    config = Config.from_annotation_item("field", Annotated[list[type_], CSS("a")])
    assert config.element_type == type_
    assert config.many
    assert config.default is NotImplemented

    config = Config.from_annotation_item("field", Annotated[type_ | None, CSS("a")])
    assert config.element_type == type_
    assert not config.many
    assert config.default is None


@pytest.mark.parametrize(
    "selector,expected",
    [
        (CSS("a"), ["css:a"]),
        (XPath("//b"), ["xpath://b"]),
        (LinkText("c"), ["link_text:c"]),
    ],
)
def test_config_selector(selector, expected):
    config = Config.from_annotation_item("field", Annotated[str, selector])
    assert config.selectors == expected


def test_config_no_default_value():
    config = Config.from_annotation_item("field", Annotated[str, CSS("a")])
    assert config.default == NotImplemented


@pytest.mark.parametrize(
    "value",
    [42, None, [], {}, "a", 3.14, datetime.now(), date.today()],
)
def test_config_with_default_value(value):
    config = Config.from_annotation_item(
        "field",
        Annotated[
            str, CSS("a"), Default(value)
        ],  # There is no validation that the default value is of the correct type
    )
    assert config.default == value


def test_config_flag_checkbox():
    config = Config.from_annotation_item("field", Annotated[checkbox, CSS("a")])
    assert config.is_checkbox


def test_config_no_selector():
    with pytest.raises(SelectorConfigError):
        Config.from_annotation_item("field", Annotated[str, Default("a")])


def test_config_wait():
    config = Config.from_annotation_item("field", Annotated[str, CSS("a"), Wait(10)])
    assert config.wait == 10


def test_config_with_component():
    class PageSection(Component):
        title: Annotated[str, CSS("p.title")]

    config = Config.from_annotation_item(
        "section",
        Annotated[list[PageSection], CSS("section")],
    )
    assert config.name == "section"
    assert config.element_type == PageSection
    assert config.many
    assert config.selectors == ["css:section"]


@pytest.mark.parametrize(
    "annotation,config",
    [
        (
            Annotated[
                datetime,
                DatetimeFormat("%Y-%m-%dT%H:%M:%S%z"),
                Attribute("datetime"),
                CSS("span.package-snippet__created time"),
            ],
            Config(
                name="field",
                element_type=datetime,
                selectors=["css:span.package-snippet__created time"],
                many=False,
                attribute="datetime",
                format="%Y-%m-%dT%H:%M:%S%z",
                wait=0,
            ),
        ),
        (
            Annotated[checkbox, CSS("input")],
            Config(
                name="field",
                element_type=bool,
                selectors=["css:input"],
                many=False,
                wait=0,
                is_checkbox=True,
            ),
        ),
        (
            Annotated[WebElement, CSS("label")],
            Config(
                name="field",
                element_type=WebElement,
                selectors=["css:label"],
                many=False,
                wait=0,
            ),
        ),
        (
            Annotated[float, CSS("span.country-area")],
            Config(
                name="field",
                element_type=float,
                selectors=["css:span.country-area"],
                many=False,
                wait=0,
            ),
        ),
    ],
)
def test_config_examples(annotation, config):
    assert Config.from_annotation_item("field", annotation) == config
