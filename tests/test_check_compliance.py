#!/usr/bin/env python3
# pylint: disable=too-many-public-methods
"""
Unit tests for check_compliance.py
"""

# built-ins
import logging
from unittest.mock import patch
from unittest import TestCase

# third party
from defusedxml import ElementTree
from requests.exceptions import HTTPError, Timeout, RequestException, TooManyRedirects

# custom
from tests import constants as test_constants
from veracode import check_compliance
from veracode.api import ResultsAPI

# Setup a logger
logging.getLogger()
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=FORMAT)
logging.raiseExceptions = True
LOG = logging.getLogger(__name__)


class TestVeracodeCheckCompliance(TestCase):
    """
    Test check_compliance.py
    """

    @patch("veracode.check_compliance.in_compliance")
    def test_check_compliance(self, mock_in_compliance):
        """
        Test the check_compliance function
        """
        # Return True when calling the check_compliance function with a valid
        # results_api with ignore_compliance_status set to True and
        # ignore_compliance_status is True
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        results_api.ignore_compliance_status = True
        mock_in_compliance.return_value = True
        self.assertTrue(check_compliance.check_compliance(results_api=results_api))

        # Return False when calling the check_compliance function with a valid
        # results_api with ignore_compliance_status set to False and
        # ignore_compliance_status is False
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        results_api.ignore_compliance_status = False
        mock_in_compliance.return_value = False
        self.assertFalse(check_compliance.check_compliance(results_api=results_api))

        # Return True when calling the check_compliance function with a valid
        # results_api with ignore_compliance_status set to True and
        # ignore_compliance_status is False
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        results_api.ignore_compliance_status = True
        mock_in_compliance.return_value = False
        self.assertTrue(check_compliance.check_compliance(results_api=results_api))

        # Return True when calling the check_compliance function with a valid
        # results_api with ignore_compliance_status set to False and
        # ignore_compliance_status is True
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        results_api.ignore_compliance_status = False
        mock_in_compliance.return_value = True
        self.assertTrue(check_compliance.check_compliance(results_api=results_api))

        # Return False after calling the check_compliance function with a valid
        # results_api with ignore_compliance_status set to False and
        # ignore_compliance_status is True, but in_compliance's mock raises a
        # ValueError when called
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        results_api.ignore_compliance_status = False
        mock_in_compliance.return_value = True
        mock_in_compliance.side_effect = ValueError
        self.assertFalse(check_compliance.check_compliance(results_api=results_api))

    @patch("veracode.check_compliance.get_policy_compliance_status")
    def test_in_compliance(self, mock_get_policy_compliance_status):
        """
        Test the in_compliance function
        """
        # Succeed when calling the in_compliance function with a valid
        # results_api and compliance_status has a mocked response of "Pass"
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        mock_get_policy_compliance_status.return_value = "Pass"
        self.assertTrue(check_compliance.in_compliance(results_api=results_api))

        # Return False when calling the in_compliance function with a valid
        # results_api and compliance_status has a mocked response of "Unknown"
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        mock_get_policy_compliance_status.return_value = "Unknown"
        self.assertRaises(
            ValueError, check_compliance.in_compliance, results_api=results_api
        )

        # Succeed when calling the in_compliance function with a valid
        # results_api and compliance_status has a mocked response of anything
        # but "Pass"
        #
        # https://analysiscenter.veracode.com/resource/2.0/applicationbuilds.xsd
        # and https://help.veracode.com/viewer/document/mo49_yYZJCUuKhwdE9WRFQ
        # for possible values
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        for value in [
            "Calculating...",
            "Not Assessed",
            "Did Not Pass",
            "Conditional Pass",
            "Under Vendor Review",
            "UNKNOWN VALUE!()&@%",
            300,
            7.12,
            results_api,
        ]:
            mock_get_policy_compliance_status.return_value = value
            self.assertFalse(check_compliance.in_compliance(results_api=results_api))

    @patch("veracode.check_compliance.get_latest_completed_build")
    def test_get_policy_compliance_status(self, mock_get_latest_completed_build):
        """
        Test the get_policy_compliance_status function
        """
        # Return a non-"Pass"ing string when calling the
        # get_policy_compliance_status function with a valid results_api and
        # get_latest_completed_build has a mocked response of "Did Not Pass"
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        mock_get_latest_completed_build.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS[
            "Element"
        ]
        self.assertEqual(
            check_compliance.get_policy_compliance_status(results_api=results_api),
            "Did Not Pass",
        )
        self.assertNotEqual(
            check_compliance.get_policy_compliance_status(results_api=results_api),
            "Pass",
        )

        # Return a "Pass"ing string when calling the
        # get_policy_compliance_status function with a valid results_api and
        # get_latest_completed_build has a mocked response that returns None
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        mock_get_latest_completed_build.return_value = None
        self.assertNotEqual(
            check_compliance.get_policy_compliance_status(results_api=results_api),
            "Pass",
        )

        # Return a non-"Pass"ing string when calling the
        # get_policy_compliance_status function with a valid results_api and
        # get_latest_completed_build has a mocked response that returns an
        # application with no build
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(
                app_name=test_constants.VALID_RESULTS_API["app_name"]
            )

        mock_get_latest_completed_build.return_value = (
            test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
                "Element"
            ]
        )

        self.assertEqual(
            check_compliance.get_policy_compliance_status(results_api=results_api),
            "Unknown",
        )
        self.assertNotEqual(
            check_compliance.get_policy_compliance_status(results_api=results_api),
            "Pass",
        )

    def test_get_latest_completed_build(self):
        """
        Test the get_latest_completed_build function
        """
        # Succeed when calling the get_latest_completed_build function with a
        # valid results_api and the http_get method returns an
        # ElementTree.Element which contains the provided app_id
        with patch.object(
            ResultsAPI,
            "http_get",
            return_value=test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
                "Element"
            ],
        ):
            with patch(
                "veracode.check_compliance.element_contains_error", return_value=False
            ):
                with patch("veracode.api.get_app_id", return_value="1337"):
                    results_api = ResultsAPI(app_name="TestApp")
                    output = check_compliance.get_latest_completed_build(
                        results_api=results_api
                    )
                    expected = ElementTree.fromstring(
                        b'<ns0:application xmlns:ns0="https://analysiscenter.veracode.com/schema/2.0/applicationbuilds" app_name="TestApp" app_id="1337" industry_vertical="Manufacturing" assurance_level="Very High" business_criticality="Very High" origin="Not Specified" modified_date="2019-08-13T14:00:10-04:00" cots="false" business_unit="Not Specified" tags="">\n      <ns0:customfield name="Custom 1" value="" />\n      <ns0:customfield name="Custom 2" value="" />\n      <ns0:customfield name="Custom 3" value="" />\n      <ns0:customfield name="Custom 4" value="" />\n      <ns0:customfield name="Custom 5" value="" />\n      <ns0:customfield name="Custom 6" value="" />\n      <ns0:customfield name="Custom 7" value="" />\n      <ns0:customfield name="Custom 8" value="" />\n      <ns0:customfield name="Custom 9" value="" />\n      <ns0:customfield name="Custom 10" value="" />\n      <ns0:build version="2019-10 Testing" build_id="1234321" submitter="Jon Zeolla" platform="Not Specified" lifecycle_stage="Deployed (In production and actively developed)" results_ready="true" policy_name="Veracode Recommended Medium" policy_version="1" policy_compliance_status="Pass" rules_status="Pass" grace_period_expired="false" scan_overdue="false">\n         <ns0:analysis_unit analysis_type="Static" published_date="2019-10-13T16:20:30-04:00" published_date_sec="1570998030" status="Results Ready" />\n      </ns0:build>\n   </ns0:application>\n'
                    )

                    self.assertEqual(
                        [output.tag, output.attrib], [expected.tag, expected.attrib]
                    )

            # However, return False when the element_contains_error function
            # returns True
            with patch(
                "veracode.check_compliance.element_contains_error", return_value=True
            ):
                self.assertFalse(
                    check_compliance.get_latest_completed_build(results_api=results_api)
                )

        # Return False when calling the get_latest_completed_build function
        # with a valid results_api and the http_get method returns an
        # ElementTree.Element which doesn't contain the provided app_id
        with patch.object(
            ResultsAPI,
            "http_get",
            return_value=test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
                "Element"
            ],
        ):
            with patch(
                "veracode.check_compliance.element_contains_error", return_value=False
            ):
                with patch("veracode.api.get_app_id", return_value="31337"):
                    results_api = ResultsAPI(app_name="TestApp")
                    output = check_compliance.get_latest_completed_build(
                        results_api=results_api
                    )
                    self.assertFalse(output)

        # Return False when calling the get_latest_completed_build function
        # with a valid results_api and the http_get method raises one of a
        # series of exceptions
        with patch("veracode.api.get_app_id", return_value="1337"):
            results_api = ResultsAPI(app_name="TestApp")
            for err in [
                HTTPError,
                ConnectionError,
                Timeout,
                TooManyRedirects,
                RequestException,
            ]:
                with patch(
                    "veracode.check_compliance.element_contains_error",
                    return_value=False,
                ):
                    with patch.object(ResultsAPI, "http_get", side_effect=err):
                        output = check_compliance.get_latest_completed_build(
                            results_api=results_api
                        )
                        self.assertFalse(output)
