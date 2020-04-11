import argparse


def get_args():
    parser = argparse.ArgumentParser(prog="tellenium",)
    choices = ["info", "download", "ls", "list"]
    parser.add_argument(dest="command", choices=choices)
    return parser.parse_args()


def main():
    args = get_args()
    print("WIP")


if __name__ == "__main__":
    main()
