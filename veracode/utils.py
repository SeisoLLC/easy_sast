#!/usr/bin/env python3
"""
A python module to interface with the Veracode Static Analysis APIs
"""

# __future__ built-ins
# See PEP 563 @ https://www.python.org/dev/peps/pep-0563/
from __future__ import annotations

# built-ins
from functools import wraps
import types
import os
from typing import cast, Any, Callable, Dict, Union, TYPE_CHECKING
from pathlib import Path
import logging
import re
import inspect
from xml.etree import (  # nosec (This is only used for static typing)
    ElementTree as InsecureElementTree,
)
from urllib.parse import urlparse

# third party
import requests
from requests.exceptions import HTTPError, Timeout, RequestException, TooManyRedirects

# The packages below are third party, but not PEP 561 compatible, therefore we
# must exclude the import statement from mypy analysis as described in
# https://mypy.readthedocs.io/en/latest/running_mypy.html#missing-imports. For
# more detail, see
# https://mypy.readthedocs.io/en/latest/installed_packages.html
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC  # type: ignore
from defusedxml import ElementTree  # type: ignore

# custom
from veracode import constants, __project_name__

if TYPE_CHECKING:
    from veracode.api import ResultsAPI, UploadAPI, SandboxAPI

LOG = logging.getLogger(__project_name__ + "." + __name__)


def validate(func: Callable) -> Callable:
    """
    Decorator to validate config information
    """
    # pylint: disable=undefined-variable
    @wraps(func)
    def wrapper(**kwargs: Any) -> Callable:
        for key, value in kwargs.items():
            if type(value).__name__ in constants.SUPPORTED_API_CLASSES:
                validate_api(api=value)
                LOG.debug("%s is valid", key)

            if is_valid_attribute(key=key, value=value):
                LOG.debug("%s is valid", key)
            else:
                LOG.error("%s is invalid", key)
                raise ValueError

        return func(**kwargs)

    return wrapper


# See https://github.com/tiran/defusedxml/issues/48 for why this doesn't have a
# return type
def parse_xml(*, content: bytes):
    """
    Parse the XML returned by the Veracode XML APIs
    """
    try:
        element = ElementTree.fromstring(content)
        LOG.debug("parse_xml successful")
    except InsecureElementTree.ParseError as parse_err:
        LOG.error("Failed to parse the XML response, untrustworthy endpoint")
        raise parse_err
    return element


def element_contains_error(*, parsed_xml: InsecureElementTree.Element) -> bool:
    """
    Check for an error
    """
    if parsed_xml.tag.casefold() == "error":
        return True

    return False


@validate
def http_request(  # pylint: disable=too-many-statements
    *,
    verb: str,
    url: str,
    data: str = None,
    params: Dict = None,
    headers: Dict = None,
) -> InsecureElementTree.Element:
    """
    Make API requests
    """
    try:
        LOG.debug("Querying the %s endpoint with a %s", url, verb)
        if verb == "get":
            response = requests.get(
                url,
                params=params,
                headers=headers,
                auth=RequestsAuthPluginVeracodeHMAC(),
            )
        if verb == "post":
            response = requests.post(
                url,
                data=data,
                params=params,
                headers=headers,
                auth=RequestsAuthPluginVeracodeHMAC(),
            )

        LOG.debug("Received a status code of %s", response.status_code)
        LOG.debug("Received content of %s", response.content)
        if response.status_code != 200:
            LOG.error("Encountered an issue with the response status code")
            response.raise_for_status()
    except HTTPError as http_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.error("%s encountered a HTTP error: %s", function_name, http_err)
        raise http_err
    except ConnectionError as conn_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.error("%s encountered a connection error: %s", function_name, conn_err)
        raise conn_err
    except Timeout as time_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.error("%s encountered a timeout error: %s", function_name, time_err)
        raise time_err
    except TooManyRedirects as redir_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.error("%s encountered too many redirects: %s", function_name, redir_err)
        raise redir_err
    except RequestException as req_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.error(
            "%s encountered a request exception error: %s", function_name, req_err
        )
        raise req_err

    # Parse the XML response
    parsed_xml = parse_xml(content=response.content)

    return parsed_xml


