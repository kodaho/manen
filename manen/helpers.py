"""
manen.helpers
=============

Helpers functions used by :py:mod:`manen`.
"""

import platform
import re
import zipfile
from os import chmod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typing import Version


PLATFORM = platform.uname()
ZIP_UNIX_SYSTEM = 3


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


def version(version_str: str) -> "Version":
    """
    Helper function to convert a version string into a tuple. The versioning
    scheme is described `here <https://www.chromium.org/developers/version-numbers>`_.
    The input will be validated with the regular expression
    ``^[\\d]+.[\\d]+.[\\d]+.[\\d]+$`` and raised a :py:class:`ValueError` if it doesn't match.

    ..  caution::

        This versioning system is not compliant with semantic versioning rules.

    Args:
        version_str: string to be converted to a tuple
    Raises:
        ValueError: raised if the input doesn't match the pattern
    Returns:
        Tuple[int, int, Optional[int], int]: parsed version
    """
    if not re.match(r"^[\d]+.[\d]+.[\d]+(.[\d]+)?$", version_str):
        raise ValueError(
            f"The version `{version_str}` is not compatible with the pattern"
            " MAJOR.MINOR(.BRANCH)?.PATH."
        )
    splitted_version = tuple([int(s) for s in version_str.split(".")])
    return (
        splitted_version[0],
        splitted_version[1],
        splitted_version[2] if len(splitted_version) == 4 else None,
        splitted_version[-1],
    )


def version_as_str(version_tuple: "Version", limit: int = 4) -> str:
    """Format a version tuple as a string in the format:
        {major}.{minor}.{build}.{patch}


    Args:
        version_tuple (Version): version info as a tuple
        limit (int, optional): Limit on the length of the tuple to format.
            Defaults to 4.

    Returns:
        str: formatted version
    """
    return ".".join(map(str, version_tuple[:limit]))


def extract(archive_path: str):
    """Uncompress a file in an archive.

    Args:
        archive_path (str): path where to find the archive

    Returns:
        str: path of the uncrompressed file
    """
    path = Path(archive_path)
    final_path = path.with_name(path.stem)

    with zipfile.ZipFile(archive_path, "r") as zip_file:
        member = zip_file.getinfo("chromedriver")
        member.filename = final_path.stem
        extracted_path = zip_file.extract(member, str(final_path.parent))
        # Add the right permissions to the extracted file
        if member.create_system == ZIP_UNIX_SYSTEM:
            unix_attributes = member.external_attr >> 16
            if unix_attributes:
                chmod(extracted_path, unix_attributes)

    return extracted_path


def batch(iterable, size: int = 1):
    """Slice an iterable into batches of given size.

    Args:
        iterable (Iterable): iterable to slice into batches
        n (int, optional): size of each batch. Default to 1.
    Returns:
        Iterable:
    """
    length = len(iterable)
    for ndx in range(0, length, size):
        yield iterable[ndx : min(ndx + size, length)]
