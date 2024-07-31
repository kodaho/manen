from dataclasses import dataclass
from types import UnionType
from typing import Any, get_args, get_origin

from manen.page_object_model.dom import Flag

__all__ = ("CSS", "Default", "LinkText", "PartialLinkText", "Wait", "XPath")


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
            kwargs.update({"element_type": get_args(type_)[0], "many": True})
        elif origin is UnionType:
            kwargs.update({"element_type": get_args(type_)[0], "many": False})
        else:
            kwargs.update({"element_type": type_, "many": False})

        config = cls.merge(annotation.__metadata__, **kwargs)

        if len(config.selectors) == 0:
            raise ValueError(
                f"At least one selector should be specified in the annotation of '{field}'"
            )

        return config
