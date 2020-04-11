from glob import glob
from os import makedirs
from os.path import abspath, exists, join

import requests

from ..exceptions import BrowserNotSupported, DriverNotFound
from ..helpers import EXPANDED_ASSET_PATH, ZIPPED_ASSET_PATH

ZIP_UNIX_SYSTEM = 3


def get_driver_path(browser, platform, version="*"):
    path = join(
        EXPANDED_ASSET_PATH, browser, "{}*".format(version), "*{}*".format(platform)
    )
    paths = glob(path)
    if not paths:
        raise DriverNotFound(
            'No driver found matching browser="{}", '.format(browser)
            + 'platform="{}" and version="{}".'.format(platform, version)
        )
    return sorted(paths)[-1]


def fetch_geckodriver_versions():
    return ["v0.{}.0".format(i) for i in range(10, 25)]


def download_zipfile(url, browser):
    response = requests.get(url)
    response.raise_for_status()
    *_, version, zipname = url.split("/")
    version_path = abspath(join(ZIPPED_ASSET_PATH, browser.lower(), version))

    if not exists(version_path):
        makedirs(version_path)
    with open(join(version_path, zipname), mode="wb") as zip_file:
        zip_file.write(response.content)

    return join(version_path, zipname)


def get_zipurl(browser, platform):
    if browser == "firefox":
        platform_code = {
            "mac os": "macos.tar.gz",
            "windows": "win64.zip",
            "linux": "linux64.tar.gz",
        }[platform.lower()]
        return (
            "https://github.com/mozilla/geckodriver/releases/download"
            "/{0}/geckodriver-{0}-{1}".format("{0}", platform_code)
        )

    raise BrowserNotSupported(browser)
