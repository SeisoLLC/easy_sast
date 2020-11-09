#!/usr/bin/env python3
# pylint: disable=too-many-public-methods, too-many-lines
"""
Unit tests for api.py
"""

# built-ins
from pathlib import Path
import logging
from unittest import TestCase
from unittest.mock import patch
from xml.etree import (  # nosec (Used only when TYPE_CHECKING) # nosem: python.lang.security.use-defused-xml.use-defused-xml
    ElementTree as InsecureElementTree,
)

# custom
from tests import constants
from veracode.api import ResultsAPI, UploadAPI, SandboxAPI, VeracodeXMLAPI

# Setup a logger
logging.getLogger()
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=FORMAT)
logging.raiseExceptions = True
LOG = logging.getLogger(__name__)


class TestVeracodeApiVeracodeXMLAPI(TestCase):
    """
    Test api.py's VeracodeXMLAPI class
    """

    ## VeracodeXMLAPI version property
    def test_veracode_xml_api_version(self):
        """
        Test the VeracodeXMLAPI version property
        """
        veracode_xml_api = VeracodeXMLAPI()

        # Fail when attempting to get the version property because version is
        # hard coded to an invalid value to discourage direct use of this class
        self.assertRaises(ValueError, getattr, veracode_xml_api, "version")

        # Fail when attempting to set the version property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            veracode_xml_api,
            "version",
            constants.INVALID_UPLOAD_API_INCORRECT_VERSION_VALUES["version"],
        )

        # Succeed when setting the version property to a valid value
        self.assertIsNone(
            setattr(veracode_xml_api, "version", constants.VALID_RESULTS_API["version"])
        )

        # Fail when attempting to delete the version property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, veracode_xml_api, "version")

    ## VeracodeXMLAPI app_id property
    def test_veracode_xml_api_app_id(self):
        """
        Test the VeracodeXMLAPI app_id property
        """
        veracode_xml_api = VeracodeXMLAPI()

        # Fail when attempting to get the app_id property because app_id is
        # hard coded to an invalid value to discourage direct use of this class
        self.assertRaises(ValueError, getattr, veracode_xml_api, "app_id")

        # Fail when attempting to set the app_id property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            veracode_xml_api,
            "app_id",
            constants.INVALID_RESULTS_API_INCORRECT_APP_ID["app_id"],
        )

        # Succeed when setting the app_id property to a valid value
        self.assertIsNone(
            setattr(veracode_xml_api, "app_id", constants.VALID_UPLOAD_API["app_id"])
        )

        # Fail when attempting to delete the app_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, veracode_xml_api, "app_id")

    ## VeracodeXMLAPI base_url property
    def test_veracode_xml_api_base_url(self):
        """
        Test the VeracodeXMLAPI base_url property
        """
        veracode_xml_api = VeracodeXMLAPI()

        # Succeed when getting a valid base_url property
        self.assertIsInstance(getattr(veracode_xml_api, "base_url"), str)

        # Fail when attempting to set the base_url property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            veracode_xml_api,
            "base_url",
            constants.INVALID_UPLOAD_API_MISSING_DOMAIN["base_url"],
        )

        # Succeed when setting the base_url property to a valid value
        self.assertIsNone(
            setattr(
                veracode_xml_api, "base_url", constants.VALID_UPLOAD_API["base_url"]
            )
        )

        # Fail when attempting to delete the base_url property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, veracode_xml_api, "base_url")

    ## VeracodeXMLAPI http_get method
    def test_veracode_xml_api_http_get(self):
        """
        Test the VeracodeXMLAPI http_get method
        """
        veracode_xml_api = VeracodeXMLAPI()

        # Fail when attempting to delete the http_get method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, veracode_xml_api, "http_get")

    ## VeracodeXMLAPI http_post method
    def test_veracode_xml_api_http_post(self):
        """
        Test the VeracodeXMLAPI http_post method
        """
        veracode_xml_api = VeracodeXMLAPI()

        # Fail when attempting to delete the http_post method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, veracode_xml_api, "http_get")

    ## VeracodeXMLAPI _validate method
    @patch("veracode.api.is_valid_attribute")
    def test_veracode_xml_api__validate(self, mock_is_valid_attribute):
        """
        Test the VeracodeXMLAPI _validate method
        """
        veracode_xml_api = VeracodeXMLAPI()

        # Mock all attributes are invalid
        mock_is_valid_attribute.return_value = False

        # Fail when attempting to call the _validate method, given that the
        # attributes are invalid
        self.assertRaises(
            ValueError,
            veracode_xml_api._validate,  # pylint: disable=protected-access
            key="key",
            value="patched to be invalid",
        )  # pylint: disable=protected-access

        # Mock all attributes are valid
        mock_is_valid_attribute.return_value = True

        # Succeed when calling the _validate method, given that the attributes


