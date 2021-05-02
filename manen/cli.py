"""
manen.cli
=========

CLI for :py:mod:`manen`."""

import argparse
from manen.helpers import version_as_str

from questionary import Choice, prompt

from .resource import chrome
from .helpers import version_as_str


def get_args():
    parser = argparse.ArgumentParser(prog="manen")
    choices = ["download", "ls"]
    parser.add_argument(dest="command", choices=choices)
    return parser.parse_args()


def download_workflow():
    chrome_version = chrome.application.installed_version()
    return [
        {
            "type": "select",
            "name": "os",
            "message": "What is your OS?",
            "choices": [
                Choice("Mac OS", "Darwin"),
                Choice("Linux", "Linux"),
                Choice(
                    "Windows", "Windows", disabled="Windows is not supported. Yet..."
                ),
            ],
        },
        {
            "type": "select",
            "name": "browser",
            "message": "For which browser do you want to download the drivers?",
            "choices": [Choice("Chrome", "chrome"), Choice("Firefox", "firefox")],
        },
        {
            "type": "checkbox",
            "name": "versions",
            "message": "Choose the version you want to download.",
            "choices": lambda choices: [
                Choice(
                    "{}{}".format(
                        version_as_str(item["version"]),
                        " (compatible)"
                        if item["version"][:3] == chrome_version[:3]
                        else "",
                    ),
                    version_as_str(item["version"]),
                )
                for item in chrome.driver.list_versions()[-10:]
            ],
        },
    ]


def download(os, browser, versions):
    if browser == "chrome":
        for version in versions:
            print(
                f"📥 Dowloading version {version} for the {browser} browser on {os}..."
            )
            driver_file = chrome.driver.download(version=version, platform_system=os)
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
    elif args.command == "ls":
        pass
    else:
        print("Work In Progress...")


if __name__ == "__main__":
    main()
