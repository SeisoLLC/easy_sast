#!/usr/bin/env python3
"""
A python module to interface with the Veracode API(s)
"""

# built-ins
from functools import wraps
import types
import os
from typing import cast, Any, Callable, Dict, Optional
from pathlib import Path
import logging
import re
import inspect
from datetime import datetime
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

LOG = logging.getLogger(__project_name__ + "." + __name__)


def validate(func: Callable) -> Callable:
    """
    Decorator to validate config information
    """
    # pylint: disable=undefined-variable
    @wraps(func)
    def wrapper(**kwargs: Any) -> Callable:
        for key, value in kwargs.items():
            if isinstance(value, ResultsAPI):
                validate_results_api(results_api=value)
            elif isinstance(value, UploadAPI):
                validate_upload_api(upload_api=value)

            if is_valid_attribute(key=key, value=value):
                LOG.debug("%s is valid", key)
            else:
                LOG.error("%s is invalid", key)
                raise ValueError

        return func(**kwargs)

    return wrapper


class VeracodeXMLAPI:
    """
    A base Veracode XML API class to inherit from

    For more details, see Veracode's documentation at
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/pd_p6JjB9PcDNH3GzWF5Ag
    """

    def __init__(self):
        # Hard code these to None as they should be specified in the derived classes
        self._app_id = None
        self._version = None

        ## Use the setter to apply a default to ensure it is valid
        self.base_url = "https://analysiscenter.veracode.com/api/"

    def http_get(
        self,
        *,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ):
        """
        Perform a HTTP GET request to a Veracode XML API and return the
        response
        """
        return http_request(
            verb="get",
            url=self.base_url + self.version[endpoint] + "/" + endpoint,
            params=params,
            headers=headers,
        )

    def http_post(
        self,
        *,
        endpoint: str,
        data: Optional[bytes] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ):
        """
        Perform a HTTP POST request to a Veracode XML API and return the
        response
        """
        return http_request(
            verb="post",
            url=self.base_url + self.version[endpoint] + "/" + endpoint,
            data=data,
            params=params,
            headers=headers,
        )

    @property
    def base_url(self):
        """
        Create the base_url property
        """
        return self._base_url  # pragma: no cover

    @base_url.getter
    def base_url(self):
        """
        Create a base_url getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="base_url", value=self._base_url)
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        """
        Create a base_url setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="base_url", value=base_url)
        self._base_url = base_url

    @property
    def version(self):
        """
        Create the version property
        """
        return self._version  # pragma: no cover

    @version.getter
    def version(self):
        """
        Create a version getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="version", value=self._version)
        return self._version

    @version.setter
    def version(self, version):
        """
        Create a version setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="version", value=version)
        self._version = version

    @property
    def app_id(self):
        """
        Create the app_id property
        """
        return self._app_id  # pragma: no cover

    @app_id.getter
    def app_id(self):
        """
        Create an app_id getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="app_id", value=self._app_id)
        return self._app_id

    @app_id.setter
    def app_id(self, app_id):
        """
        Create an app_id setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="app_id", value=app_id)
        self._app_id = app_id

    @staticmethod
    def _validate(*, key: str, value: Any):
        if is_valid_attribute(key=key, value=value):
            return True
        raise ValueError(f"Invalid {key}")