class TestVeracodeApiUploadAPI(TestCase):
    """
    Test api.py's UploadAPI class
    """

    ## UploadAPI version property
    def test_upload_api_version(self):
        """
        Test the UploadAPI version property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting a valid version property
        self.assertIsInstance(upload_api.version, dict)

        # Succeed when setting the version property to a valid value
        self.assertIsNone(
            setattr(upload_api, "version", constants.VALID_UPLOAD_API["version"])
        )

        # Fail when attempting to set the version property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "version",
            constants.INVALID_UPLOAD_API_INCORRECT_VERSION_VALUES["version"],
        )

        # Fail when attempting to get the version property when it contains an
        # invalid value
        upload_api._version = constants.INVALID_UPLOAD_API_INCORRECT_VERSION_VALUES[  # pylint: disable=protected-access
            "version"
        ]
        self.assertRaises(ValueError, getattr, upload_api, "version")

        # Fail when attempting to delete the version property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "version")

    ## UploadAPI app_id property
    def test_upload_api_app_id(self):
        """
        Test the UploadAPI app_id property
        """
        # Fail when attempting to create an UploadAPI object when the app_id
        # property wasn't provided to the constructor
        self.assertRaises(TypeError, UploadAPI)

        # Succeed when creating an UploadAPI object when the app_id property is
        # properly provided to the constructor
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])
        self.assertIsInstance(getattr(upload_api, "app_id"), str)

        # Succeed when setting the app_id property to a valid value
        self.assertIsNone(
            setattr(upload_api, "app_id", constants.VALID_UPLOAD_API["app_id"])
        )

        # Succeed when getting a valid app_id property
        self.assertIsInstance(upload_api.app_id, str)

        # Fail when attempting to set the app_id property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "app_id",
            constants.INVALID_RESULTS_API_INCORRECT_APP_ID["app_id"],
        )

        # Fail when attempting to get the app_id property when it contains an
        # invalid value
        upload_api._app_id = constants.INVALID_RESULTS_API_INCORRECT_APP_ID[  # pylint: disable=protected-access
            "app_id"
        ]
        self.assertRaises(ValueError, getattr, upload_api, "app_id")

        # Fail when attempting to delete the app_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "app_id")

    ## UploadAPI base_url property
    def test_upload_api_base_url(self):
        """
        Test the UploadAPI base_url property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting a valid base_url property
        self.assertIsInstance(upload_api.base_url, str)

        # Succeed when setting the base_url property to a valid value
        self.assertIsNone(
            setattr(upload_api, "base_url", constants.VALID_UPLOAD_API["base_url"])
        )

        # Fail when attempting to set the base_url property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "base_url",
            constants.INVALID_UPLOAD_API_MISSING_DOMAIN["base_url"],
        )

        # Fail when attempting to get the base_url property when it contains an
        # invalid value
        upload_api._base_url = constants.INVALID_UPLOAD_API_MISSING_DOMAIN[  # pylint: disable=protected-access
            "base_url"
        ]
        self.assertRaises(ValueError, getattr, upload_api, "base_url")

        # Fail when attempting to delete the base_url property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "base_url")

    ## UploadAPI build_dir property
    def test_upload_api_build_dir(self):
        """
        Test the UploadAPI build_dir property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting a valid build_dir property
        self.assertIsInstance(upload_api.build_dir, Path)

        # Succeed when setting the build_dir property to a valid value
        self.assertIsNone(
            setattr(upload_api, "build_dir", constants.VALID_UPLOAD_API["build_dir"])
        )

        # Fail when attempting to set the build_dir property to an invalid
        # value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "build_dir",
            constants.INVALID_UPLOAD_API_BUILD_DIR["build_dir"],
        )

        # Fail when attempting to get the build_dir property when it contains
        # an invalid value
        upload_api._build_dir = (  # pylint: disable=protected-access
            constants.INVALID_UPLOAD_API_BUILD_DIR["build_dir"]
        )
        self.assertRaises(ValueError, getattr, upload_api, "build_dir")

        # Fail when attempting to delete the build_dir property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "build_dir")

    ## UploadAPI build_id property
    def test_upload_api_build_id(self):
        """
        Test the UploadAPI build_id property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting a valid build_id property
        self.assertIsInstance(upload_api.build_id, str)

        # Succeed when setting the build_id property to a valid value
        self.assertIsNone(
            setattr(upload_api, "build_id", constants.VALID_UPLOAD_API["build_id"])
        )

        # Fail when attempting to set the build_id property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "build_id",
            constants.INVALID_UPLOAD_API_BUILD_ID["build_id"],
        )

        # Fail when attempting to get the build_id property when it contains an
        # invalid value
        upload_api._build_id = (  # pylint: disable=protected-access
            constants.INVALID_UPLOAD_API_BUILD_ID["build_id"]
        )
        self.assertRaises(ValueError, getattr, upload_api, "build_id")

        # Fail when attempting to delete the build_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "build_id")

    ## UploadAPI sandbox_id property
    def test_upload_api_sandbox_id(self):
        """
        Test the UploadAPI sandbox_id property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting the default sandbox_id property
        self.assertIsNone(upload_api.sandbox_id)

        # Succeed when setting the sandbox_id property to a valid value
        self.assertIsNone(setattr(upload_api, "sandbox_id", None))
        self.assertIsNone(setattr(upload_api, "sandbox_id", "12489"))

        # Succeed when getting a valid app_id property
        self.assertIsInstance(upload_api.sandbox_id, str)

        # Fail when attempting to set the sandbox_id property to an invalid
        # value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "sandbox_id",
            12489,
        )

        # Fail when attempting to get the sandbox_id property when it contains
        # an invalid value
        upload_api._sandbox_id = 12489  # pylint: disable=protected-access
        self.assertRaises(ValueError, getattr, upload_api, "sandbox_id")

        # Fail when attempting to delete the sandbox_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "sandbox_id")

    ## UploadAPI scan_all_nonfatal_top_level_modules property
    def test_upload_api_scan_all_nonfatal_top_level_modules(self):
        """
        Test the UploadAPI scan_all_nonfatal_top_level_modules property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting a valid scan_all_nonfatal_top_level_modules
        # property
        self.assertIsInstance(upload_api.scan_all_nonfatal_top_level_modules, bool)

        # Succeed when setting the scan_all_nonfatal_top_level_modules property
        # to a valid value
        self.assertIsNone(
            setattr(
                upload_api,
                "scan_all_nonfatal_top_level_modules",
                constants.VALID_UPLOAD_API["scan_all_nonfatal_top_level_modules"],
            )
        )

        # Fail when attempting to set the scan_all_nonfatal_top_level_modules
        # property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "scan_all_nonfatal_top_level_modules",
            constants.INVALID_UPLOAD_API_SCAN_ALL_NONFATAL_TOP_LEVEL_MODULES[
                "scan_all_nonfatal_top_level_modules"
            ],
        )

        # Fail when attempting to get the scan_all_nonfatal_top_level_modules
        # property when it contains an invalid value
        upload_api._scan_all_nonfatal_top_level_modules = constants.INVALID_UPLOAD_API_SCAN_ALL_NONFATAL_TOP_LEVEL_MODULES[  # pylint: disable=protected-access
            "scan_all_nonfatal_top_level_modules"
        ]
        self.assertRaises(
            ValueError, getattr, upload_api, "scan_all_nonfatal_top_level_modules"
        )

        # Fail when attempting to delete the
        # scan_all_nonfatal_top_level_modules property, because the deleter is
        # intentionally missing
        self.assertRaises(
            AttributeError, delattr, upload_api, "scan_all_nonfatal_top_level_modules"
        )

    ## UploadAPI auto_scan property
    def test_upload_api_auto_scan(self):
        """
        Test the UploadAPI auto_scan property
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Succeed when getting a valid auto_scan property
        self.assertIsInstance(upload_api.auto_scan, bool)

        # Succeed when setting the auto_scan property to a valid value
        self.assertIsNone(
            setattr(upload_api, "auto_scan", constants.VALID_UPLOAD_API["auto_scan"])
        )

        # Fail when attempting to set the auto_scan property to an invalid
        # value
        self.assertRaises(
            ValueError,
            setattr,
            upload_api,
            "auto_scan",
            constants.INVALID_UPLOAD_API_AUTO_SCAN["auto_scan"],
        )

        # Fail when attempting to get the auto_scan property when it contains
        # an invalid value
        upload_api._auto_scan = (  # pylint: disable=protected-access
            constants.INVALID_UPLOAD_API_AUTO_SCAN["auto_scan"]
        )
        self.assertRaises(ValueError, getattr, upload_api, "auto_scan")

        # Fail when attempting to delete the auto_scan property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "auto_scan")

    ## UploadAPI http_get method
    @patch("veracode.api.http_request")
    def test_upload_api_http_get(self, mock_http_request):
        """
        Test the UploadAPI http_get method
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Fail when attempting to call the http_get method with invalid
        # arguments
        self.assertRaises(KeyError, upload_api.http_get, endpoint="getappbuilds.do")

        # Succeed when calling the http_get method with valid arguments
        mock_http_request.return_value = (
            constants.VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML["Element"]
        )
        self.assertIsInstance(
            upload_api.http_get(endpoint="getappinfo.do"), InsecureElementTree.Element
        )

        # Fail when attempting to delete the http_get method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "http_get")

    ## UploadAPI http_post method
    @patch("veracode.api.http_request")
    def test_upload_api_http_post(self, mock_http_request):
        """
        Test the UploadAPI http_post method
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Fail when attempting to call the http_post method with invalid
        # arguments
        self.assertRaises(KeyError, upload_api.http_post, endpoint="createuser.do")

        # Succeed when calling the http_post method with valid arguments
        mock_http_request.return_value = (
            constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML["Element"]
        )
        self.assertIsInstance(
            upload_api.http_post(endpoint="uploadlargefile.do"),
            InsecureElementTree.Element,
        )

        # Fail when attempting to delete the http_post method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "http_post")

    ## UploadAPI _validate method
    @patch("veracode.api.is_valid_attribute")
    def test_upload_api__validate(self, mock_is_valid_attribute):
        """
        Test the UploadAPI _validate method
        """
        upload_api = UploadAPI(app_id=constants.VALID_UPLOAD_API["app_id"])

        # Mock all attributes are invalid
        mock_is_valid_attribute.return_value = False

        # Fail when attempting to call the _validate method, given that the
        # attributes are invalid
        self.assertRaises(
            ValueError,
            upload_api._validate,  # pylint: disable=protected-access
            key="key",
            value="patched to be invalid",
        )

        # Mock all attributes are valid
        mock_is_valid_attribute.return_value = True

        # Succeed when calling the _validate method, given that the attributes
        # are valid
        self.assertTrue(
            upload_api._validate(  # pylint: disable=protected-access
                key="key", value="patched to be valid"
            )
        )

        # Fail when attempting to delete the _validate method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, upload_api, "_validate")


class TestVeracodeApiResultsAPI(TestCase):
    """
    Test api.py's ResultsAPI class
    """

    ## ResultsAPI version property
    def test_results_api_version(self):
        """
        Test the ResultsAPI version property
        """
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        # Succeed when getting a valid version property
        self.assertIsInstance(results_api.version, dict)

        # Succeed when setting the version property to a valid value
        self.assertIsNone(
            setattr(results_api, "version", constants.VALID_RESULTS_API["version"])
        )

        # Fail when attempting to set the version property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            results_api,
            "version",
            constants.INVALID_RESULTS_API_INCORRECT_VERSION_VALUES["version"],
        )

        # Fail when attempting to get the version property when it contains an
        # invalid value
        results_api._version = constants.INVALID_RESULTS_API_INCORRECT_VERSION_VALUES[  # pylint: disable=protected-access
            "version"
        ]
        self.assertRaises(ValueError, getattr, results_api, "version")

        # Fail when attempting to delete the version property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, results_api, "version")

    ## ResultsAPI app_id property
    def test_results_api_app_id(self):
        """
        Test the ResultsAPI app_id property
        """
        # Fail when attempting to create a ResultsAPI object when the app_id
        # property wasn't provided to the constructor
        self.assertRaises(TypeError, ResultsAPI)

        # Succeed when creating a ResultsAPI object when the app_id property is
        # properly provided to the constructor
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        self.assertIsInstance(getattr(results_api, "app_id"), str)

        # Succeed when setting the app_id property to a valid value
        self.assertIsNone(
            setattr(results_api, "app_id", constants.VALID_RESULTS_API["app_id"])
        )

        # Succeed when getting a valid app_id property
        self.assertIsInstance(results_api.app_id, str)

        # Fail when attempting to set the app_id property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            results_api,
            "app_id",
            constants.INVALID_RESULTS_API_INCORRECT_APP_ID["app_id"],
        )

        # Fail when attempting to get the app_id property when it contains an
        # invalid value
        results_api._app_id = constants.INVALID_RESULTS_API_INCORRECT_APP_ID[  # pylint: disable=protected-access
            "app_id"
        ]
        self.assertRaises(ValueError, getattr, results_api, "app_id")

        # Fail when attempting to delete the app_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, results_api, "app_id")

    ## ResultsAPI base_url property
    def test_results_api_base_url(self):
        """
        Test the ResultsAPI base_url property
        """
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        # Succeed when getting a valid base_url property
        self.assertIsInstance(results_api.base_url, str)

        # Succeed when setting the base_url property to a valid value
        self.assertIsNone(
            setattr(results_api, "base_url", constants.VALID_RESULTS_API["base_url"])
        )

        # Fail when attempting to set the base_url property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            results_api,
            "base_url",
            constants.INVALID_RESULTS_API_MISSING_DOMAIN["base_url"],
        )

        # Fail when attempting to get the base_url property when it contains an
        # invalid value
        results_api._base_url = constants.INVALID_RESULTS_API_MISSING_DOMAIN[  # pylint: disable=protected-access
            "base_url"
        ]
        self.assertRaises(ValueError, getattr, results_api, "base_url")

        # Fail when attempting to delete the base_url property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, results_api, "base_url")

    ## ResultsAPI ignore_compliance_status property
    def test_results_api_ignore_compliance_status(self):
        """
        Test the ResultsAPI ignore_compliance_status property
        """
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        # Succeed when getting a valid ignore_compliance_status property
        self.assertIsInstance(results_api.ignore_compliance_status, bool)

        # Succeed when setting the ignore_compliance_status property to a valid
        # value
        self.assertIsNone(
            setattr(
                results_api,
                "ignore_compliance_status",
                constants.VALID_RESULTS_API["ignore_compliance_status"],
            )
        )

        # Fail when attempting to set the ignore_compliance_status property to
        # an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            results_api,
            "ignore_compliance_status",
            constants.INVALID_RESULTS_API_INCORRECT_COMPLIANCE_STATUS[
                "ignore_compliance_status"
            ],
        )

        # Fail when attempting to get the ignore_compliance_status property
        # when it contains an invalid value
        results_api._ignore_compliance_status = constants.INVALID_RESULTS_API_INCORRECT_COMPLIANCE_STATUS[  # pylint: disable=protected-access
            "ignore_compliance_status"
        ]
        self.assertRaises(ValueError, getattr, results_api, "ignore_compliance_status")

        # Fail when attempting to delete the ignore_compliance_status property,
        # because the deleter is intentionally missing
        self.assertRaises(
            AttributeError, delattr, results_api, "ignore_compliance_status"
        )

    ## ResultsAPI http_get method
    @patch("veracode.api.http_request")
    def test_results_api_http_get(self, mock_http_request):
        """
        Test the ResultsAPI http_get method
        """
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        # Fail when attempting to call the http_get method with invalid
        # arguments
        self.assertRaises(KeyError, results_api.http_get, endpoint="getbuildlist.do")

        # Succeed when calling the http_get method with valid arguments
        mock_http_request.return_value = constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
            "Element"
        ]
        self.assertIsInstance(
            results_api.http_get(endpoint="getappbuilds.do"),
            InsecureElementTree.Element,
        )

        # Fail when attempting to delete the http_get method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, results_api, "http_get")

    ## ResultsAPI http_post method
    @patch("veracode.api.http_request")
    def test_results_api_http_post(self, mock_http_request):
        """
        Test the ResultsAPI http_post method
        """
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        # Fail when attempting to call the http_post method with invalid
        # arguments
        self.assertRaises(KeyError, results_api.http_post, endpoint="removefile.do")

        # Succeed when calling the http_post method with valid arguments
        #
        # As of the writing of this Veracode's Results API doesn't have any
        # endpoints that take a POST so the constants and endpoints below don't
        # align with a real-world scenario (because one doesn't exist)
        mock_http_request.return_value = constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
            "Element"
        ]
        self.assertIsInstance(
            results_api.http_post(endpoint="detailedreport.do"),
            InsecureElementTree.Element,
        )

        # Fail when attempting to delete the http_post method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, results_api, "http_post")

    ## RequestsAPI _validate method
    @patch("veracode.api.is_valid_attribute")
    def test_results_api__validate(self, mock_is_valid_attribute):
        """
        Test the ResultsAPI _validate method
        """
        results_api = ResultsAPI(app_id=constants.VALID_RESULTS_API["app_id"])

        # Mock all attributes are invalid
        mock_is_valid_attribute.return_value = False

        # Fail when attempting to call the _validate method, given that the
        # attributes are invalid
        self.assertRaises(
            ValueError,
            results_api._validate,  # pylint: disable=protected-access
            key="key",
            value="patched to be invalid",
        )

        # Mock all attributes are valid
        mock_is_valid_attribute.return_value = True

        # Succeed when calling the _validate method, given that the attributes
        # are valid
        self.assertTrue(
            results_api._validate(  # pylint: disable=protected-access
                key="key", value="patched to be valid"
            )
        )

        # Fail when attempting to delete the _validate method, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, results_api, "_validate")


class TestVeracodeApiSandboxAPI(TestCase):
    """
    Test api.py's SandboxAPI class
    """

    ## SandboxAPI version property
    def test_sandbox_api_version(self):
        """
        Test the SandboxAPI version property
        """
        sandbox_api = SandboxAPI(
            app_id=constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=constants.VALID_SANDBOX_API["sandbox_name"],
        )

        # Succeed when getting a valid version property
        self.assertIsInstance(sandbox_api.version, dict)

        # Succeed when setting the version property to a valid value
        self.assertIsNone(
            setattr(sandbox_api, "version", constants.VALID_SANDBOX_API["version"])
        )

        # Fail when attempting to set the version property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            sandbox_api,
            "version",
            constants.INVALID_SANDBOX_API_INCORRECT_VERSION_VALUES["version"],
        )

        # Fail when attempting to get the version property when it contains an
        # invalid value
        sandbox_api._version = constants.INVALID_SANDBOX_API_INCORRECT_VERSION_VALUES[  # pylint: disable=protected-access
            "version"
        ]
        self.assertRaises(ValueError, getattr, sandbox_api, "version")

        # Fail when attempting to delete the version property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, sandbox_api, "version")

    ## SandboxAPI app_id property
    def test_sandbox_api_app_id(self):
        """
        Test the SandboxAPI app_id property
        """
        # Fail when attempting to create an SandboxAPI object when the app_id
        # property wasn't provided to the constructor
        self.assertRaises(TypeError, SandboxAPI)

        # Succeed when creating an SandboxAPI object when the app_id property is
        # properly provided to the constructor
        sandbox_api = SandboxAPI(
            app_id=constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=constants.VALID_SANDBOX_API["sandbox_name"],
        )
        self.assertIsInstance(getattr(sandbox_api, "app_id"), str)

        # Succeed when setting the app_id property to a valid value
        self.assertIsNone(
            setattr(sandbox_api, "app_id", constants.VALID_SANDBOX_API["app_id"])
        )

        # Succeed when getting a valid app_id property
        self.assertIsInstance(sandbox_api.app_id, str)

        # Fail when attempting to set the app_id property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            sandbox_api,
            "app_id",
            constants.INVALID_RESULTS_API_INCORRECT_APP_ID["app_id"],
        )

        # Fail when attempting to get the app_id property when it contains an
        # invalid value
        sandbox_api._app_id = constants.INVALID_RESULTS_API_INCORRECT_APP_ID[  # pylint: disable=protected-access
            "app_id"
        ]
        self.assertRaises(ValueError, getattr, sandbox_api, "app_id")

        # Fail when attempting to delete the app_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, sandbox_api, "app_id")

    ## SandboxAPI base_url property
    def test_sandbox_api_base_url(self):
        """
        Test the SandboxAPI base_url property
        """
        sandbox_api = SandboxAPI(
            app_id=constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=constants.VALID_SANDBOX_API["sandbox_name"],
        )

        # Succeed when getting a valid base_url property
        self.assertIsInstance(sandbox_api.base_url, str)

        # Succeed when setting the base_url property to a valid value
        self.assertIsNone(
            setattr(sandbox_api, "base_url", constants.VALID_SANDBOX_API["base_url"])
        )

        # Fail when attempting to set the base_url property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            sandbox_api,
            "base_url",
            constants.INVALID_SANDBOX_API_INCORRECT_DOMAIN["base_url"],
        )

        # Fail when attempting to get the base_url property when it contains an
        # invalid value
        sandbox_api._base_url = constants.INVALID_SANDBOX_API_INCORRECT_DOMAIN[  # pylint: disable=protected-access
            "base_url"
        ]
        self.assertRaises(ValueError, getattr, sandbox_api, "base_url")

        # Fail when attempting to delete the base_url property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, sandbox_api, "base_url")

    ## SandboxAPI build_id property
    def test_sandbox_api_build_id(self):
        """
        Test the SandboxAPI build_id property
        """
        sandbox_api = SandboxAPI(
            app_id=constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=constants.VALID_SANDBOX_API["sandbox_name"],
        )

        # Succeed when getting a valid build_id property
        self.assertIsInstance(sandbox_api.build_id, str)

        # Succeed when setting the build_id property to a valid value
        self.assertIsNone(
            setattr(sandbox_api, "build_id", constants.VALID_SANDBOX_API["build_id"])
        )

        # Fail when attempting to set the build_id property to an invalid value
        self.assertRaises(
            ValueError,
            setattr,
            sandbox_api,
            "build_id",
            constants.INVALID_SANDBOX_API_BUILD_ID["build_id"],
        )

        # Fail when attempting to get the build_id property when it contains an
        # invalid value
        sandbox_api._build_id = (  # pylint: disable=protected-access
            constants.INVALID_SANDBOX_API_BUILD_ID["build_id"]
        )
        self.assertRaises(ValueError, getattr, sandbox_api, "build_id")

        # Fail when attempting to delete the build_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, sandbox_api, "build_id")

    ## SandboxAPI sandbox_id property
    def test_sandbox_api_sandbox_id(self):
        """
        Test the SandboxAPI sandbox_id property
        """
        sandbox_api = SandboxAPI(
            app_id=constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=constants.VALID_SANDBOX_API["sandbox_name"],
        )

        # Succeed when getting a the default sandbox_id property
        self.assertIsNone(sandbox_api.sandbox_id)

        # Succeed when setting the sandbox_id property to a valid value
        self.assertIsNone(setattr(sandbox_api, "sandbox_id", None))
        self.assertIsNone(setattr(sandbox_api, "sandbox_id", "12489"))

        # Succeed when getting a valid app_id property
        self.assertIsInstance(sandbox_api.sandbox_id, str)

        # Fail when attempting to set the sandbox_id property to an invalid
        # value
        self.assertRaises(
            ValueError,
            setattr,
            sandbox_api,
            "sandbox_id",
            12489,
        )

        # Fail when attempting to get the sandbox_id property when it contains
        # an invalid value
        sandbox_api._sandbox_id = 12489  # pylint: disable=protected-access
        self.assertRaises(ValueError, getattr, sandbox_api, "sandbox_id")

        # Fail when attempting to delete the sandbox_id property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, sandbox_api, "sandbox_id")

    ## SandboxAPI sandbox_name property
    def test_sandbox_api_sandbox_name(self):
        """
        Test the SandboxAPI sandbox_name property
        """
        sandbox_api = SandboxAPI(
            app_id=constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=constants.VALID_SANDBOX_API["sandbox_name"],
        )

        # Succeed when getting a valid sandbox_name property
        self.assertIsInstance(sandbox_api.sandbox_name, str)

        # Succeed when setting the sandbox_name property to a valid value
        self.assertIsNone(
            setattr(
                sandbox_api, "sandbox_name", constants.VALID_SANDBOX_API["sandbox_name"]
            )
        )

        # Fail when attempting to set the sandbox_name property to an invalid
        # value
        self.assertRaises(
            ValueError,
            setattr,
            sandbox_api,
            "sandbox_name",
            constants.INVALID_SANDBOX_API_SANDBOX_NAME["sandbox_name"],
        )

        # Fail when attempting to get the sandbox_name property when it
        # contains an invalid value
        sandbox_api._sandbox_name = constants.INVALID_SANDBOX_API_SANDBOX_NAME[  # pylint: disable=protected-access
            "sandbox_name"
        ]
        self.assertRaises(ValueError, getattr, sandbox_api, "sandbox_name")

        # Fail when attempting to delete the sandbox_name property, because the
        # deleter is intentionally missing
        self.assertRaises(AttributeError, delattr, sandbox_api, "sandbox_name")
