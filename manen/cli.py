"""
manen.cli
=========

CLI for :py:mod:`manen`.
"""

import argparse

from questionary import Choice, prompt

from manen.helpers import version_as_str

from .helpers import version_as_str
from .resource.brave import application as brave_app
from .resource.chrome import application as chrome_app
from .resource.chrome import driver as chromedriver


def get_args():
    parser = argparse.ArgumentParser(prog="manen")
    choices = ["download"]
    parser.add_argument(dest="command", choices=choices)
    return parser.parse_args()


def download_workflow():
    chrome_version = chrome_app.installed_version()
    brave_version = brave_app.installed_version()

    def is_compatible(version):
        browsers = []
        if version[:3] == chrome_version[:3]:
            browsers.append("Chrome")
        if version[:3] == brave_version[:3]:
            browsers.append("Brave")
        if browsers:
            return f" (compatible with {', '.join(browsers)})"
        return ""

    return [
        {
            "type": "select",
            "name": "os",
            "message": "What is your OS?",
            "choices": [
                Choice("Mac OS", "Darwin"),
                Choice("Linux", "Linux"),
            ],
        },
        {
            "type": "select",
            "name": "browser",
            "message": "For which browser do you want to download the drivers?",
            "choices": [
                Choice("Chrome / Brave", "chrome"),
            ],
        },
        {
            "type": "checkbox",
            "name": "versions",
            "message": "Choose the version you want to download.",
            "choices": lambda choices: [
                Choice(
                    "{}{}".format(
                        version_as_str(item["version"]),
                        is_compatible(item["version"]),
                    ),
                    version_as_str(item["version"]),
                )
                for item in chromedriver.list_versions()[-10:]
            ],
        },
    ]


def download(os, browser, versions):
    if browser == "chrome":
        for version in versions:
            print(
                f"📥 Dowloading version {version} for the {browser} browser on {os}..."
            )
            driver_file = chromedriver.download(version=version, platform_system=os)
            print(f"✅ Driver file available at {driver_file}")
    else:
        raise NotImplementedError


def main():
    print(" 🌔 manen CLI\n")
    args = get_args()
    if args.command == "download":
        print("» Starting interactive CLI to download webdrivers...")
        driver_info = prompt(download_workflow())
        if driver_info:
            download(**driver_info)
    else:
        print("Work In Progress...")


if __name__ == "__main__":
    main()