class UploadAPI(VeracodeXMLAPI):  # pylint: disable=too-many-instance-attributes
    """
    A class to interact with the Upload API
    """

    def __init__(self, *, app_id: str):
        # Don't forget to call the init of the parent
        super().__init__()

        ## Use the setter to apply a default to ensure it is valid
        self.app_id = app_id
        # version information was pulled from
        # https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/G1Nd5yH0QSlT~vPccPhtRQ
        self.version = {
            "beginprescan.do": "5.0",
            "beginscan.do": "5.0",
            "createapp.do": "5.0",
            "createbuild.do": "5.0",
            "deleteapp.do": "5.0",
            "deletebuild.do": "5.0",
            "getappinfo.do": "5.0",
            "getapplist.do": "5.0",
            "getbuildinfo.do": "5.0",
            "getbuildlist.do": "5.0",
            "getfilelist.do": "5.0",
            "getpolicylist.do": "5.0",
            "getprescanresults.do": "5.0",
            "getvendorlist.do": "5.0",
            "removefile.do": "5.0",
            "updateapp.do": "5.0",
            "updatebuild.do": "5.0",
            "uploadfile.do": "5.0",
            "uploadlargefile.do": "5.0",
        }
        self.build_dir = Path("/build").absolute()
        self.build_id = datetime.utcnow().strftime("%F_%H-%M-%S")
        self.scan_all_nonfatal_top_level_modules = True
        self.auto_scan = True

    @property
    def build_dir(self):
        """
        Create the build_dir property
        """
        return self._build_dir  # pragma: no cover

    @build_dir.getter
    def build_dir(self):
        """
        Create a build_dir getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="build_dir", value=self._build_dir)
        return self._build_dir

    @build_dir.setter
    def build_dir(self, build_dir):
        """
        Create a build_dir setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="build_dir", value=build_dir)
        self._build_dir = build_dir

    @property
    def build_id(self):
        """
        Create the build_id property
        """
        return self._build_id  # pragma: no cover

    @build_id.getter
    def build_id(self):
        """
        Create a build_id getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="build_id", value=self._build_id)
        return self._build_id

    @build_id.setter
    def build_id(self, build_id):
        """
        Create a build_id setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="build_id", value=build_id)
        self._build_id = build_id

    @property
    def scan_all_nonfatal_top_level_modules(self):
        """
        Create the scan_all_nonfatal_top_level_modules property
        """
        return self._scan_all_nonfatal_top_level_modules  # pragma: no cover

    @scan_all_nonfatal_top_level_modules.getter
    def scan_all_nonfatal_top_level_modules(self):
        """
        Create a scan_all_nonfatal_top_level_modules getter that validates
        before returning
        """
        # Validate what was already stored
        self._validate(
            key="scan_all_nonfatal_top_level_modules",
            value=self._scan_all_nonfatal_top_level_modules,
        )
        return self._scan_all_nonfatal_top_level_modules

    @scan_all_nonfatal_top_level_modules.setter
    def scan_all_nonfatal_top_level_modules(self, scan_all_nonfatal_top_level_modules):
        """
        Create a scan_all_nonfatal_top_level_modules setter that validates before setting
        """
        # Validate what was provided
        self._validate(
            key="scan_all_nonfatal_top_level_modules",
            value=scan_all_nonfatal_top_level_modules,
        )
        self._scan_all_nonfatal_top_level_modules = scan_all_nonfatal_top_level_modules

    @property
    def auto_scan(self):
        """
        Create the auto_scan property
        """
        return self._auto_scan  # pragma: no cover

    @auto_scan.getter
    def auto_scan(self):
        """
        Create an auto_scan getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="auto_scan", value=self._auto_scan)
        return self._auto_scan

    @auto_scan.setter
    def auto_scan(self, auto_scan):
        """
        Create an auto_scan setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="auto_scan", value=auto_scan)
        self._auto_scan = auto_scan


