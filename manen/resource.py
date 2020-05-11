"""Manage assets used by `manen`"""

import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from itertools import chain
from os import chmod
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests

from .exceptions import DriverNotFound, ManenException
from .helpers import PLATFORM

ZIP_UNIX_SYSTEM = 3


class Version:
    """
    Helper class to compare version matching the pattern:
    MAJOR.MINOR(.BRANCH)?.PATH where BRANCH is optional.

    https://sites.google.com/a/chromium.org/chromedriver/downloads/version-selection

    Note: This is not compliant with semantic versioning rules.
    """

    def __init__(self, version: str):
        """Build an instance of Version based on a string.

        Args:
            version (str): string matching the pattern

        Raises:
            ValueError: raised if the string is not in the right format
        """
        self.__class__.validate(version)
        self.__version = version

    def __str__(self):
        return self.__version

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__version}>"

    def __getitem__(self, index):
        splitted_version = self.__version.split(".")
        if isinstance(index, slice):
            return ".".join(splitted_version[index])
        if isinstance(index, int):
            return int(splitted_version[index])
        raise TypeError("`index` must be of type `int` or `slice`")

    @property
    def major(self) -> int:
        """Integer corresponding to the MAJOR part of the version."""
        return int(self.__version.split(".")[0])

    @property
    def minor(self) -> int:
        """Integer corresponding to the MINOR part of the version."""
        return int(self.__version.split(".")[1])

    @property
    def branch(self) -> Optional[int]:
        """Integer corresponding to the BRANCH part of the version."""
        versioning = self.__version.split(".")
        return int(versioning[2]) if len(versioning) == 4 else None

    @property
    def patch(self) -> int:
        """Integer corresponding to the PATCH part of the version."""
        return int(self.__version.split(".")[-1])

    @staticmethod
    def validate(version: str) -> bool:
        """Check the format of a version string.

        Args:
            version (str): [description]

        Raises:
            ValueError: [description]

        Returns:
            bool: [description]
        """
        if not re.match(r"^[\d]+.[\d]+.[\d]+(.[\d]+)?$", version):
            raise ValueError("Invalid version string")
        return True

    def __eq__(self, other: object):
        if isinstance(other, str):
            return self == self.__class__(other)
        if not isinstance(other, self.__class__):
            raise TypeError
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.branch == other.branch
        )


class LocalAsset:
    PATH = Path(__file__).parent / "assets/drivers"

    @classmethod
    def list_drivers(  # pylint: disable=bad-continuation
        cls,
        browser: str,
        os: Optional[str] = PLATFORM.system,
        version: Optional[str] = None,
    ):
        if os is None:
            os = "*"
        version = "*" if version is None else f"{version}*"
        drivers = list((cls.PATH / os.lower() / browser).glob(f"{version}/*"))
        if drivers:
            return [
                {
                    "path": str(path),
                    "version": path.parent.stem,
                    "browser": path.parents[1].stem,
                    "os": path.parents[2].stem,
                }
                for path in drivers
            ]
        raise DriverNotFound(
            'No driver found matching the query browser="{}", '.format(browser)
            + 'platform="{}" and version="{}".'.format(os, version)
        )


