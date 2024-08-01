from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from selenium.webdriver.remote.webelement import WebElement

__all__ = (
    "checkbox",
    "element",
    "href",
    "inner_html",
    "input_value",
    "outer_html",
    "src",
)


class Flag(str, Enum):
    INPUT = "INPUT"
    CHECKBOX = "CHECKBOX"


@dataclass
class Attribute:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)


checkbox = Annotated[bool, Flag.CHECKBOX]
element = WebElement
href = Annotated[str, Attribute("href")]
inner_html = Annotated[str, Attribute("innerHTML")]
input_value = Annotated[str, Flag.INPUT]
outer_html = Annotated[str, Attribute("outerHTML")]
src = Annotated[str, Attribute("src")]
