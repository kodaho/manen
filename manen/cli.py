"""
manen.cli
=========

CLI for :py:mod:`manen`.
"""

import argparse
from typing import List

from questionary import Choice, prompt

from manen.helpers import version_as_str

from .helpers import version_as_str
from .resource.brave import application as brave_app
from .resource.chrome import application as chrome_app
from .resource.chrome import driver as chromedriver


def get_args():
    """Get arguments from the command line."""
    parser = argparse.ArgumentParser(prog="manen")
    choices = ["download"]
    parser.add_argument(dest="command", choices=choices)
    return parser.parse_args()


def download_workflow():
    """Build the pipeline of successive questions used to identify the drivers
    to be downloaded.
    """
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


def download(platform: str, browser: str, versions: List[str]):
    """Download the drivers based on the information provided in questionary pipeline.

    Args:
        os (str): platform on which the drivers will run (1st answer in CLI workflow)
        browser (str): browser associated to the drivers (2nd anwser in CLI workflow)
        versions (List[str]): versions to be downloaded (3rd answer in CLI workflow)

    Raises:
        NotImplementedError: if the browser is different from Chrome or Brave.
    """
    if browser == "chrome":
        for version in versions:
            print(
                f"📥 Dowloading version {version} for the {browser} browser on {platform}..."
            )
            driver_file = chromedriver.download(
                version=version, platform_system=platform
            )
            print(f"✅ Driver file available at {driver_file}")
    else:
        raise NotImplementedError


def main():
    """Main function run by the CLI."""
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