def is_valid_attribute(  # pylint: disable=too-many-branches, too-many-statements
    *, key: str, value: Any
) -> bool:
    """
    Validate the provided attribute
    """
    # Do not log the values to avoid sensitive information disclosure
    LOG.debug("Provided key to is_valid_attribute: %s", key)

    is_valid = True

    # Key-specific validation
    if key == "base_url":
        try:
            parsed_url = urlparse(value)
            if protocol_is_insecure(protocol=parsed_url.scheme):
                is_valid = False
                LOG.error("An insecure protocol was provided in the base_url")
            if parsed_url.netloc == "":
                is_valid = False
                LOG.error("An empty network location was provided in the base_url")
            if not is_valid_netloc(netloc=parsed_url.netloc):
                is_valid = False
                LOG.error("An invalid network location was provided in the base_url")
            # A useful side effect of the below check is that it will cause a
            # ValueError if the port is specified but invalid
            if parsed_url.port is None:
                LOG.debug("A port was not specified in the base_url")
            if parsed_url.path == "/" or parsed_url.path == "":
                is_valid = False
                LOG.error("An empty path was provided in the base_url")
            if not parsed_url.path.endswith("/"):
                is_valid = False
                LOG.error("An invalid basepath was provided. Must end with /")
        except ValueError as val_err:
            is_valid = False
            LOG.error("An invalid base_url was provided")
            raise val_err
    elif key == "version":
        if not isinstance(value, dict):
            is_valid = False
            LOG.error("The version must be a dict")
        else:
            for inner_key, inner_value in value.items():
                if not isinstance(inner_key, str):
                    is_valid = False
                    LOG.error("The keys in the version dict must be strings")
                if not isinstance(inner_value, str):
                    is_valid = False
                    LOG.error("The values in the version dict must be strings")
    elif key == "endpoint":
        if not isinstance(value, str):
            is_valid = False
            LOG.error("endpoint must be a string")
        # Limiting to unreserved characters as defined in
        # https://tools.ietf.org/html/rfc3986#section-2.3
        elif not re.fullmatch("[a-zA-Z0-9-._~]+", value):
            is_valid = False
            LOG.error("An invalid endpoint was provided")
    elif key == "app_id":
        if not isinstance(value, str):
            is_valid = False
            LOG.error("app_id must be a string")

        try:
            int(value)
        except (ValueError, TypeError):
            is_valid = False
            LOG.error("app_id must be a string containing a whole number")
    elif key == "build_dir":
        if not isinstance(value, Path):
            is_valid = False
            LOG.error("An invalid build_dir was provided")
    elif key == "build_id":
        if not isinstance(value, str):
            is_valid = False
            LOG.error("build_id must be a string")
        # Limiting to unreserved characters as defined in
        # https://tools.ietf.org/html/rfc3986#section-2.3
        elif not re.fullmatch("[a-zA-Z0-9-._~]+", value):
            is_valid = False
            LOG.error("An invalid build_id was provided")
    elif key == "sandbox_id":
        if not isinstance(value, str) and value is not None:
            is_valid = False
            LOG.error("sandbox_id must be a string or None")

        if isinstance(value, str):
            try:
                int(value)
            except (ValueError, TypeError):
                is_valid = False
                LOG.error(
                    "sandbox_id must be None or a string containing a whole number"
                )
    elif key == "scan_all_nonfatal_top_level_modules":
        if not isinstance(value, bool):
            is_valid = False
            LOG.error("scan_all_nonfatal_top_level_modules must be a boolean")
    elif key == "auto_scan":
        if not isinstance(value, bool):
            is_valid = False
            LOG.error("auto_scan must be a boolean")
    elif key == "sandbox_name":
        if not isinstance(value, str):
            is_valid = False
            LOG.error("sandbox_name must be a string")
        # Roughly the Veracode Sandbox allowed characters, excluding \
        elif not re.fullmatch(r"[a-zA-Z0-9`~!@#$%^&*()_+=\-\[\]|}{;:,./? ]+", value):
            is_valid = False
            LOG.error("An invalid sandbox_name was provided")
    elif key == "api_key_id":
        if not isinstance(value, str) or len(str(value)) != 32:
            is_valid = False
            LOG.error("api_key_id must be a 32 character string")

        try:
            int(value, 16)
        except (ValueError, TypeError):
            is_valid = False
            LOG.error("api_key_id must be hex")
    elif key == "api_key_secret":
        if len(str(value)) != 128:
            is_valid = False
            LOG.error("api_key_secret must be 128 characters")

        try:
            int(value, 16)
        except (ValueError, TypeError):
            is_valid = False
            LOG.error("api_key_secret must be hex")
    elif key == "ignore_compliance_status":
        if not isinstance(value, bool):
            is_valid = False
            LOG.error("ignore_compliance_status must be a boolean")
    elif key == "loglevel":
        if value not in constants.ALLOWED_LOG_LEVELS:
            is_valid = False
            LOG.error("Invalid log level: %s", value)
    elif key == "workflow":
        if not isinstance(value, list):
            is_valid = False
            LOG.error("workflow must be a list")
        if not constants.SUPPORTED_WORKFLOWS.issuperset(set(value)):
            is_valid = False
            LOG.error("Invalid workflow: %s", value)
    elif key == "verb":
        if value not in constants.SUPPORTED_VERBS:
            is_valid = False
            LOG.error("Invalid or unsupported verb provided")
    else:
        # Do not log the values to avoid sensitive information disclosure
        LOG.debug("Unknown argument provided with key: %s", key)

    return is_valid


