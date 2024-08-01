from enum import Enum
from typing import Annotated, NewType


class Flag(str, Enum):
    INPUT = "INPUT"
    CHECKBOX = "CHECKBOX"


Checkbox = Annotated[bool, Flag.CHECKBOX]
HRef = NewType("HRef", str)
ImageSrc = NewType("ImageSrc", str)
InnerHTML = NewType("InnerHTML", str)
OuterHTML = NewType("OuterHTML", str)
Input = Annotated[str, Flag.INPUT]
