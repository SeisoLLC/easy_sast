#!/usr/bin/env python3
# pylint: disable=too-many-public-methods, too-many-lines
"""
Unit tests for api.py
"""

# built-ins
import logging
import secrets
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

# third party
from defusedxml import ElementTree
from requests.exceptions import HTTPError, Timeout, RequestException, TooManyRedirects

# custom
from tests import constants as test_constants
from veracode import constants as veracode_constants
from veracode import api
from veracode.api import ResultsAPI, UploadAPI

# Setup a logger
logging.getLogger()
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=FORMAT)
logging.raiseExceptions = True
LOG = logging.getLogger(__name__)


class TestVeracodeApiFunctions(TestCase):
    """
    Test api.py's functions
    """

    ## validate tests
    # validate decorator on a Results API function
    @patch("veracode.api.validate_api")
    @patch("veracode.api.is_valid_attribute")
    def test_validate_decorator(self, mock_is_valid_attribute, mock_validate_api):
        """
        Test the validate decorator
        """
        # Prereqs to test the validate decorator with a valid ResultsAPI
        @api.validate
        def test_results_function(
            *, results_api: ResultsAPI, variable: int  # pylint: disable=unused-argument
        ) -> None:
            pass

        results_api = ResultsAPI(app_id=test_constants.VALID_RESULTS_API["app_id"])

        # Prereqs to test the validate decorator with a valid UploadAPI
        @api.validate
        def test_upload_function(
            *, upload_api: UploadAPI, variable: int  # pylint: disable=unused-argument
        ) -> None:
            pass

        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])

        # Test the validate decorator with a valid ResultsAPI
        for is_valid_attribute_return_value in [True, False]:
            for validate_api_side_effect in [None, KeyError, ValueError]:
                mock_is_valid_attribute.return_value = is_valid_attribute_return_value
                mock_validate_api.side_effect = validate_api_side_effect

                if validate_api_side_effect == KeyError:
                    self.assertRaises(
                        KeyError,
                        test_results_function,
                        results_api=results_api,
                        variable=123,
                    )
                elif validate_api_side_effect == ValueError:
                    self.assertRaises(
                        ValueError,
                        test_results_function,
                        results_api=results_api,
                        variable=123,
                    )
                elif not is_valid_attribute_return_value:
                    self.assertRaises(
                        ValueError,
                        test_results_function,
                        results_api=results_api,
                        variable=123,
                    )
                else:
                    self.assertIsNone(
                        test_results_function(results_api=results_api, variable=123)
                    )

        # Test the validate decorator with a valid ResultsAPI
        for is_valid_attribute_return_value in [True, False]:
            for validate_api_side_effect in [None, KeyError, ValueError]:
                mock_is_valid_attribute.return_value = is_valid_attribute_return_value
                mock_validate_api.side_effect = validate_api_side_effect

                if validate_api_side_effect == KeyError:
                    self.assertRaises(
                        KeyError,
                        test_upload_function,
                        upload_api=upload_api,
                        variable=123,
                    )
                elif validate_api_side_effect == ValueError:
                    self.assertRaises(
                        ValueError,
                        test_upload_function,
                        upload_api=upload_api,
                        variable=123,
                    )
                elif not is_valid_attribute_return_value:
                    self.assertRaises(
                        ValueError,
                        test_upload_function,
                        upload_api=upload_api,
                        variable=123,
                    )
                else:
                    self.assertIsNone(
                        test_upload_function(upload_api=upload_api, variable=123)
                    )

    ## parse_xml tests
    def test_parse_xml(self):
        """
        Test the parse_xml function
        """
        # Fail when attempting to call the parse_xml function, given that the
        # argument causes an exception to be raised
        self.assertRaises(
            ElementTree.ParseError,
            api.parse_xml,
            content=test_constants.XML_API_INVALID_RESPONSE_XML_ERROR["bytes"],
        )

        # Succeed when calling the parse_xml function with valid arguments
        output = api.parse_xml(
            content=test_constants.XML_API_VALID_RESPONSE_XML_ERROR["bytes"]
        )
        self.assertEqual(
            [output.tag, output.attrib],
            [
                test_constants.XML_API_VALID_RESPONSE_XML_ERROR["Element"].tag,
                test_constants.XML_API_VALID_RESPONSE_XML_ERROR["Element"].attrib,
            ],
        )

    ## element_contains_error tests
    def test_element_contains_error(self):
        """
        Test the element_contains_error function
        """
        # Succeed when calling the element_contains_error function, given an
        # argument which contains an error
        self.assertTrue(
            api.element_contains_error(
                parsed_xml=test_constants.XML_API_VALID_RESPONSE_XML_ERROR["Element"]
            )
        )

        # Return False when calling the element_contains_error function, given
        # an argument which doesn't contain an error
        self.assertFalse(
            api.element_contains_error(
                parsed_xml=test_constants.VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML[
                    "Element"
                ]
            )
        )

    ## http_request tests
    # http_request get 200
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_200(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and 200 response
        """
        # Succeed when calling the http_request function with valid arguments,
        # a verb="get", and a mocked 200 response
        mock_element_contains_error.return_value = False
        mock_get.return_value.content = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "bytes"
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.side_effect = HTTPError()
        mock_parse_xml.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "Element"
        ]

        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )
        response = api.http_request(verb="get", url=url)

        self.assertEqual(
            [response.tag, response.attrib],
            [
                test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
                    "Element"
                ].tag,
                test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
                    "Element"
                ].attrib,
            ],
        )

    # http_request get httperror
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_httperror(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and experience a
        variety of HTTPError failures based on the status_code
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="get", and a mocked failure response from the
        # list above
        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )

        for failure_code in [403, 404, 500]:
            mock_get.return_value.status_code = failure_code
            mock_get.return_value.raise_for_status.side_effect = HTTPError()

            self.assertRaises(
                HTTPError, api.http_request, verb="get", url=url,
            )

    # http_request get connectionerror
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_connectionerror(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and experience a
        ConnectionError
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="get", and a mocked ConnectionError
        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_get.side_effect = ConnectionError()

        self.assertRaises(
            ConnectionError, api.http_request, verb="get", url=url,
        )

    # http_request get requestexception
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_requestexception(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and experience a
        RequestException
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="get", and a mocked RequestException
        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_get.side_effect = RequestException()

        self.assertRaises(
            RequestException, api.http_request, verb="get", url=url,
        )

    # http_request get timeout
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_timeout(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and experience a
        Timeout
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="get", and a mocked Timeout
        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_get.side_effect = Timeout()

        self.assertRaises(
            Timeout, api.http_request, verb="get", url=url,
        )

    # http_request get toomanyredirects
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_toomanyredirects(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and experience a
        TooManyRedirects
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="get", and a mocked TooManyRedirects
        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_get.side_effect = TooManyRedirects()

        self.assertRaises(
            TooManyRedirects, api.http_request, verb="get", url=url,
        )

    # http_request get error body response
    @patch("requests.get")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_get_error_body_response(
        self, mock_element_contains_error, mock_parse_xml, mock_get
    ):
        """
        Test the http_request function with a get verb and experience an error
        in the response body
        """
        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="get", and a mocked element_contains_error of True
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.side_effect = HTTPError()
        mock_get.return_value.content = test_constants.VERACODE_ERROR_RESPONSE_XML[
            "bytes"
        ]
        mock_parse_xml.return_value = test_constants.VERACODE_ERROR_RESPONSE_XML[
            "Element"
        ]
        mock_element_contains_error.return_value = True

        endpoint = "getappbuilds.do"
        url = (
            test_constants.VALID_RESULTS_API["base_url"]
            + test_constants.VALID_RESULTS_API["version"][endpoint]
            + "/"
            + endpoint
        )

        self.assertRaises(
            RuntimeError, api.http_request, verb="get", url=url,
        )

    # http_request post 200
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_200(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and 200 response
        """
        # Succeed when calling the http_request function with valid arguments,
        # a verb="post", and a mocked 200 response
        mock_element_contains_error.return_value = False
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        mock_parse_xml.return_value = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "Element"
        ]

        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )
        response = api.http_request(
            verb="post", url=url, data=data, params=params, headers=headers,
        )

        self.assertEqual(
            [response.tag, response.attrib],
            [
                test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
                    "Element"
                ].tag,
                test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
                    "Element"
                ].attrib,
            ],
        )

    # http_request post httperror
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_httperror(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and experience a
        variety of HTTPError failures based on the status_code
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="post", and a mocked failure response from the
        # list above
        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        for failure_code in [403, 404, 500]:
            mock_post.return_value.status_code = failure_code
            mock_post.return_value.raise_for_status.side_effect = HTTPError()

            self.assertRaises(
                HTTPError,
                api.http_request,
                verb="post",
                url=url,
                data=data,
                params=params,
                headers=headers,
            )

    # http_request post connectionerror
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_connectionerror(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and experience a
        ConnectionError
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="post", and a mocked ConnectionError
        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_post.side_effect = ConnectionError()

        self.assertRaises(
            ConnectionError,
            api.http_request,
            verb="post",
            url=url,
            data=data,
            params=params,
            headers=headers,
        )

    # http_request post requestexception
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_requestexception(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and experience a
        RequestException
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="post", and a mocked RequestException
        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_post.side_effect = RequestException()

        self.assertRaises(
            RequestException,
            api.http_request,
            verb="post",
            url=url,
            data=data,
            params=params,
            headers=headers,
        )

    # http_request post timeout
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_timeout(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and experience a
        Timeout
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="post", and a mocked Timeout
        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_post.side_effect = Timeout()

        self.assertRaises(
            Timeout,
            api.http_request,
            verb="post",
            url=url,
            data=data,
            params=params,
            headers=headers,
        )

    # http_request post toomanyredirects
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_toomanyredirects(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and experience a
        TooManyRedirects
        """
        # These two should not be relevant, but keeping in case the test
        # follows an unexpected path
        mock_element_contains_error.return_value = False
        mock_parse_xml.return_value = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "Element"
        ]

        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="post", and a mocked TooManyRedirects
        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_post.side_effect = TooManyRedirects()

        self.assertRaises(
            TooManyRedirects,
            api.http_request,
            verb="post",
            url=url,
            data=data,
            params=params,
            headers=headers,
        )

    # http_request post error body response
    @patch("requests.post")
    @patch("veracode.api.parse_xml")
    @patch("veracode.api.element_contains_error")
    def test_http_request_post_error_body_response(
        self, mock_element_contains_error, mock_parse_xml, mock_post
    ):
        """
        Test the http_request function with a post verb and experience an error
        in the response body
        """
        # Fail when attempting to call the http_request function with valid
        # arguments, a verb="post", and a mocked element_contains_error of True
        app_id = test_constants.VALID_UPLOAD_API["app_id"]
        filename = test_constants.VALID_FILE["name"]
        data = test_constants.VALID_FILE["bytes"]
        params = {"app_id": app_id, "filename": filename}
        headers = {"Content-Type": "binary/octet-stream"}
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        mock_post.return_value.content = test_constants.VERACODE_ERROR_RESPONSE_XML[
            "bytes"
        ]
        mock_parse_xml.return_value = test_constants.VERACODE_ERROR_RESPONSE_XML[
            "Element"
        ]
        mock_element_contains_error.return_value = True

        self.assertRaises(
            RuntimeError,
            api.http_request,
            verb="post",
            url=url,
            data=data,
            params=params,
            headers=headers,
        )

    # http_request unsupported verb valueerror
    def test_http_request_unsupported_verb_valueerror(self):
        """
        Test the http_request function with a list of unsupported verbs
        """
        # Fail when attempting to call the http_request function with an invalid verb
        # as an argument
        endpoint = "uploadlargefile.do"
        url = (
            test_constants.VALID_UPLOAD_API["base_url"]
            + test_constants.VALID_UPLOAD_API["version"][endpoint]
            + "/"
            + endpoint
        )

        for verb in ["put", "patch", "delete", "options", "head", "connect", "trace"]:
            self.assertRaises(
                ValueError, api.http_request, verb=verb, url=url,
            )

    ## is_valid_attribute tests
    # base_url validation
    @patch("veracode.api.protocol_is_insecure")
    @patch("veracode.api.is_valid_netloc")
    def test_is_valid_attribute_base_url(
        self, mock_is_valid_netloc, mock_protocol_is_insecure
    ):
        """
        Test the base_url validation in is_valid_attribute
        """
        # Fail when calling the is_valid_attribute function with valid
        # arguments and a mocked protocol_is_insecure of True
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = True
        self.assertFalse(
            api.is_valid_attribute(
                key="base_url", value=test_constants.VALID_RESULTS_API["base_url"]
            )
        )

        # Succeed when calling the is_valid_attribute function with valid
        # arguments and a mocked protocol_is_insecure of False
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertTrue(
            api.is_valid_attribute(
                key="base_url", value=test_constants.VALID_RESULTS_API["base_url"]
            )
        )

        # Fail when calling the is_valid_attribute function with an invalid
        # argument that contains an empty netloc on the base_url
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertFalse(
            api.is_valid_attribute(
                key="base_url",
                value=test_constants.INVALID_RESULTS_API_MISSING_DOMAIN["base_url"],
            )
        )

        # Succeed when calling the is_valid_attribute function with a valid
        # argument, and an in_valid_netloc patched to always return True
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertTrue(
            api.is_valid_attribute(
                key="base_url", value=test_constants.VALID_RESULTS_API["base_url"],
            )
        )

        # Fail when calling the is_valid_attribute function with a valid
        # argument, and an in_valid_netloc patched to always return False
        mock_is_valid_netloc.return_value = False
        mock_protocol_is_insecure.return_value = False
        self.assertFalse(
            api.is_valid_attribute(
                key="base_url", value=test_constants.VALID_RESULTS_API["base_url"],
            )
        )

        # Succeed when calling the is_valid_attribute function with a missing
        # port (and thus valid) in the base_url
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertTrue(
            api.is_valid_attribute(
                key="base_url", value=test_constants.VALID_RESULTS_API["base_url"],
            )
        )

        # Succeed when calling the is_valid_attribute function with a valid
        # port in the base_url
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertTrue(
            api.is_valid_attribute(
                key="base_url",
                value=test_constants.VALID_RESULTS_API_WITH_PORT_IN_URL["base_url"],
            )
        )

        # Fail when calling the is_valid_attribute function with an invalid
        # port in the base_url
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertRaises(
            ValueError,
            api.is_valid_attribute,
            key="base_url",
            value=test_constants.INVALID_RESULTS_API_INVALID_PORT["base_url"],
        )

        # Fail when attempting to call the is_valid_attribute function with an
        # improperly formatted base_url dual to the double colon
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertRaises(
            ValueError,
            api.is_valid_attribute,
            key="base_url",
            value="https://example.com::443/testing/",
        )

        # Fail when calling the is_valid_attribute function with an empty path
        # in the base_url
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertFalse(
            api.is_valid_attribute(key="base_url", value="https://example.com/")
        )

        # Fail when calling the is_valid_attribute function with a base_url
        # that doesn't end with /
        mock_is_valid_netloc.return_value = True
        mock_protocol_is_insecure.return_value = False
        self.assertFalse(
            api.is_valid_attribute(key="base_url", value="https://example.com/thing")
        )

    # version validation
    def test_is_valid_attribute_version(self):
        """
        Test the version validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a version
        # that maps a string to a string
        self.assertTrue(api.is_valid_attribute(key="version", value={"test.do": "1.2"}))

        # Fail when calling the is_valid_attribute function with a version that
        # maps a string to a float
        self.assertFalse(api.is_valid_attribute(key="version", value={"test.do": 1.1}))

        # Fail when calling the is_valid_attribute function with a version that
        # maps a float to a string
        self.assertFalse(api.is_valid_attribute(key="version", value={3.141: "2.718"}))

        # Fail when calling the is_valid_attribute function with a version that
        # is a string
        self.assertFalse(api.is_valid_attribute(key="version", value="failure"))

    # endpoint validation
    def test_is_valid_attribute_endpoint(self):
        """
        Test the endpoint validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with an endpoint
        # that is a valid string
        self.assertTrue(
            api.is_valid_attribute(
                key="endpoint",
                value="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~",
            )
        )

        # Fail when calling the is_valid_attribute function with an endpoint
        # that is an empty string
        self.assertFalse(api.is_valid_attribute(key="endpoint", value=""))

        # Fail when calling the is_valid_attribute function with an endpoint
        # that is an invalid string
        self.assertFalse(api.is_valid_attribute(key="endpoint", value=";$"))

        # Fail when calling the is_valid_attribute function with an endpoint
        # that is an int
        self.assertFalse(api.is_valid_attribute(key="endpoint", value=7))

    # app_id validation
    def test_is_valid_attribute_app_id(self):
        """
        Test the app_id validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with an app_id
        # that is whole number represented as a string
        self.assertTrue(api.is_valid_attribute(key="app_id", value="54321"))

        # Fail when calling the is_valid_attribute function with an app_id that
        # is an int
        self.assertFalse(api.is_valid_attribute(key="app_id", value=54321))

        # Fail when calling the is_valid_attribute function with an app_id that
        # is a string but not a whole number
        self.assertFalse(api.is_valid_attribute(key="app_id", value="success"))

        # Fail when calling the is_valid_attribute function with an app_id that
        # is a float
        self.assertFalse(api.is_valid_attribute(key="app_id", value=543.21))

    # build_dir validation
    def test_is_valid_attribute_build_dir(self):
        """
        Test the build_dir validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a build_dir
        # that is a Path object
        self.assertTrue(
            api.is_valid_attribute(key="build_dir", value=Path("./path.pdb"))
        )

        # Fail when calling the is_valid_attribute function with a build_dir
        # that is a string
        self.assertFalse(api.is_valid_attribute(key="build_dir", value="./path.pdb"))

    # build_id validation
    def test_is_valid_attribute_build_id(self):
        """
        Test the build_id validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a build_id
        # that is a valid string
        self.assertTrue(
            api.is_valid_attribute(
                key="build_id",
                value="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~",
            )
        )

        # Fail when calling the is_valid_attribute function with a build_id
        # that is an empty string
        self.assertFalse(api.is_valid_attribute(key="build_id", value=""))

        # Succeed when calling the is_valid_attribute function with a build_id
        # that is an invalid string
        self.assertFalse(api.is_valid_attribute(key="build_id", value=";$"))

        # Fail when calling the is_valid_attribute function with a build_id
        # that is an int
        self.assertFalse(api.is_valid_attribute(key="build_id", value=7))

    # sandbox validation
    def test_is_valid_attribute_sandbox(self):
        """
        Test the sandbox validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a sandbox
        # that is whole number represented as a string
        self.assertTrue(api.is_valid_attribute(key="sandbox", value="54321"))

        # Succeed when calling the is_valid_attribute function with a sandbox
        # that is None (the default)
        self.assertTrue(api.is_valid_attribute(key="sandbox", value=None))

        # Fail when calling the is_valid_attribute function with a sandbox that
        # is an int
        self.assertFalse(api.is_valid_attribute(key="sandbox", value=54321))

        # Fail when calling the is_valid_attribute function with a sandbox that
        # is a string but not a whole number
        self.assertFalse(api.is_valid_attribute(key="sandbox", value="success"))

        # Fail when calling the is_valid_attribute function with a sandbox that
        # is a float
        self.assertFalse(api.is_valid_attribute(key="sandbox", value=543.21))

    # scan_all_nonfatal_top_level_modules validation
    def test_is_valid_attribute_scan_all_nonfatal_top_level_modules(self):
        """
        Test the scan_all_nonfatal_top_level_modules validation in
        is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a
        # scan_all_nonfatal_top_level_modules that is a bool
        self.assertTrue(
            api.is_valid_attribute(
                key="scan_all_nonfatal_top_level_modules", value=False
            )
        )

        # Fail when calling the is_valid_attribute function with a
        # scan_all_nonfatal_top_level_modules that is a string
        self.assertFalse(
            api.is_valid_attribute(
                key="scan_all_nonfatal_top_level_modules", value="string"
            )
        )

        # Succeed when calling the is_valid_attribute function with a
        # scan_all_nonfatal_top_level_modules that is an int
        self.assertFalse(
            api.is_valid_attribute(key="scan_all_nonfatal_top_level_modules", value=1)
        )

    # auto_scan validation
    def test_is_valid_attribute_auto_scan(self):
        """
        Test the auto_scan validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with an auto_scan
        # that is a bool
        self.assertTrue(api.is_valid_attribute(key="auto_scan", value=False))

        # Fail when calling the is_valid_attribute function with an auto_scan
        # that is a string
        self.assertFalse(api.is_valid_attribute(key="auto_scan", value="string"))

        # Succeed when calling the is_valid_attribute function with an auto_scan
        # that is an int
        self.assertFalse(api.is_valid_attribute(key="auto_scan", value=1))

    # api_key_id validation
    def test_is_valid_attribute_api_key_id(self):
        """
        Test the api_key_id validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with an
        # api_key_id that is 32 characters of hex
        self.assertTrue(
            api.is_valid_attribute(key="api_key_id", value=secrets.token_hex(16))
        )

        # Fail when calling the is_valid_attribute function with an api_key_id
        # that is a 32 digit int
        self.assertFalse(
            api.is_valid_attribute(
                key="api_key_id", value=12345678901234567890123456789012
            )
        )

        # Fail when calling the is_valid_attribute function with an api_key_id
        # that is a 32 character string but contains non-hex characters
        self.assertFalse(
            api.is_valid_attribute(
                key="api_key_id", value="a" * 15 + "z" + "b" * 15 + "g"
            )
        )

    # api_key_secret validation
    def test_is_valid_attribute_api_key_secret(self):
        """
        Test the api_key_secret validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with an
        # api_key_secret that is 128 characters of hex
        self.assertTrue(
            api.is_valid_attribute(key="api_key_secret", value=secrets.token_hex(64))
        )

        # Fail when calling the is_valid_attribute function with an
        # api_key_secret that is 127 characters of hex
        self.assertFalse(
            api.is_valid_attribute(
                key="api_key_secret", value=secrets.token_hex(63) + "0"
            )
        )

        # Fail when calling the is_valid_attribute function with an
        # api_key_secret that is a 128 character string which contains non-hex
        # characters
        self.assertFalse(
            api.is_valid_attribute(
                key="api_key_secret", value=secrets.token_hex(63) + "zz"
            )
        )

    # ignore_compliance_status validation
    def test_is_valid_attribute_ignore_compliance_status(self):
        """
        Test the ignore_compliance_status validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with an
        # ignore_compliance_status that is a bool
        self.assertTrue(
            api.is_valid_attribute(key="ignore_compliance_status", value=False)
        )

        # Fail when calling the is_valid_attribute function with an
        # ignore_compliance_status that is a string
        self.assertFalse(
            api.is_valid_attribute(key="ignore_compliance_status", value="string")
        )

        # Succeed when calling the is_valid_attribute function with an
        # ignore_compliance_status that is an int
        self.assertFalse(
            api.is_valid_attribute(key="ignore_compliance_status", value=1)
        )

    # loglevel validation
    def test_is_valid_attribute_loglevel(self):
        """
        Test the loglevel validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a loglevel
        # that is an allowed log level, appropriately formatted
        for log_level in veracode_constants.ALLOWED_LOG_LEVELS:
            self.assertTrue(api.is_valid_attribute(key="loglevel", value=log_level))

        # Fail when calling the is_valid_attribute function with a loglevel
        # that is a lowercase version of an allowed log level
        for log_level in veracode_constants.ALLOWED_LOG_LEVELS:
            self.assertFalse(
                api.is_valid_attribute(key="loglevel", value=log_level.casefold())
            )

        # Fail when calling the is_valid_attribute function with a loglevel
        # that is an int
        self.assertFalse(api.is_valid_attribute(key="loglevel", value=20))

        # Fail when calling the is_valid_attribute function with a loglevel
        # that is both an int and a non-existant log level
        self.assertFalse(api.is_valid_attribute(key="loglevel", value=1020384))

    # workflow validation
    def test_is_valid_attribute_workflow(self):
        """
        Test the workflow validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a workflow
        # that is a list of allowed workflows
        self.assertTrue(
            api.is_valid_attribute(
                key="workflow", value=list(veracode_constants.SUPPORTED_WORKFLOWS)
            )
        )

        # Fail when calling the is_valid_attribute function with a workflow
        # that is a set of allowed workflows
        self.assertFalse(
            api.is_valid_attribute(
                key="workflow", value=veracode_constants.SUPPORTED_WORKFLOWS
            )
        )

        # Fail when calling the is_valid_attribute function with a workflow
        # that is a list that contains an unsupported workflow mixed in with
        # supported workflows
        invalid_workflow = (
            list(veracode_constants.SUPPORTED_WORKFLOWS)
            + ["unsupported_workflow"]
            + list(veracode_constants.SUPPORTED_WORKFLOWS)
        )
        self.assertFalse(api.is_valid_attribute(key="workflow", value=invalid_workflow))

    # verb validation
    def test_is_valid_attribute_verb(self):
        """
        Test the verb validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a verb that
        # is an allowed verb, appropriately formatted
        for verb in veracode_constants.SUPPORTED_VERBS:
            self.assertTrue(api.is_valid_attribute(key="verb", value=verb))

        # Fail when calling the is_valid_attribute function with a verb that
        # is not an allowed verb
        self.assertFalse(api.is_valid_attribute(key="verb", value=123.2))

        # Fail when calling the is_valid_attribute function with a verb that
        # is not an allowed verb
        for verb in ["put", "patch", "delete", "options", "head", "connect", "trace"]:
            self.assertFalse(api.is_valid_attribute(key="verb", value=verb))

    # catch-all validation
    def test_is_valid_attribute_catch_all(self):
        """
        Test the catch-all validation in is_valid_attribute
        """
        # Succeed when calling the is_valid_attribute function with a key that
        # is not handled
        self.assertTrue(
            api.is_valid_attribute(key="ajfoanweofkwmeofmow", value="alksmfo")
        )

    ## configure_environment tests
    def test_configure_environment(self):
        """
        Test the configure_environment function
        """
        invalid_api_key_id = secrets.token_hex(15) + "zZ"
        invalid_api_key_secret = secrets.token_hex(63) + "zZ"

        # Succeed when calling the configure_environment function with a valid
        # api_key_id and api_key_secret, and no pre-existing environment
        # variables
        values = {}
        with patch.dict("os.environ", values=values, clear=True):
            self.assertIsNone(
                api.configure_environment(
                    api_key_id=test_constants.VALID_RESULTS_API["api_key_id"],
                    api_key_secret=test_constants.VALID_RESULTS_API["api_key_secret"],
                )
            )

        # Succeed when calling the configure_environment function with a valid
        # api_key_id and api_key_secret, even though the VERACODE_API_KEY_ID
        # and VERACODE_API_KEY_SECRET environment variables are currently set,
        # and do not match the provided values
        values = {
            "VERACODE_API_KEY_ID": invalid_api_key_id,
            "VERACODE_API_KEY_SECRET": invalid_api_key_secret,
        }
        with patch.dict("os.environ", values=values, clear=True):
            self.assertIsNone(
                api.configure_environment(
                    api_key_id=test_constants.VALID_RESULTS_API["api_key_id"],
                    api_key_secret=test_constants.VALID_RESULTS_API["api_key_secret"],
                )
            )

        # Succeed when calling the configure_environment function with a valid
        # api_key_id and api_key_secret, even though the VERACODE_API_KEY_ID
        # and VERACODE_API_KEY_SECRET environment variables are currently set,
        # and match the provided values
        values = {
            "VERACODE_API_KEY_ID": test_constants.VALID_RESULTS_API["api_key_id"],
            "VERACODE_API_KEY_SECRET": test_constants.VALID_RESULTS_API[
                "api_key_secret"
            ],
        }
        with patch.dict("os.environ", values=values, clear=True):
            self.assertIsNone(
                api.configure_environment(
                    api_key_id=test_constants.VALID_RESULTS_API["api_key_id"],
                    api_key_secret=test_constants.VALID_RESULTS_API["api_key_secret"],
                )
            )

        # Fail when calling the configure_environment function with an invalid
        # api_key_id and a valid api_key_secret due to the validate decorator
        self.assertRaises(
            ValueError,
            api.configure_environment,
            api_key_id=invalid_api_key_id,
            api_key_secret=test_constants.VALID_RESULTS_API["api_key_secret"],
        )

        # Fail when calling the configure_environment function with a valid
        # api_key_id and an invalid api_key_secret due to the validate
        # decorator
        self.assertRaises(
            ValueError,
            api.configure_environment,
            api_key_id=test_constants.VALID_RESULTS_API["api_key_id"],
            api_key_secret=invalid_api_key_secret,
        )

        # Fail when calling the configure_environment function with an invalid
        # api_key_id and an invalid api_key_secret due to the validate
        # decorator
        self.assertRaises(
            ValueError,
            api.configure_environment,
            api_key_id=invalid_api_key_id,
            api_key_secret=invalid_api_key_secret,
        )

    ## validate_api tests
    def test_validate_api(self):
        """
        Test the validate_api function
        """
        # Succeed when calling the validate_api function, given a
        # properly configured ResultsAPI object
        results_api = ResultsAPI(app_id=test_constants.VALID_RESULTS_API["app_id"])
        self.assertIsNone(api.validate_api(api=results_api))

        # Succeed when calling the validate_api function, given a
        # properly configured UploadAPI object
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        self.assertIsNone(api.validate_api(api=upload_api))

        # Fail when attempting to call the validate_api function, given
        # an improperly configured results_api due to an invalid property
        results_api._app_id = test_constants.INVALID_RESULTS_API_INCORRECT_APP_ID[  # pylint: disable=protected-access
            "app_id"
        ]
        self.assertRaises(
            ValueError, api.validate_api, api=results_api,
        )

        # Fail when attempting to call the validate_api function, given
        # an improperly configured upload_api due to an invalid property
        upload_api._base_url = test_constants.INVALID_UPLOAD_API_MISSING_DOMAIN[  # pylint: disable=protected-access
            "base_url"
        ]
        self.assertRaises(
            ValueError, api.validate_api, api=upload_api,
        )

    ## protocol_is_insecure tests
    def test_protocol_is_insecure(self):
        """
        Test the protocol_is_insecure function
        """
        # protocol_is_insecure must be passed the protocol
        self.assertRaises(TypeError, api.protocol_is_insecure)

        # http is insecure
        output = api.protocol_is_insecure(protocol="http")
        self.assertTrue(output)

        # https is secure
        output = api.protocol_is_insecure(protocol="https")
        self.assertFalse(output)

    ## is_null tests
    def test_is_null(self):
        """
        Test the is_null function
        """
        # is_null must be passed a value
        self.assertRaises(TypeError, api.is_null)

        # Python's null equivalent is None
        output = api.is_null(value=None)
        self.assertTrue(output)

        # An empty string is not null
        output = api.is_null(value="")
        self.assertFalse(output)

        # A tuple is not null
        output = api.is_null(value=(1, "2"))
        self.assertFalse(output)

        # A dict is not null
        output = api.is_null(value={"a": {"Test": 123}})
        self.assertFalse(output)

        # An int is not null
        output = api.is_null(value=12321)
        self.assertFalse(output)

        # A string is not null
        output = api.is_null(value="thisisonlyatest")
        self.assertFalse(output)

        # A list is not null
        output = api.is_null(value=["a", "b", "c"])
        self.assertFalse(output)

        # A set is not null
        output = api.is_null(value={"1", 2})
        self.assertFalse(output)

    ## is_valid_netloc tests
    def test_is_valid_netloc(self):
        """
        Test the is_valid_netloc function
        """
        # Succeed when calling the is_valid_netloc function with a legal
        # netloc, containing no subdomains
        self.assertTrue(api.is_valid_netloc(netloc="example.com"))

        # Succeed when calling the is_valid_netloc function with a legal
        # netloc, containing numerous subdomains
        self.assertTrue(
            api.is_valid_netloc(netloc="i.love.to.use.subdomains.example.com")
        )

        # Succeed when calling the is_valid_netloc function with a legal netloc
        # due to a 63 character (max valid length) subdomain
        self.assertTrue(api.is_valid_netloc(netloc="a" * 63 + ".example.com"))

        # Succeed when calling the is_valid_netloc function with a valid
        # port in the netloc
        self.assertTrue(api.is_valid_netloc(netloc="example.com:443"))

        # Fail when calling the is_valid_netloc function with a legal netloc,
        # containing no subdomains, but a user/pass specified in the url
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@example.com"))

        # Fail when attempting to call the is_valid_netloc function with an
        # illegal netloc based on the characters used
        self.assertFalse(api.is_valid_netloc(netloc="$$"))

        # Fail when attempting to call the is_valid_netloc function with an
        # illegal netloc due to a 64 character (invalid) subdomain
        self.assertFalse(api.is_valid_netloc(netloc="a" * 64 + ".example.com"))

        # Fail when attempting to call the is_valid_netloc function with a
        # non-string value
        self.assertFalse(api.is_valid_netloc(netloc=12321))

        # Fail when calling the is_valid_netloc function with an invalid port
        # in the netloc
        self.assertFalse(api.is_valid_netloc(netloc="example.com:65536"))

        # Fail when calling the is_valid_netloc function with an IPv4 address
        # as the netloc, as it is not currently supported
        self.assertFalse(api.is_valid_netloc(netloc="192.0.2.1"))
        self.assertFalse(api.is_valid_netloc(netloc="192.0.2.1:443"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@192.0.2.1"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@192.0.2.1:443"))

        # Fail when calling the is_valid_netloc function with a compressed IPv6
        # address as the netloc, as it is not currently supported
        self.assertFalse(api.is_valid_netloc(netloc="2001:db8::1"))
        self.assertFalse(api.is_valid_netloc(netloc="2001:db8::1:443"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@2001:db8::1"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@2001:db8::1:443"))
        self.assertFalse(api.is_valid_netloc(netloc="[2001:db8::1]"))
        self.assertFalse(api.is_valid_netloc(netloc="[2001:db8::1]:443"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@[2001:db8::1]"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@[2001:db8::1]:443"))

        # Fail when calling the is_valid_netloc function with an IPv6 address
        # as the netloc, as it is not currently supported
        self.assertFalse(api.is_valid_netloc(netloc="2001:db8:0:0:0:0:0:1"))
        self.assertFalse(api.is_valid_netloc(netloc="2001:db8:0:0:0:0:0:1:443"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@2001:db8:0:0:0:0:0:1"))
        self.assertFalse(
            api.is_valid_netloc(netloc="user:pass@2001:db8:0:0:0:0:0:1:443")
        )
        self.assertFalse(api.is_valid_netloc(netloc="[2001:db8:0:0:0:0:0:1]"))
        self.assertFalse(api.is_valid_netloc(netloc="[2001:db8:0:0:0:0:0:1]:443"))
        self.assertFalse(api.is_valid_netloc(netloc="user:pass@[2001:db8:0:0:0:0:0:1]"))
        self.assertFalse(
            api.is_valid_netloc(netloc="user:pass@[2001:db8:0:0:0:0:0:1]:443")
        )
