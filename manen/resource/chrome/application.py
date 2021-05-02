"""
manen.resource.chrome.application
=================================
"""
import re
import shutil
from datetime import datetime
from subprocess import PIPE, STDOUT, Popen
from typing import TYPE_CHECKING, Dict, List

import requests

from ...exceptions import ManenException
from ...helpers import PLATFORM
from ...helpers import version as parse_version

if TYPE_CHECKING:
    from ...typing import Version

# https://cloud.google.com/storage/docs/xml-api/get-bucket-list

COMMANDS = {
    "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "Linux": "google-chrome",
}


def installed_version() -> "Version":
    if PLATFORM.system not in COMMANDS:
        raise ManenException(
            "Unable to find the Google Chrome command for the platform `%s`"
            % PLATFORM.system
        )

    version_command = Popen(
        [COMMANDS[PLATFORM.system], "--version"], stdout=PIPE, stderr=STDOUT,
    )
    ans, stderr = version_command.communicate()
    if stderr:
        raise ManenException(
            "The following exception was raised while finding the installed "
            "version: {!r}".format(stderr)
        )

    pattern = re.compile(r"(?P<version>[\d.]+)")
    match = pattern.search(ans.decode())
    if not match:
        raise ManenException(f"No version inferred from the string {ans!r}")
    return parse_version(match.group("version"))


def is_installed():
    return bool(shutil.which(COMMANDS[PLATFORM.system]))


def list_versions(os: str = PLATFORM.system):
    def extractor(prefix):
        return lambda data: {
            "version": parse_version(data[f"{prefix}_version"]),
            "release_date": datetime.strptime(
                data[f"{prefix}_reldate"], "%m/%d/%y"
            ).date(),
            "os": data["os"],
            "channel": data["channel"],
        }

    mapping_os = {"Windows": "win", "Darwin": "mac"}
    params = {"os": mapping_os[os] if os else os}
    res = requests.get("http://omahaproxy.appspot.com/all.json", params=params)
    versions: List[Dict] = []
    for data in res.json():
        versions.extend(map(extractor("current"), data["versions"]))
        versions.extend(map(extractor("previous"), data["versions"]))
    return sorted(versions, key=lambda item: item["version"])
