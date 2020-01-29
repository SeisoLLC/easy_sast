#!/usr/bin/env python3
"""
Config parser for easy_sast
"""

# built-ins
import copy
from argparse import ArgumentParser
import logging
from pathlib import Path
from typing import Any, Dict, List, Union
import os

# third party
import yaml

# custom
from veracode.api import ResultsAPI, UploadAPI, SandboxAPI
from veracode.utils import is_valid_attribute
from veracode import constants
from veracode import __version__, __project_name__

LOG = logging.getLogger(__project_name__ + "." + __name__)


def remove_nones(*, obj: Any) -> Any:
    """
    Remove Nones from a provided object
    """
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_nones(obj=item) for item in obj if item is not None)
    if isinstance(obj, dict):
        return type(obj)(
            (remove_nones(obj=key), remove_nones(obj=value))
            for key, value in obj.items()
            if key is not None and value is not None
        )
    return obj


def remove_empty_dicts(*, obj: Any) -> Any:
    """
    Remove empty dicts from a provided object
    """
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_empty_dicts(obj=item) for item in obj if item != {})
    if isinstance(obj, dict):
        return type(obj)(
            (remove_empty_dicts(obj=key), remove_empty_dicts(obj=value))
            for key, value in obj.items()
            if value != {}
        )
    return obj


def filter_config(*, config: Dict) -> Dict:
    """
    Perform config filtering
    """
    # Perform initial filtering
    filtered_config = remove_nones(obj=config)
    filtered_config = remove_empty_dicts(obj=filtered_config)

    # If filtering did not result in any changes, return the config
    if config == filtered_config:
        return config

    # Perform recursive filtering
    previous_iteration_filtered_config = filtered_config
    while True:
        if (
            filtered_config := remove_empty_dicts(obj=remove_nones(obj=filtered_config))
        ) != previous_iteration_filtered_config:
            previous_iteration_filtered_config = filtered_config
        else:
            return filtered_config


def get_default_config() -> Dict:
    """
    Return a dict of the default values
    """
    default_config: Dict[str, Union[int, Dict[str, Dict], str, List[str]]] = {}
    # Set the workflow default
    default_config["workflow"] = constants.DEFAULT_WORKFLOW
    # Set the loglevel default
    default_config["loglevel"] = "WARNING"
    # Set placeholders for the various APIs
    default_config["apis"] = {}
    for api in constants.SUPPORTED_APIS:
        default_config["apis"][api] = {}

    return default_config


def get_file_config(*, config_file: Path) -> Dict:
    """
    Return a dict of the values provided in the config file
    """
    if isinstance(config_file, Path):
        # Build the file_config
        file_config = parse_file_config(config_file=config_file)
        normalized_file_config = normalize_config(config=file_config)
    else:
        # Invalid argument
        LOG.error("config_file must be a Path object")
        raise ValueError

    return normalized_file_config


def parse_file_config(*, config_file: Path) -> Dict:
    """
    Parse the sast-veracode config file
    """
    # Filter
    suffix_whitelist = {".yml", ".yaml"}

    if config_file.suffix not in suffix_whitelist:
        LOG.error("Suffix for the config file %s is not allowed", config_file)
        return {}

    try:
        with open(config_file) as yaml_data:
            config = yaml.safe_load(yaml_data)
    except FileNotFoundError:
        LOG.warning("The config file %s was not found", config_file)
        config = {}
    except PermissionError as pe_err:
        LOG.error(
            "Permission denied when attempting to read the config file %s", config_file
        )
        raise pe_err
    except IsADirectoryError as isdir_err:
        LOG.error("The specified config file is a directory: %s", config_file)
        raise isdir_err
    except OSError as os_err:
        LOG.error(
            "Unknown OS error when attempting to read the config file %s", config_file
        )
        raise os_err

    return config


def get_env_config() -> Dict:
    """
    Return a dict of the environment variables
    """
    env_var_config = {}
    env_var_config["api_key_id"] = os.environ.get("VERACODE_API_KEY_ID", None)
    env_var_config["api_key_secret"] = os.environ.get("VERACODE_API_KEY_SECRET", None)
    return env_var_config


