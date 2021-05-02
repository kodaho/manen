"""
manen.resource.chrome.driver
============================
"""
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Dict, Union

import requests

from ...exceptions import DriverNotFound
from ...helpers import PLATFORM, extract
from ...helpers import version as parse_version
from ...helpers import version_as_str
from ..local import LocalAsset
from .application import installed_version as app_version

if TYPE_CHECKING:
    from ...typing import Version


CHROMEDRIVER_API = "https://chromedriver.storage.googleapis.com/"


def download(
    version: Union[str, "Version"] = "installed",
    platform_system: str = PLATFORM.system,
    unzip: bool = True,
    remove_archive: bool = True,
):
    """Given a specific Chrome version, download the matching driver from
    the official Chrome driver storage.

    Args:
        version (str):
        os (str):
        unzip (bool):
        remove_archive (bool):
    Returns:
        str: path of the downloaded driver
    """
    if version == "latest":
        target_version = version_as_str(latest_release())
    elif version == "installed":
        installed_version: str = version_as_str(app_version(), 3)
        target_version = version_as_str(
            list_versions(query=installed_version)[-1]["version"]
        )
    elif isinstance(version, tuple):
        target_version = version_as_str(version)
    else:
        target_version = version

    mapping_platform_code = {"Darwin": "mac64", "Windows": "win32", "Linux": "linux64"}
    platform_code = mapping_platform_code[platform_system]
    url = (
        CHROMEDRIVER_API + target_version + "/chromedriver_{}.zip".format(platform_code)
    )
    response = requests.get(url)
    response.raise_for_status()

    driver = (
        LocalAsset.PATH
        / platform_system.lower()
        / "chrome"
        / target_version
        / "chromedriver.zip"
    )
    driver.parent.mkdir(parents=True, exist_ok=True)
    with open(driver, mode="wb") as zip_file:
        zip_file.write(response.content)

    filename = extract(str(driver)) if unzip else str(driver)

    if remove_archive:
        driver.unlink()

    return filename


def list_versions(query: str = "", platform_system: str = PLATFORM.system):
    params: Dict[str, Union[str, int]] = {"marker": 3, "prefix": query}
    response = requests.get(CHROMEDRIVER_API, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    ns = "".join(root.tag.partition("}")[:2])  # pylint: disable=invalid-name
    chromedrivers = (
        {
            "version": parse_version(
                (content.findtext(f"{ns}Key") or "").split("/")[0]
            ),
            "name": (content.findtext(f"{ns}Key") or "").split("/")[1],
            "updated_at": content.findtext(f"{ns}LastModified"),
            "size": int(content.findtext(f"{ns}Size") or 0),
        }
        for content in root.iterfind(f"{ns}Contents")
        if "chromedriver" in (content.findtext(f"{ns}Key") or "")
    )
    if platform_system:
        name_by_platform = {
            "Darwin": "chromedriver_mac64.zip",
            "Windows": "chromedriver_win32.zip",
            "Linux": "chromedriver_linux64.zip",
        }
        chromedrivers = (
            chromedriver
            for chromedriver in chromedrivers
            if name_by_platform[platform_system] == chromedriver["name"]
        )

    return sorted(chromedrivers, key=lambda x: x["version"])


def latest_release(version="installed"):
    if version == "installed":
        version = version_as_str(app_version(), 3)

    url = f"{CHROMEDRIVER_API.rstrip('/')}/LATEST_RELEASE"
    url += f"_{version}" if version else ""

    remote_version = requests.get(url).content.decode()
    return parse_version(remote_version)


def get(query: str = "installed", download_if_missing: bool = True) -> str:
    query = version_as_str(latest_release(version=query))
    try:
        return LocalAsset.list_drivers(browser="chrome", version=query)[-1]["path"]
    except DriverNotFound as exception:
        if download_if_missing:
            return download(version=query)
        raise exception
