"""Helpers functions used by :py:mod:`manen`."""

import re
from collections import namedtuple
from platform import platform

from .exceptions import PlatformNotRecognized

ZIP_UNIX_SYSTEM = 3

Platform = namedtuple("Platform", "system information")


def get_current_platform() -> "Platform":
    """Return the operating system and metadata about the current platform.
    The information will be wrapped in a ``Platform`` namedtuple.

    Returns:
        Platform: namedtuple with ``system`` and ``information`` attributes
            storing information about the platform running the code.
    """
    sys_platform = platform()
    if "darwin" in sys_platform.lower() or "macos" in sys_platform.lower():
        return Platform("MAC", sys_platform)
    elif "windows" in sys_platform.lower():
        return Platform("WIN", sys_platform)
    elif "linux" in sys_platform.lower():
        return Platform("LINUX", sys_platform)
    raise PlatformNotRecognized(sys_platform)


def extract_integer(string: str) -> int:
    """Extract an integer from a string.

    Args:
        string (str): text to process
    Raises:
        ValueError: exception raised if no integer were fonnd in the string.
    Returns:
        int: integer extracted from the string
    """
    string = re.sub(r"[\s,]", "", string)
    match = re.compile(r"(?P<figure>[\d]+)").search(string)
    if match:
        return int(match.group("figure"))
    raise ValueError("No figure detected in %s" % string)


PLATFORM = get_current_platform()
