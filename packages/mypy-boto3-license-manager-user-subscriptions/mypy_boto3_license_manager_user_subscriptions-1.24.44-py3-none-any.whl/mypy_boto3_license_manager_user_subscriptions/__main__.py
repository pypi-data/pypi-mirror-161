"""
Main CLI entrypoint.
"""
import sys


def print_info() -> None:
    """
    Print package info to stdout.
    """
    print(
        "Type annotations for boto3.LicenseManagerUserSubscriptions 1.24.44\nVersion:        "
        " 1.24.44\nBuilder version: 7.11.1\nDocs:           "
        " https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions//\nBoto3"
        " docs:     "
        " https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions\nOther"
        " services:  https://pypi.org/project/boto3-stubs/\nChangelog:      "
        " https://github.com/youtype/mypy_boto3_builder/releases"
    )


def print_version() -> None:
    """
    Print package version to stdout.
    """
    print("1.24.44")


def main() -> None:
    """
    Main CLI entrypoint.
    """
    if "--version" in sys.argv:
        return print_version()
    print_info()


if __name__ == "__main__":
    main()
