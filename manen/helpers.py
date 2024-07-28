"""
:py:mod:`~manen.helpers`
========================

Helpers functions used by :py:mod:`manen`.
"""

import platform
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typing import Version


PLATFORM = platform.uname()


def extract_integer(string: str) -> int:
    """
    Extract an integer from a string.

    Args:
        string (str): text to process
    Raises:
        ValueError: Raised if no integer is found in the string.
    Returns:
        int: Integer extracted from the string
    """
    string = re.sub(r"[\s,]", "", string)
    match = re.compile(r"(?P<integer>[\d]+)").search(string)
    if match:
        return int(match.group("integer"))
    raise ValueError(f"No integer detected in {string}")


def version(version_str: str) -> "Version":
    """
    Helper function to convert a version string into a tuple. The versioning
    scheme is described `here <https://www.chromium.org/developers/version-numbers>`_.
    The input will be validated with the regular expression
    ``^[\\d]+.[\\d]+.[\\d]+.[\\d]+$`` and raised a :py:class:`ValueError` if it doesn't match.

    ..  caution::

        This versioning system is not compliant with semantic versioning rules.

    Args:
        version_str (str): string to be converted to a tuple

    Raises:
        ValueError: raised if the input doesn't match the pattern

    Returns:
        Version: parsed version
    """
    if not re.match(r"^[\d]+.[\d]+(.[\d]+)?(.[\d]+)?$", version_str):
        raise ValueError(
            f"The version `{version_str}` is not compatible with the pattern"
            " MAJOR.MINOR(.BRANCH)?.PATH."
        )
    splitted_version = tuple([int(s) for s in version_str.split(".")])
    return (
        splitted_version[0],
        splitted_version[1],
        splitted_version[2] if len(splitted_version) == 4 else None,
        splitted_version[-1] if len(splitted_version) >= 3 else None,
    )


def version_as_str(version_tuple: "Version", limit: int = 4) -> str:
    """
    Format a version tuple as a string in the format: {major}.{minor}.{build}.{patch}

    Args:
        version_tuple (Version): version info as a tuple
        limit (int, optional): Limit on the length of the tuple to format. Defaults to 4.

    Returns:
        str: formatted version
    """
    return ".".join(map(str, version_tuple[:limit]))
