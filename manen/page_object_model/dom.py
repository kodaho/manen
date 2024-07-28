from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Any, NewType, get_origin


@dataclass
class XPath:
    selector: str


@dataclass
class CSS:
    selector: str


@dataclass
class LinkText:
    selector: str


@dataclass
class PartialLinkText:
    selector: str


@dataclass
class Wait:
    seconds: int


@dataclass
class Default:
    value: Any


class Flag(str, Enum):
    INPUT = "INPUT"


@dataclass
class Config:
    name: str
    element_type: type
    selectors: list[str]
    wait: int
    default: Any = NotImplemented
    many: bool = False
    is_input: bool = False

    @classmethod
    def merge(cls, configs, **kwargs):
        selectors = []
        wait = None
        default = NotImplemented
        is_input = False
        for config in configs:
            if isinstance(config, cls):
                selectors.extend(config.selectors)
                wait = config.wait
                default = config.default
            elif isinstance(config, XPath):
                selectors.append(f"xpath:{config.selector}")
            elif isinstance(config, CSS):
                selectors.append(f"css:{config.selector}")
            elif isinstance(config, LinkText):
                selectors.append(f"link_text:{config.selector}")
            elif isinstance(config, PartialLinkText):
                selectors.append(f"partial_link_text:{config.selector}")
            elif isinstance(config, Wait):
                wait = config.seconds
            elif isinstance(config, Default):
                default = config.value
            elif config == Flag.INPUT:
                is_input = True
            else:
                raise ValueError(f"Unknown config type: {config}")
        return cls(
            selectors=selectors,
            wait=wait or 0,
            default=default,
            is_input=is_input,
            **kwargs,
        )

    @classmethod
    def from_annotation_item(cls, field, annotation):
        origin = get_origin(type_ := annotation.__origin__)
        kwargs = {"name": field}
        if origin is list:
            kwargs.update({"element_type": type_.__args__[0], "many": True})
        else:
            kwargs.update({"element_type": type_, "many": False})
        return cls.merge(annotation.__metadata__, **kwargs)


Checkbox = NewType("Checkbox", str)
HRef = NewType("HRef", str)
ImageSrc = NewType("ImageSrc", str)
InnerHTML = NewType("InnerHTML", str)
OuterHTML = NewType("OuterHTML", str)
Input = Annotated[str, Flag.INPUT]