# pylint: disable=too-many-instance-attributes
class ResultsAPI(VeracodeXMLAPI):
    """
    A class to interact with the Results API
    """

    def __init__(self, *, app_id: str):
        # Don't forget to call the init of the parent
        super().__init__()

        ## Use the setter to apply a default to ensure it is valid
        self.app_id = app_id
        self.ignore_compliance_status = False
        # version information was pulled from
        # https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/Mp2BEkLx6rD87k465BWqQg
        self.version = {
            "detailedreport.do": "5.0",
            "detailedreportpdf.do": "4.0",
            "getaccountcustomfieldlist.do": "5.0",
            "getappbuilds.do": "4.0",
            "getcallstacks.do": "5.0",
            "summaryreport.do": "4.0",
            "summaryreportpdf.do": "4.0",
            "thirdpartyreportpdf.do": "4.0",
        }

    @property
    def ignore_compliance_status(self):
        """
        Specify whether or not to ignore the app compliance status
        """
        return self._ignore_compliance_status  # pragma: no cover

    @ignore_compliance_status.getter
    def ignore_compliance_status(self):
        """
        Create an ignore_compliance_status getter that validates before returning
        """
        # Validate what was already stored
        self._validate(
            key="ignore_compliance_status", value=self._ignore_compliance_status
        )
        return self._ignore_compliance_status

    @ignore_compliance_status.setter
    def ignore_compliance_status(self, ignore_compliance_status):
        """
        Create an ignore_compliance_status setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="ignore_compliance_status", value=ignore_compliance_status)
        self._ignore_compliance_status = ignore_compliance_status


# See https://github.com/tiran/defusedxml/issues/48 for why this doesn't have a
# return type
def parse_xml(*, content: bytes):
    """
    Parse the XML returned by the Veracode XML APIs
    """
    try:
        element = ElementTree.fromstring(content)
        LOG.info("parse_xml successful")
    except InsecureElementTree.ParseError as parse_err:
        LOG.exception("Failed to parse the XML response, untrustworthy endpoint")
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
    *, verb: str, url: str, data: str = None, params: Dict = None, headers: Dict = None,
) -> InsecureElementTree.Element:
    """
    API GET to the Veracode XML APIs
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
        LOG.exception("%s encountered a HTTP error: %s", function_name, http_err)
        raise http_err
    except ConnectionError as conn_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.exception("%s encountered a connection error: %s", function_name, conn_err)
        raise conn_err
    except Timeout as time_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.exception("%s encountered a timeout error: %s", function_name, time_err)
        raise time_err
    except TooManyRedirects as redir_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.exception("%s encountered too many redirects: %s", function_name, redir_err)
        raise redir_err
    except RequestException as req_err:
        function_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
        LOG.exception(
            "%s encountered a request exception error: %s", function_name, req_err
        )
        raise req_err

    # Parse the XML response
    parsed_xml = parse_xml(content=response.content)

    if element_contains_error(parsed_xml=parsed_xml):
        LOG.error("The Veracode API responded with an error message")
        raise RuntimeError

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
    elif key == "scan_all_nonfatal_top_level_modules":
        if not isinstance(value, bool):
            is_valid = False
            LOG.error("An invalid scan_all_nonfatal_top_level_modules was provided")
    elif key == "auto_scan":
        if not isinstance(value, bool):
            is_valid = False
            LOG.error("An invalid auto_scan was provided")
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
            LOG.error("An invalid ignore_compliance_status was provided")
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


def validate_results_api(*, results_api: ResultsAPI) -> None:
    """
    Validate the ResultsAPI object contains the required information
    """
    property_set = set(
        p for p in dir(ResultsAPI) if isinstance(getattr(ResultsAPI, p), property)
    )

    # Validate that the properties pass sanitization
    for prop in property_set:
        # Use the getters to ensure that all of the properties of the instance
        # are valid
        getattr(results_api, prop)

    LOG.info("results_api passed validation")


def validate_upload_api(*, upload_api: UploadAPI) -> None:
    """
    Validate the UploadAPI object contains the required information
    """
    # Validate that the required properties exist
    property_set = set(
        p for p in dir(UploadAPI) if isinstance(getattr(UploadAPI, p), property)
    )

    # Validate that the properties pass sanitization
    for prop in property_set:
        # Use the getters to ensure that all of the properties of the instance
        # are valid
        getattr(upload_api, prop)

    LOG.info("upload_api passed validation")


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
        r"(?:[a-z0-9](?:[a-z0-9-_]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]((:[0-9]{1,4}|:[1-5][0-9]{4}|:6[0-4][0-9]{3}|:65[0-4][0-9]{2}|:655[0-2][0-9]|:655  3[0-5])?)"
    )

    if pattern.fullmatch(netloc):
        return True

    return False
