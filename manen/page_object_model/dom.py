from enum import Enum
from typing import Annotated, NewType


class Flag(str, Enum):
    INPUT = "INPUT"


Checkbox = NewType("Checkbox", str)
HRef = NewType("HRef", str)
ImageSrc = NewType("ImageSrc", str)
InnerHTML = NewType("InnerHTML", str)
OuterHTML = NewType("OuterHTML", str)
Input = Annotated[str, Flag.INPUT]
