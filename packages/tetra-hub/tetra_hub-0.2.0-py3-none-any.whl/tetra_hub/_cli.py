import configparser
import argparse
import shutil
import warnings
import os
from .public_rest_api import get_config_path

_HUB_URL = "https://hub.tetra.ai"


def get_cli_parser() -> argparse.ArgumentParser:

    # Main CLI arguments
    main_parser = argparse.ArgumentParser(description="CLI interface for tetra-hub")
    subparsers = main_parser.add_subparsers(dest="command")

    # Parser for configure command
    config_parser = subparsers.add_parser(
        "configure", help="Configure tetra-hub client"
    )
    config_parser.add_argument(
        "--api_token",
        action="store",
        help=f"API token (from the accounts page of {_HUB_URL})",
        required=True,
    )
    config_parser.add_argument(
        "--api_url",
        action="store",
        help=argparse.SUPPRESS,
        default=_HUB_URL,
    )
    config_parser.add_argument(
        "--web_url",
        action="store",
        help=argparse.SUPPRESS,
        default=_HUB_URL,
    )

    # Return the argument parser
    return main_parser


def configure(config_data: dict, tetra_config_ini_path: str) -> None:

    # Make a backup if it exists
    if os.path.exists(tetra_config_ini_path):
        backup_tetra_config = f"{tetra_config_ini_path}.bak"
        warnings.warn(
            f"Overwriting configuration: {tetra_config_ini_path} (previous configuration saved to {backup_tetra_config})"
        )
        shutil.copy(tetra_config_ini_path, backup_tetra_config)

    # Create a configuration
    config = configparser.ConfigParser()
    for section in config_data:
        config.add_section(section)
        for key, value in config_data[section].items():
            config.set(section, key, value)

    # Create and save the file
    os.makedirs(os.path.dirname(tetra_config_ini_path), exist_ok=True)
    with open(tetra_config_ini_path, "w") as configfile:
        config.write(configfile)

    # Let the user know they are ready to go.
    print(f"tetra-hub configuration saved to {tetra_config_ini_path}")
    print("=" * 20, f"{tetra_config_ini_path}", "=" * 20)
    with open(tetra_config_ini_path, "r") as configfile:
        print(configfile.read())


def main() -> None:

    # Parse command line arguments
    main_parser = get_cli_parser()
    args = main_parser.parse_args()

    if args.command == "configure":
        # Data to write to the configuration file
        config_data: dict = {
            "api": {
                "api_token": args.api_token,
                "api_url": args.api_url,
                "web_url": args.web_url,
            }
        }

    # Location for the config file
    config_path: str = get_config_path()

    # Configure
    configure(config_data, config_path)