def add_apis_to_config(*, config: Dict) -> Dict:
    """
    Add the supported apis to a config
    """
    # Add the top level "apis" key
    if "apis" not in config.keys():
        config["apis"] = {}

    # Add a key for each of the supported APIs under the top level "apis" key
    for api in constants.SUPPORTED_APIS:
        if api not in config["apis"].keys():
            config["apis"][api] = {}

    return config


# pylint: disable=too-many-branches
def normalize_config(*, config: Dict) -> Dict:
    """
    Normalize a provided config dict into the preferred format for the
    supported APIs
    """
    ## Establish normalized structure
    config = add_apis_to_config(config=config)

    ## Move configs into the normalized structure
    for common_attribute in constants.COMMON_API_ATTRIBUTES:
        if common_attribute not in config.keys():
            continue

        # Distribute the keys into the appropriate slots
        for api in constants.SUPPORTED_APIS:
            config["apis"][api][common_attribute] = config[common_attribute]

        # Clean up
        del config[common_attribute]

    ## Normalize config value formats
    # Search for a loglevel value provided as a string and modify it to be an
    # accurate level
    if "loglevel" in config.keys() and isinstance(config["loglevel"], str):
        if hasattr(logging, config["loglevel"].upper()):
            config["loglevel"] = config["loglevel"].upper()
        else:
            LOG.error("Unable to normalize the provided loglevel")
            raise AttributeError

    # Search for a build_dir value provided as a string in the upload API
    # config and modify it to be a Path object
    if "build_dir" in config["apis"]["upload"].keys() and isinstance(
        config["apis"]["upload"]["build_dir"], str
    ):
        config["apis"]["upload"]["build_dir"] = Path(
            config["apis"]["upload"]["build_dir"]
        ).absolute()

    ## Sanitize the config
    # Perform a final filter of the config (may remove the top level "apis"
    # key, among other keys, if they were never populated)
    config = filter_config(config=config)

    if "apis" not in config.keys():
        return config

    ## Validate the api config values
    for api in set(config["apis"].keys()).intersection(constants.SUPPORTED_APIS):
        for key, value in config["apis"][api].items():
            if not is_valid_attribute(key=key, value=value):
                LOG.error("Unable to validate the normalized config")
                raise ValueError

    return config


def get_args_config() -> Dict:
    """
    Get the configs passed as arguments
    """
    parser = create_arg_parser()
    parsed_args = vars(parser.parse_args())

    inverted_attributes = {
        "auto_scan": "disable_auto_scan",
        "scan_all_nonfatal_top_level_modules": "disable_scan_nonfatal_modules",
    }

    # Invert and rename the inverted_attributes appropriately
    for key, value in inverted_attributes.items():
        if value in parsed_args.keys():
            parsed_args[key] = not parsed_args[value]
            del parsed_args[value]

    ## Load parsed arguments into args_config
    args_config = add_apis_to_config(config={})

    # Apply the configs from parsed_args
    for key in parsed_args.keys():
        # Distribute the parsed_args configurations appropriately
        if key in constants.ONLY_UPLOAD_ATTRIBUTES:
            args_config["apis"]["upload"][key] = parsed_args[key]
        elif key in constants.ONLY_RESULTS_ATTRIBUTES:
            args_config["apis"]["results"][key] = parsed_args[key]
        else:
            # Put in top level
            args_config[key] = parsed_args[key]

    normalized_args_config = normalize_config(config=args_config)

    return normalized_args_config


