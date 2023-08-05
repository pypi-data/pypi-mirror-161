"""
Main CLI entrypoint.
"""
import sys


def print_info() -> None:
    """
    Print package info to stdout.
    """
    print(
        "Type annotations for botocore 1.27.40\n"
        "Version:         1.27.40\n"
        "Builder version: 7.10.1\n"
        "Docs:            https://pypi.org/project/botocore-stubs/\n"
        "Changelog:       https://github.com/youtype/mypy_boto3_builder/releases"
    )


def print_version() -> None:
    """
    Print package version to stdout.
    """
    print("1.27.40")


def main() -> None:
    """
    Main CLI entrypoint.
    """
    if "--version" in sys.argv:
        return print_version()
    print_info()


if __name__ == "__main__":
    main()