class ChromeAppResource:
    """
    https://cloud.google.com/storage/docs/xml-api/get-bucket-list
    """

    CHROMIUM_RELEASE_API = "http://omahaproxy.appspot.com/"
    COMMAND = {
        "mac": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "linux": "google-chrome",
    }

    @classmethod
    def list_remote(cls, os=PLATFORM.system) -> List[Dict]:
        def extract_current_and_previous_versions(data):
            current = {
                "version": Version(data["current_version"]),
                "release_date": datetime.strptime(
                    data["current_reldate"], "%m/%d/%y"
                ).date(),
                "os": data["os"],
                "channel": data["channel"],
            }
            previous = {
                "version": Version(data["previous_version"]),
                "release_date": datetime.strptime(
                    data["previous_reldate"], "%m/%d/%y"
                ).date(),
                "os": data["os"],
                "channel": data["channel"],
            }
            return [current, previous]

        params = {"os": os.lower() if os else os}
        res = requests.get(cls.CHROMIUM_RELEASE_API + "all.json", params=params)
        versions = []
        for data in res.json():
            versions.extend(
                list(
                    chain.from_iterable(
                        map(extract_current_and_previous_versions, data["versions"])
                    )
                )
            )
        return list(chain(versions))

    @classmethod
    def version(cls) -> "Version":
        command = cls.COMMAND[PLATFORM.system.lower()]
        if command is None:
            raise ManenException(
                "Unable to find the Google Chrome command for the platform %s"
                % PLATFORM.information
            )

        version_command = subprocess.Popen(
            [command, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        ans, stderr = version_command.communicate()
        if stderr:
            raise ManenException(stderr)

        pattern = re.compile(r"(?P<version>[\d.]+)")
        match = pattern.search(ans.decode())
        if not match:
            raise ManenException(
                "No version inferred from the string %s" % ans.decode()
            )
        return Version(match.group("version"))


class ChromeDriverResource:
    API = "https://chromedriver.storage.googleapis.com/"

    @classmethod
    def latest_release(cls, version: str = "installed") -> "Version":
        if version == "installed":
            version = ChromeAppResource.version()[:3]
        version = f"_{version}" if version else ""
        remote_version = requests.get(
            f"{cls.API}LATEST_RELEASE{version}"
        ).content.decode()
        return Version(remote_version)

    @classmethod
    def find(cls, query: str = "installed", download: bool = True) -> str:
        query = str(cls.latest_release(version=query))
        try:
            return LocalAsset.list_drivers(browser="chrome", version=query)[-1]["path"]
        except DriverNotFound as exception:
            if download:
                return cls.download(version=query)
            raise exception

    @classmethod
    def list_remote(cls, query: Optional[str] = None, os: str = PLATFORM.system):
        response = requests.get(cls.API, params={"marker": 3, "prefix": query})
        response.raise_for_status()
        root = ET.fromstring(response.content)
        namespaces = {"root": root.tag.split("}")[0].strip("{")}
        chromedrivers = filter(
            lambda x: "chromedriver" in x[0],
            zip(
                map(
                    lambda x: x.text,
                    root.findall("./root:Contents/root:Key", namespaces),
                ),
                map(
                    lambda x: datetime.strptime(x.text, "%Y-%m-%dT%H:%M:%S.%fZ"),
                    root.findall("./root:Contents/root:LastModified", namespaces),
                ),
                map(
                    lambda x: x.text,
                    root.findall("./root:Contents/root:Size", namespaces),
                ),
            ),
        )
        chromedrivers = map(
            lambda x: {
                "version": Version(x[0].split("/")[0]),
                "name": x[0].split("/")[1],
                "updated_at": x[1],
                "size": int(x[2]),
            },
            chromedrivers,
        )
        if os:
            chromedrivers = filter(lambda x: os.lower() in x["name"], chromedrivers)
        return sorted(chromedrivers, key=lambda x: x["updated_at"])

    @classmethod
    def download(  # pylint: disable=bad-continuation
        cls,
        version: Union[str, "Version"] = "installed",
        os: str = PLATFORM.system,
        extract: bool = True,
        remove_archive: bool = True,
    ) -> str:
        """Given a specific Chrome version, download the matching driver from
        the official Chrome driver storage.

        Args:
            version (str):
            os (str):
            extract (bool):
            remove_archive (bool):
        Returns:
            str: path of the downloaded driver
        """
        platform_code = {"mac": "mac64", "win": "win32", "linux": "linux64"}[os.lower()]
        if version == "latest":
            version = cls.latest_release()
        if version == "installed":
            installed_version = ChromeAppResource.version()[:3]
            version = cls.list_remote(query=installed_version)[-1]["version"]
            version = str(version)
        if isinstance(version, Version):
            version = str(version)
        url = cls.API + version + "/chromedriver_{}.zip".format(platform_code)
        response = requests.get(url)
        response.raise_for_status()
        name = LocalAsset.PATH / os.lower() / "chrome" / version / "chromedriver.zip"
        name.parent.mkdir(parents=True, exist_ok=True)
        with open(name, mode="wb") as zip_file:
            zip_file.write(response.content)

        if extract:
            filename = cls.extract(str(name))

        if remove_archive:
            name.unlink()

        return filename if extract else str(name)

    @classmethod
    def extract(cls, archive_path: str):
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


class FirefoxDriverResource:
    """
    Remote versions URL: https://api.github.com/repos/mozilla/geckodriver/releases
    https://developer.github.com/v3/repos/releases/
    """
