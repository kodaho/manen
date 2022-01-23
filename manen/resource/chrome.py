"""
manen.resource.chrome
=====================
"""
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from subprocess import PIPE, STDOUT, Popen
from typing import TYPE_CHECKING, Dict, List, Union

import requests

from ..exceptions import DriverNotFound, ManenException
from ..helpers import PLATFORM, extract
from ..helpers import version as parse_version
from ..helpers import version_as_str
from .local import LocalAsset

if TYPE_CHECKING:
    from ..typing import InstalledVersionInfo, Version


class application:  # type: ignore
    # https://cloud.google.com/storage/docs/xml-api/get-bucket-list

    BINARIES = {
        "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "Linux": "google-chrome",
    }

    @classmethod
    def installed_version(cls) -> "Version":
        """Get the version of the installed application, as a tuple.

        Raises:
            ManenException: raised in 4 possible cases:
                - the browser is not installed
                - `manen` doesn't know the shell command to find the version of Chrome
                - an error is returned by the shell command used to get the version
                - a version could not be inferred from the output of the shell command

        Returns:
            Tuple[int]: Version of the browser installed, as a tuple
        """
        if not cls.is_installed():
            raise ManenException("Chrome is not installed.")

        if PLATFORM.system not in cls.BINARIES:
            raise ManenException(
                f"Unable to find the Google Chrome command for the platform `{PLATFORM.system}`"
            )

        version_command = Popen(
            [cls.BINARIES[PLATFORM.system], "--version"],
            stdout=PIPE,
            stderr=STDOUT,
        )
        ans, stderr = version_command.communicate()
        if stderr:
            raise ManenException(
                "The following exception was raised while finding the installed "
                f"version: {stderr!r}"
            )

        pattern = re.compile(r"(?P<version>[\d.]+)")
        match = pattern.search(ans.decode())
        if not match:
            raise ManenException(f"No version inferred from the string {ans!r}")
        return parse_version(match.group("version"))

    @classmethod
    def is_installed(cls) -> bool:
        """Check if the application is installed locally.

        Returns:
            bool: Whether or not the browser is installed.
        """
        return bool(shutil.which(cls.BINARIES[PLATFORM.system]))

    @staticmethod
    def list_versions(os: str = PLATFORM.system) -> List["InstalledVersionInfo"]:
        """List all the versions available online for the browser.

        Args:
            os (str, optional): OS to check by. Defaults to ``PLATFORM.system``.
        Returns:
            List[InstalledVersionInfo]: A list of dictionaries with the following keys:
                - `version`
                - `release_date`
                - `os`
                - `channel`
        """

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
        versions: List["InstalledVersionInfo"] = []
        for data in res.json():
            versions.extend(map(extractor("current"), data["versions"]))  # type: ignore
            versions.extend(map(extractor("previous"), data["versions"]))  # type: ignore
        return sorted(versions, key=lambda item: item["version"])


class driver:
    """A set of functions used to manage the Chrome drivers. It can be used, for
    instance, to list all existing versions of Chromedriver and then download one of
    the available versions.
    """

    CHROMEDRIVER_API = "https://chromedriver.storage.googleapis.com/"

    @classmethod
    def download(
        cls,
        version: Union[str, "Version"] = "installed",
        platform_system: str = PLATFORM.system,
        unzip: bool = True,
        remove_archive: bool = True,
    ) -> str:
        """Given a specific Chrome version, download the matching driver from
        the official Chrome driver storage.

        Args:
            version (str, Tuple[int]): Default to the current installed version.
            os (str): Default to ``PLATFORM.system``.
            unzip (bool): Default to ``True``.
            remove_archive (bool): Default to ``True``.
        Returns:
            str: Path of the downloaded driver
        """
        if version == "latest":
            target_version = version_as_str(cls.latest_release())
        elif version == "installed":
            installed_version: str = version_as_str(application.installed_version(), 3)
            target_version = version_as_str(
                cls.list_versions(query=installed_version)[-1]["version"]
            )
        elif isinstance(version, tuple):
            target_version = version_as_str(version)
        else:
            target_version = version

        mapping_platform_code = {
            "Darwin": "mac64",
            "Windows": "win32",
            "Linux": "linux64",
        }
        platform_code = mapping_platform_code[platform_system]
        url = (
            cls.CHROMEDRIVER_API
            + target_version
            + "/chromedriver_{}.zip".format(platform_code)
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

    @classmethod
    def list_versions(cls, query: str = "", platform_system: str = PLATFORM.system):
        params: Dict[str, Union[str, int]] = {"marker": 3, "prefix": query}
        response = requests.get(cls.CHROMEDRIVER_API, params=params)
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

    @classmethod
    def latest_release(cls, version="installed") -> "Version":
        if version == "installed":
            version = version_as_str(application.installed_version(), 3)

        url = f"{cls.CHROMEDRIVER_API.rstrip('/')}/LATEST_RELEASE"
        url += f"_{version}" if version else ""

        remote_version = requests.get(url).content.decode()
        return parse_version(remote_version)

    @classmethod
    def get(
        cls,
        query: str = "installed",
        platform_system: str = PLATFORM.system,
        download_if_missing: bool = True,
    ) -> str:
        query = version_as_str(cls.latest_release(version=query))
        try:
            return LocalAsset.list_drivers(browser="chrome", version=query)[-1]["path"]
        except DriverNotFound as exception:
            if download_if_missing:
                return cls.download(version=query, platform_system=platform_system)
            raise exception