def create_arg_parser() -> ArgumentParser:
    """Parse the arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--api-key-id", type=str, help="veracode api key id",
    )
    parser.add_argument(
        "--api-key-secret", type=str, help="veracode api key secret",
    )
    parser.add_argument(
        "--app-id", type=str, help="application id as provided by Veracode",
    )
    parser.add_argument(
        "--build-dir",
        type=lambda p: Path(p).absolute(),
        help="a Path containing build artifacts",
    )
    parser.add_argument(
        "--build-id", type=str, help="application build id",
    )
    parser.add_argument(
        "--config-file",
        type=lambda p: Path(p).absolute(),
        default=Path("easy_sast.yml").absolute(),
        help="specify a config file",
    )
    parser.add_argument(
        "--disable-auto-scan", action="store_true", help="disable auto_scan"
    )
    parser.add_argument(
        "--disable-scan-nonfatal-modules",
        action="store_true",
        help="disable scan_all_nonfatal_top_level_modules",
    )
    parser.add_argument(
        "--ignore-compliance-status",
        action="store_true",
        help="ignore (but still check) the compliance status",
    )
    parser.add_argument("--sandbox-name", type=str, help="application sandbox name")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--workflow", nargs="+", help="specify the workflow steps to enable and order"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--debug",
        action="store_const",
        dest="loglevel",
        const="DEBUG",
        help="enable debug level logging",
    )
    group.add_argument(
        "--verbose",
        action="store_const",
        dest="loglevel",
        const="INFO",
        help="enable info level logging",
    )
    return parser


def is_valid_non_api_config(*, config: dict) -> bool:
    """
    Validate the non-api portions of a config
    """
    for key, value in config.items():
        if key == "apis":
            continue

        if not is_valid_attribute(key=key, value=value):
            LOG.error("Unable to validate the non-api configs")
            return False

    for attribute in constants.REQUIRED_CONFIG_ATTRIBUTES_TOP:
        if attribute not in config:
            LOG.error(
                "The final config does not contain the minimum required information"
            )
            return False

    return True


def is_valid_api_config(*, config: dict) -> bool:
    """
    Validate the api portions of a config
    """
    for step in config["workflow"]:
        # Don't validate configs for apis that won't be used
        for api in constants.WORKFLOW_TO_API_MAP[step].intersection(
            constants.SUPPORTED_APIS
        ):
            for attribute in constants.REQUIRED_CONFIG_ATTRIBUTES_API:
                if attribute not in config["apis"][api]:
                    LOG.error(
                        "The %s API config is missing the required %s config",
                        api,
                        attribute,
                    )
                    return False

            for key, value in config["apis"][api].items():
                if not is_valid_attribute(key=key, value=value):
                    LOG.error("Unable to validate the %s api config")
                    return False

    return True


def get_config() -> Dict:
    """
    Get the config dict
    """
    default_config = get_default_config()
    args_config = get_args_config()
    file_config = get_file_config(config_file=args_config["config_file"])
    env_config = get_env_config()

    ## Create the final config
    # Start with the minimal default
    config = copy.deepcopy(default_config)

    # Apply the config from the config file
    for api in constants.SUPPORTED_APIS:
        if "apis" in file_config and api in file_config["apis"].keys():
            config["apis"][api].update(file_config["apis"][api])

    # A subset of the options are used here to deter storing sensitive
    # information in a config file
    for option in constants.LIMITED_OPTIONS_SET:
        if option in file_config.keys():
            config[option] = file_config[option]

    # Apply the config from environment variables
    config.update(env_config)

    # Apply the config from the arguments
    for api in constants.SUPPORTED_APIS:
        if "apis" in args_config and api in args_config["apis"].keys():
            config["apis"][api].update(args_config["apis"][api])

    for option in constants.ALL_OPTIONS_SET:
        if option in args_config.keys():
            config[option] = args_config[option]

    # Perform validation of the non-api configs
    if not is_valid_non_api_config(config=config):
        raise ValueError

    # Perform validation of the api configs
    if not is_valid_api_config(config=config):
        raise ValueError

    return config


def apply_config(
    *, api: Union[ResultsAPI, UploadAPI, SandboxAPI], config: dict
) -> Union[ResultsAPI, UploadAPI, SandboxAPI]:
    """
    Apply a provided config dict to a provided object
    """
    config = add_apis_to_config(config=config)

    if isinstance(api, ResultsAPI):
        for key, value in config["apis"]["results"].items():
            setattr(api, key, value)
    elif isinstance(api, UploadAPI):
        for key, value in config["apis"]["upload"].items():
            setattr(api, key, value)
    elif isinstance(api, SandboxAPI):
        for key, value in config["apis"]["sandbox"].items():
            setattr(api, key, value)
    else:
        LOG.error("api argument is not a supported type (%s)", type(api))
        raise TypeError

    return api
