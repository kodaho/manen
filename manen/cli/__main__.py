import argparse
from questionary import prompt, Choice
from ..resource import ChromeDriverResource, ChromeResource


def get_args():
    parser = argparse.ArgumentParser(prog="manen",)
    choices = ["download"]
    parser.add_argument(
        dest="command", choices=choices,
    )
    return parser.parse_args()


def download_workflow():
    chrome_version = ChromeResource.version()
    return [
        {
            "type": "select",
            "name": "os",
            "message": "What is your OS?",
            "choices": [
                Choice("Mac OS", "mac"),
                Choice("Linux", "linux"),
                Choice("Windows", "win", disabled=True),
            ],
        },
        {
            "type": "select",
            "name": "browser",
            "message": "For which browser do you want to download the drivers?",
            "choices": [Choice("Chrome", "chrome")],
        },
        {
            "type": "select",
            "name": "version",
            "message": "Choose the version you want to download.",
            "choices": lambda choices: [
                Choice(
                    "{}{}".format(
                        str(item["version"]),
                        " (installed)" if item["version"] == chrome_version else "",
                    ),
                    str(item["version"]),
                )
                for item in ChromeDriverResource.remote_versions()[-10:]
            ],
        },
    ]


def download(os, browser, version):
    if browser == "chrome":
        print(f"📥 Dowloading version {version} for the {browser} browser on {os}...")
        driver_file = ChromeDriverResource.download(version=version, os=os)
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
