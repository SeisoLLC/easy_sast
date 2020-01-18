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
from veracode import __project_name__
from veracode.utils import is_valid_attribute, http_request

LOG = logging.getLogger(__project_name__ + "." + __name__)


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
        self.sandbox = None
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
    def sandbox(self):
        """
        Create the sandbox property
        """
        return self._sandbox  # pragma: no cover

    @sandbox.getter
    def sandbox(self):
        """
        Create a sandbox getter that validates before returning
        """
        # Validate what was already stored
        self._validate(key="sandbox", value=self._sandbox)
        return self._sandbox

    @sandbox.setter
    def sandbox(self, sandbox):
        """
        Create a sandbox setter that validates before setting
        """
        # Validate what was provided
        self._validate(key="sandbox", value=sandbox)
        self._sandbox = sandbox

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
