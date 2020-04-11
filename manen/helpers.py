"""Helpers functions."""

import re
from collections import namedtuple
from platform import platform

from .exceptions import ManenException, PlatformNotRecognized

ZIP_UNIX_SYSTEM = 3

Platform = namedtuple("Platform", "system information")


def get_current_platform() -> "Platform":
    sys_platform = platform()
    if "darwin" in sys_platform.lower() or "macos" in sys_platform.lower():
        return Platform("MAC", sys_platform)
    elif "windows" in sys_platform.lower():
        return Platform("WIN", sys_platform)
    elif "linux" in sys_platform.lower():
        return Platform("LINUX", sys_platform)
    raise PlatformNotRecognized(sys_platform)


def extract_integer(string: str) -> int:
    string = re.sub(r"[\s,]", "", string)
    match = re.compile(r"(?P<figure>[\d]+)").search(string)
    if match:
        return int(match.group("figure"))
    raise ManenException("No figure detected in %s" % string)


PLATFORM = get_current_platform()
