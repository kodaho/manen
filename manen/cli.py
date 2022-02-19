"""
manen.cli
=========

Command Line Interface for :py:mod:`manen`.
"""

import argparse
import sys
from typing import List

from questionary import Choice, prompt

from manen.helpers import version_as_str

from . import __version__
from .helpers import version_as_str
from .resource.brave import application as brave_app
from .resource.chrome import application as chrome_app
from .resource.chrome import driver as chromedriver


def with_browser_parser(subparser: argparse._SubParsersAction):
    """Build the parser for the `driver` sub-command.

    Args:
        subparser (argparse._SubParsersAction): subparser in which the command `browser` will
            be add
    Returns:
        argparse.ArgumentParser
    """
    subparser.add_parser(
        "browser",
        help="Utils to get information about the installed browser.",
    )


def with_driver_parser(subparser: argparse._SubParsersAction):
    """Build the parser for the `driver` sub-command.

    Args:
        subparser (argparse._SubParsersAction): subparser in which the command `driver` will
            be add
    """
    parser: argparse.ArgumentParser = subparser.add_parser(
        "driver",
        help="Management of the drivers executable needed to launch a Selenium/manen application.",
    )
    child_parser: argparse._SubParsersAction = parser.add_subparsers(
        dest="command",
        title="subcommands",
    )
    with_driver_download_parser(child_parser)


def with_driver_download_parser(subparser: argparse._SubParsersAction):
    """Build the subparser used for the download sub-command.

    Args:
        subparser (argparse._SubParsersAction): subparser in which the command
            `driver download` will be add
    """
    parser = subparser.add_parser(
        "download",
        description="Download one or several drivers for a specific browser on a given OS.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Set the specifications for the download through a serie of interactive questions. "
        "If specified, the options of the specifications group must not be set.",
    )

    spec_group = parser.add_argument_group("specifications")
    spec_group.add_argument(
        "-b",
        "--browser",
        required=False,
        choices=["chrome", "brave"],
        type=str.lower,
        help="Browser that will be used to launch the Selenium/manen application.",
    )
    spec_group.add_argument(
        "-p",
        "--platform",
        required=False,
        default="Mac",
        choices=["Darwin", "Linux"],
        type=lambda v: {"mac": "Darwin"}.get(v.lower(), v).title(),
        help="Platform (OS) on which the driver binary will run. Note that 'Darwin' is for MacOS "
        "and you can use the alias 'Mac' for this OS.",
    )
    spec_group.add_argument(
        "-v",
        "--version",
        nargs="+",
        help="List of driver versions to be downloaded",
    )

    return parser


def download_workflow():
    """Build the pipeline of successive questions used to identify the drivers to be downloaded.

    Returns:
        List[Dict]: list with metadata about the successive questions to be asked by
            `questionary.`
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
            "name": "platform",
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
        platform (str): platform on which the drivers will run (1st answer in CLI workflow)
        browser (str): browser associated to the drivers (2nd anwser in CLI workflow)
        versions (List[str]): versions to be downloaded (3rd answer in CLI workflow)

    Raises:
        NotImplementedError: if the browser is different from Chrome or Brave.
    """
    if browser in ("chrome", "brave"):
        for version in versions:
            print(
                f"↧ Dowloading version {version} for the {browser.title()} browser on ",
                "Mac" if platform.lower() == "darwin" else platform,
                "...",
                sep="",
            )
            driver_file = chromedriver.download(version=version, platform_system=platform)
            print(f"✓ Driver file available at {driver_file}")
    else:
        raise NotImplementedError(
            f"Dowloading drivers for browser {browser.title()} is not currently supported."
        )


def get_args() -> argparse.Namespace:
    """Parse the arguments specified in the command line.

    Returns:
        argparse.Namespace: class containing all options as attributes
    """
    parser = argparse.ArgumentParser(prog="manen")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparser = parser.add_subparsers(
        dest="section",
        title="commands",
        metavar="\n  Command managed by manen for resource management",
    )
    with_driver_parser(subparser)
    # with_browser_parser(subparser)
    return parser.parse_args()


def cli():
    """Command line entrypoint for the package. After retrieving the given argument(s) and
    option(s), it will run the right workflow according to the specified options.
    """
    args = get_args()
    if args.command == "download":
        if args.interactive and (args.browser or args.version):
            print(
                "⤫ Inconsistent CLI options choice; if you want to interactive mode, "
                "the specifications of the drivers must not be set at the same time."
            )
            sys.exit(1)
        elif args.interactive:
            print("» Starting interactive CLI to download webdrivers...")
            specifications = prompt(download_workflow())
        else:
            specifications = {
                "platform": args.platform,
                "browser": args.browser,
                "versions": args.version,
            }
        if specifications and specifications["browser"]:
            download(**specifications)


if __name__ == "__main__":
    cli()
