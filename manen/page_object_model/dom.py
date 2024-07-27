from dataclasses import dataclass
from typing import Any, NewType, get_origin


@dataclass
class XPath:
    selector: str


@dataclass
class CSS:
    selector: str


@dataclass
class Wait:
    seconds: int


@dataclass
class Default:
    value: Any


@dataclass
class Config:
    name: str
    element_type: type
    selectors: list[str]
    wait: int
    default: Any = NotImplemented
    many: bool = False

    @classmethod
    def merge(cls, configs, **kwargs):
        selectors = []
        wait = None
        default = NotImplemented
        for config in configs:
            if isinstance(config, cls):
                selectors.extend(config.selectors)
                wait = config.wait
                default = config.default
            elif isinstance(config, (XPath, CSS)):
                selectors.append(config.selector)
            elif isinstance(config, Wait):
                wait = config.seconds
            elif isinstance(config, Default):
                default = config.value
            else:
                raise ValueError(f"Unknown config type: {config}")
        return cls(selectors=selectors, wait=wait or 0, default=default, **kwargs)

    @classmethod
    def from_annotation_item(cls, field, annotation):
        origin = get_origin(type_ := annotation.__origin__)
        kwargs = {"name": field}
        if origin is list:
            kwargs.update({"element_type": type_.__args__[0], "many": True})
        else:
            kwargs.update({"element_type": type_, "many": False})
        return cls.merge(annotation.__metadata__, **kwargs)


InnerHTML = NewType("InnerHTML", str)
OuterHTML = NewType("OuterHTML", str)
HRef = NewType("HRef", str)
ImageSrc = NewType("ImageSrc", str)
Input = NewType("Input", str)
Checkbox = NewType("Checkbox", str)