@validate
def configure_environment(*, api_key_id: str, api_key_secret: str) -> None:
    """
    Configure the environment variables
    """
    ## Set environment variables for veracode-api-signing
    if (
        "VERACODE_API_KEY_ID" in os.environ
        and os.environ.get("VERACODE_API_KEY_ID") != api_key_id
    ):
        LOG.warning(
            "VERACODE_API_KEY_ID environment variable is being overwritten based on the effective configuration"
        )
    elif "VERACODE_API_KEY_ID" not in os.environ:
        LOG.debug("VERACODE_API_KEY_ID environment variable not detected")

    os.environ["VERACODE_API_KEY_ID"] = api_key_id

    if (
        "VERACODE_API_KEY_SECRET" in os.environ
        and os.environ.get("VERACODE_API_KEY_SECRET") != api_key_secret
    ):
        LOG.warning(
            "VERACODE_API_KEY_SECRET environment variable is being overwritten based on the effective configuration"
        )
    elif "VERACODE_API_KEY_SECRET" not in os.environ:
        LOG.debug("VERACODE_API_KEY_SECRET environment variable not detected")

    os.environ["VERACODE_API_KEY_SECRET"] = api_key_secret


def validate_api(*, api: Union[ResultsAPI, UploadAPI, SandboxAPI]) -> None:
    """
    Validate that an api object contains the required information
    """
    api_type = type(api)

    property_set = set(
        p for p in dir(api_type) if isinstance(getattr(api_type, p), property)
    )

    # Validate that the properties pass sanitization
    for prop in property_set:
        # Use the getters to ensure that all of the properties of the instance
        # are valid
        getattr(api, prop)

    LOG.debug("The provided %s passed validation", api_type)


def protocol_is_insecure(*, protocol: str) -> bool:
    """
    Identify the use of insecure protocols
    """
    return bool(protocol.casefold() != "https")


def is_null(*, value: str) -> bool:
    """
    Identify if the passed value is null
    """
    if value is None:
        return True
    return False


def is_valid_netloc(*, netloc: str) -> bool:
    """
    Identify if a given netloc is valid
    """
    if not isinstance(netloc, str):
        return False

    pattern = re.compile(
        r"(?:[a-z0-9](?:[a-z0-9-_]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]((:[0-9]{1,4}|:[1-5][0-9]{4}|:6[0-4][0-9]{3}|:65[0-4][0-9]{2}|:655[0-2][0-9]|:6553[0-5])?)"
    )

    if pattern.fullmatch(netloc):
        return True

    return False
