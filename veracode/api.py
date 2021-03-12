#!/usr/bin/env python3
"""
A python module to interface with the Veracode Static Analysis APIs
"""

# built-ins
from pathlib import Path
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# custom
from veracode import constants, __project_name__
from veracode.utils import (
    is_valid_attribute,
    http_request,
    get_app_id,
)

LOG = logging.getLogger(__project_name__ + "." + __name__)


class VeracodeXMLAPI:
    """
    A base Veracode XML API class to inherit from

    For more details, see Veracode's documentation at
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/pd_p6JjB9PcDNH3GzWF5Ag
    """

    def __init__(self, *, app_name: str):
        # Hard code to None as it should be specified in the derived classes
        self._version = None

        ## Use the setter to apply a default to ensure it is valid
        self.base_url = constants.API_BASE_URL

        # Set app name and look up ID
        self.app_name = app_name
        self.app_id = get_app_id(app_name)

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

    @property
    def app_name(self):
        """
        Create the app_name property
        """
        return self._app_name  # pragma: no cover

    @app_name.getter
    def app_name(self):
        """
        Create an app_name getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="app_name", value=self._app_name)
        return self._app_name

    @app_name.setter
    def app_name(self, app_name):
        """
        Create an app_name setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="app_name", value=app_name)
        self._app_name = app_name

    @staticmethod
    def _validate(*, key: str, value: Any):
        if is_valid_attribute(key=key, value=value):
            return True
        raise ValueError(f"Invalid {key}")


class UploadAPI(VeracodeXMLAPI):  # pylint: disable=too-many-instance-attributes
    """
    A class to interact with the Upload API
    """

    def __init__(self, *, app_name: str):
        # Don't forget to call the init of the parent
        super().__init__(app_name=app_name)

        ## Use the setter to apply a default to ensure it is valid
        # version information was pulled from
        # https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/G1Nd5yH0QSlT~vPccPhtRQ
        self.version = constants.UPLOAD_API_VERSIONS
        self.build_dir = Path("/build").absolute()
        self.build_id = datetime.utcnow().strftime("%F_%H-%M-%S")
        self.scan_all_nonfatal_top_level_modules = True
        self.auto_scan = True
        # sandbox_id is not meant to be set manually. Instead, configure using
        # the response of a Sandbox API query using the intended sandbox name
        self.sandbox_id = None

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
    def sandbox_id(self):
        """
        Create the sandbox_id property
        """
        return self._sandbox_id  # pragma: no cover

    @sandbox_id.getter
    def sandbox_id(self):
        """
        Create a sandbox_id getter that validates before returning

        This should only be set using the response of a Sandbox API query using
        the intended sandbox name
        """
        # Validate what was already stored
        self._validate(key="sandbox_id", value=self._sandbox_id)
        return self._sandbox_id

    @sandbox_id.setter
    def sandbox_id(self, sandbox_id):
        """
        Create a sandbox_id setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="sandbox_id", value=sandbox_id)
        self._sandbox_id = sandbox_id

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

    def __init__(self, *, app_name: str):
        # Don't forget to call the init of the parent
        super().__init__(app_name=app_name)

        ## Use the setter to apply a default to ensure it is valid
        self.ignore_compliance_status = False
        # version information was pulled from
        # https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/Mp2BEkLx6rD87k465BWqQg
        self.version = constants.RESULTS_API_VERSIONS

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


class SandboxAPI(VeracodeXMLAPI):
    """
    A class to interact with the Sandbox API
    """

    def __init__(self, *, app_name: str, sandbox_name: str):
        # Don't forget to call the init of the parent
        super().__init__(app_name=app_name)

        # version information was pulled from
        # https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/KusbW5J7EG8jEr64JEiBzw
        self.version = constants.SANDBOX_API_VERSIONS
        self.build_id = datetime.utcnow().strftime("%F_%H-%M-%S")
        self.sandbox_name = sandbox_name
        # sandbox_id is not meant to be set manually. Instead, configure using
        # the response of a Sandbox API query using the intended sandbox name
        self.sandbox_id = None

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
    def sandbox_id(self):
        """
        Create the sandbox_id property
        """
        return self._sandbox_id  # pragma: no cover

    @sandbox_id.getter
    def sandbox_id(self):
        """
        Create a sandbox_id getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="sandbox_id", value=self._sandbox_id)
        return self._sandbox_id

    @sandbox_id.setter
    def sandbox_id(self, sandbox_id):
        """
        Create a sandbox_id setter that validates before setting

        This should only be set using the response of a Sandbox API query using
        the intended sandbox name
        """
        # Validate what was provided
        self._validate(key="sandbox_id", value=sandbox_id)
        self._sandbox_id = sandbox_id

    @property
    def sandbox_name(self):
        """
        Create the sandbox_name property
        """
        return self._sandbox_name  # pragma: no cover

    @sandbox_name.getter
    def sandbox_name(self):
        """
        Create a sandbox_name getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="sandbox_name", value=self._sandbox_name)
        return self._sandbox_name

    @sandbox_name.setter
    def sandbox_name(self, sandbox_name):
        """
        Create a sandbox_name setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="sandbox_name", value=sandbox_name)
        self._sandbox_name = sandbox_name
