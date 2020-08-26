#!/usr/bin/env python3
# pylint: disable=too-many-public-methods
"""
Unit tests for submit_artifacts.py
"""

# built-ins
import logging
from pathlib import Path
from unittest.mock import patch, mock_open
from unittest import TestCase

# third party
from requests.exceptions import HTTPError

# custom
from tests import constants as test_constants
from veracode import submit_artifacts
from veracode.api import UploadAPI, SandboxAPI

# Setup a logger
logging.getLogger()
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=FORMAT)
logging.raiseExceptions = True
LOG = logging.getLogger(__name__)


class TestSubmitArtifacts(TestCase):
    """
    Test submit_artifacts.py
    """

    def test_create_build(self):
        """
        Test the create_build function
        """
        # Test the create_build function when the api call gets a valid response
        with patch.object(
            UploadAPI,
            "http_post",
            return_value=test_constants.VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML[
                "Element"
            ],
        ):
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                # Policy scan, no error in response body
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                self.assertTrue(submit_artifacts.create_build(upload_api=upload_api))

                # Sandbox scan, no error in response body
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                upload_api.sandbox_id = "12345"
                self.assertTrue(submit_artifacts.create_build(upload_api=upload_api))

            # Fail when the create_build function gets a response containing an
            # error in the response body
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=True
            ):
                # Policy scan, response body contains error
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                self.assertFalse(submit_artifacts.create_build(upload_api=upload_api))

                # Sandbox scan, response body contains error
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                upload_api.sandbox_id = "12345"
                self.assertFalse(submit_artifacts.create_build(upload_api=upload_api))

        # Fail when calling the create_build function and the api call gets a
        # mocked error message response and a mocked side effect of HTTPError
        with patch.object(
            UploadAPI,
            "http_post",
            return_value=test_constants.VERACODE_ERROR_RESPONSE_XML["Element"],
            side_effect=HTTPError(),
        ):
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                # Policy scan, no error in response body
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                self.assertFalse(submit_artifacts.create_build(upload_api=upload_api))

                # Sandbox scan, no error in response body
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                upload_api.sandbox_id = "12345"
                self.assertFalse(submit_artifacts.create_build(upload_api=upload_api))

    def test_begin_prescan(self):
        """
        Test the begin_prescan function
        """
        # Succeed when calling the begin_prescan function and the api call gets
        # a valid response
        with patch.object(
            UploadAPI,
            "http_post",
            return_value=test_constants.VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML[
                "Element"
            ],
        ):
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                # Policy scan
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                self.assertTrue(submit_artifacts.begin_prescan(upload_api=upload_api))

                # Sandbox scan
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                upload_api.sandbox_id = "12345"
                self.assertTrue(submit_artifacts.begin_prescan(upload_api=upload_api))

            # Fail when the begin_prescan function gets a response containing an
            # error in the response body
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=True
            ):
                # Policy scan
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                self.assertFalse(submit_artifacts.begin_prescan(upload_api=upload_api))

                # Sandbox scan
                upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
                upload_api.sandbox_id = "12345"
                self.assertFalse(submit_artifacts.begin_prescan(upload_api=upload_api))

        # Fail when calling the begin_prescan function and the api call gets a
        # mocked side effect of HTTPError
        with patch.object(UploadAPI, "http_post", side_effect=HTTPError()):
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                # Policy scan
                upload_api = UploadAPI(app_id="31337")
                self.assertFalse(submit_artifacts.begin_prescan(upload_api=upload_api))

                # Sandbox scan
                upload_api = UploadAPI(app_id="31337")
                upload_api.sandbox_id = "12345"
                self.assertFalse(submit_artifacts.begin_prescan(upload_api=upload_api))

    def test_filter_file_file_is_in_whitelist(self):
        """Test the filter_file function with a valid file suffix"""
        for filename in test_constants.VALID_FILE["names"]:
            valid_artifact = Path("/path/" + filename)
            self.assertTrue(submit_artifacts.filter_file(artifact=valid_artifact))

    def test_filter_file_file_is_not_in_whitelist(self):
        """Test the filter_file function with an invalid file suffix"""
        for filename in test_constants.INVALID_FILE["names"]:
            invalid_artifact = Path("/path/" + filename)
            self.assertFalse(submit_artifacts.filter_file(artifact=invalid_artifact))

    @patch("veracode.submit_artifacts.element_contains_error")
    def test_upload_large_file(self, mock_element_contains_error):
        """
        Test the upload_large_file function
        """
        mock_element_contains_error.return_value = False
        # Succeed when calling the upload_large_file function and the api call
        # gets a valid response
        with patch.object(
            UploadAPI,
            "http_post",
            return_value=test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
                "bytes"
            ],
        ):
            # Policy scan
            upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
            valid_artifact = test_constants.VALID_FILE["Path"]

            with patch(
                "veracode.submit_artifacts.open",
                new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
            ):
                self.assertTrue(
                    submit_artifacts.upload_large_file(
                        upload_api=upload_api, artifact=valid_artifact
                    )
                )

            # Sandbox scan
            upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
            upload_api.sandbox_id = "12345"
            valid_artifact = test_constants.VALID_FILE["Path"]

            with patch(
                "veracode.submit_artifacts.open",
                new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
            ):
                self.assertTrue(
                    submit_artifacts.upload_large_file(
                        upload_api=upload_api, artifact=valid_artifact
                    )
                )

        # Fail when calling the upload_large_file function and the api call
        # raises a HTTPError
        with patch.object(
            UploadAPI,
            "http_post",
            return_value=test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
                "bytes"
            ],
            side_effect=HTTPError(),
        ):
            # Policy scan
            upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
            valid_artifact = test_constants.VALID_FILE["Path"]

            with patch(
                "veracode.submit_artifacts.open",
                new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
            ):
                self.assertRaises(
                    HTTPError,
                    submit_artifacts.upload_large_file,
                    upload_api=upload_api,
                    artifact=valid_artifact,
                )

            # Sandbox scan
            upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
            upload_api.sandbox_id = "12345"
            valid_artifact = test_constants.VALID_FILE["Path"]

            with patch(
                "veracode.submit_artifacts.open",
                new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
            ):
                self.assertRaises(
                    HTTPError,
                    submit_artifacts.upload_large_file,
                    upload_api=upload_api,
                    artifact=valid_artifact,
                )

    def test_get_sandbox_id(self):
        """
        Test the get_sandbox_id function
        """
        # Succeed when calling the get_sandbox_id function and the api call
        # gets a valid response
        with patch.object(
            SandboxAPI,
            "http_get",
            return_value=test_constants.VALID_SANDBOX_GETSANDBOXLIST_API_RESPONSE_XML[
                "Element"
            ],
        ):
            sandbox_api = SandboxAPI(app_id="31337", sandbox_name="Project Security")
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertEqual(
                    submit_artifacts.get_sandbox_id(sandbox_api=sandbox_api),
                    "111111111",
                )

            # Raise a RuntimeError when element_contains_error returns True
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=True
            ):
                self.assertRaises(
                    RuntimeError,
                    submit_artifacts.get_sandbox_id,
                    sandbox_api=sandbox_api,
                )

        # Return None when calling the get_sandbox_id function and the api call
        # gets a valid response, but does not contain the requested
        # sandbox_name
        with patch.object(
            SandboxAPI,
            "http_get",
            return_value=test_constants.VALID_SANDBOX_GETSANDBOXLIST_API_RESPONSE_XML[
                "Element"
            ],
        ):
            sandbox_api = SandboxAPI(
                app_id="31337", sandbox_name="Unknown Sandbox Name"
            )
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertIsNone(
                    submit_artifacts.get_sandbox_id(sandbox_api=sandbox_api)
                )

    def test_create_sandbox(self):
        """
        Test the create_sandbox function
        """
        # Succeed when calling the create_sandbox function and the api call
        # gets a valid response
        with patch.object(
            SandboxAPI,
            "http_post",
            return_value=test_constants.VALID_SANDBOX_CREATESANDBOX_API_RESPONSE_XML[
                "Element"
            ],
        ):
            sandbox_api = SandboxAPI(app_id="31337", sandbox_name="Project Security")
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertEqual(
                    submit_artifacts.create_sandbox(sandbox_api=sandbox_api), "1111111"
                )

            # Raise a RuntimeError when element_contains_error returns True
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=True
            ):
                self.assertRaises(
                    RuntimeError,
                    submit_artifacts.create_sandbox,
                    sandbox_api=sandbox_api,
                )

        # Raise a RuntimeError when calling the create_sandbox function and the
        # api call gets a response, but does not contain the requested
        # sandbox_name
        with patch.object(
            SandboxAPI,
            "http_post",
            return_value=test_constants.INVALID_SANDBOX_CREATESANDBOX_API_RESPONSE_XML_NO_SANDBOX[
                "Element"
            ],
        ):
            sandbox_api = SandboxAPI(app_id="31337", sandbox_name="Project Security")
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertRaises(
                    RuntimeError,
                    submit_artifacts.create_sandbox,
                    sandbox_api=sandbox_api,
                )

    def test_cancel_build(self):
        """
        Test the cancel_build function
        """
        # Succeed when calling the cancel_build function and the api call gets
        # a valid response
        with patch.object(
            UploadAPI,
            "http_get",
            return_value=test_constants.VALID_UPLOAD_API_DELETEBUILD_RESPONSE_XML[
                "Element"
            ],
        ):
            # Policy scan
            upload_api = UploadAPI(app_id="31337")
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertTrue(submit_artifacts.cancel_build(upload_api=upload_api))

            # Sandbox scan
            upload_api.sandbox_id = "12345"
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertTrue(submit_artifacts.cancel_build(upload_api=upload_api))

            # Return False when element_contains_error returns True
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=True
            ):
                self.assertFalse(submit_artifacts.cancel_build(upload_api=upload_api))

        # Return False when calling the cancel_build function and the api call
        # raises a ConnectionError
        with patch.object(
            UploadAPI,
            "http_get",
            return_value=test_constants.VALID_UPLOAD_API_DELETEBUILD_RESPONSE_XML[
                "Element"
            ],
            side_effect=ConnectionError,
        ):
            upload_api = UploadAPI(app_id="31337")
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertFalse(submit_artifacts.cancel_build(upload_api=upload_api))

    def test_setup_scan_prereqs(self):
        """
        Test the setup_scan_prereqs function
        """
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        ## Policy Scan
        # Successful create build
        with patch("veracode.submit_artifacts.create_build", return_value=True):
            with patch(
                "veracode.submit_artifacts.check_if_build_exists", return_value=True
            ):
                self.assertTrue(
                    submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                )

        # Unsuccessful create build
        with patch("veracode.submit_artifacts.create_build", return_value=False):
            with patch(
                "veracode.submit_artifacts.check_if_build_exists", return_value=True
            ):
                self.assertFalse(
                    submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                )

        ## Sandbox Scan
        upload_api.sandbox_id = "12345"
        # Successful create build
        with patch("veracode.submit_artifacts.create_build", return_value=True):
            with patch(
                "veracode.submit_artifacts.check_if_build_exists", return_value=True
            ):
                self.assertTrue(
                    submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                )

        # Build in progress, try to cancel and recreate
        with patch(
            "veracode.submit_artifacts.check_if_build_exists", return_value=False
        ):
            # Unsuccessful create build
            with patch("veracode.submit_artifacts.create_build", return_value=True):
                # cancel_build returns True, create_build returns False, return False
                with patch("veracode.submit_artifacts.cancel_build", return_value=True):
                    self.assertTrue(
                        submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                    )

                # cancel_build returns False, return False
                with patch(
                    "veracode.submit_artifacts.cancel_build", return_value=False
                ):
                    self.assertFalse(
                        submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                    )

        with patch(
            "veracode.submit_artifacts.check_if_build_exists", return_value=True
        ):
            # Unsuccessful create build
            with patch("veracode.submit_artifacts.create_build", return_value=False):
                # cancel_build returns True, create_build returns False, return False
                with patch("veracode.submit_artifacts.cancel_build", return_value=True):
                    self.assertFalse(
                        submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                    )

                # cancel_build returns False, return False
                with patch(
                    "veracode.submit_artifacts.cancel_build", return_value=False
                ):
                    self.assertFalse(
                        submit_artifacts.setup_scan_prereqs(upload_api=upload_api)
                    )

    def test_check_if_build_exists(self):
        """
        Test the check_if_build_exists function
        """
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])

        with patch.object(
            UploadAPI,
            "http_get",
            return_value=test_constants.VALID_UPLOAD_API_GETBUILDLIST_MISSING_BUILDID_IN_RESPONSE_XML[
                "Element"
            ],
        ):
            # Succeed when no existing build IDs are present
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertTrue(
                    submit_artifacts.check_if_build_exists(upload_api=upload_api)
                )

            # Raise a RuntimeError when element_contains_error returns True
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=True
            ):
                self.assertRaises(
                    RuntimeError,
                    submit_artifacts.check_if_build_exists,
                    upload_api=upload_api,
                )

        ## Create Sandbox Scan and have existing build ID
        upload_api.sandbox_id = "12345"
        with patch.object(
            UploadAPI,
            "http_get",
            return_value=test_constants.VALID_UPLOAD_API_GETBUILDLIST_BUILDID_IN_RESPONSE_XML[
                "Element"
            ],
        ):
            # Fail when build already exists
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                self.assertFalse(
                    submit_artifacts.check_if_build_exists(upload_api=upload_api)
                )

        # Raise RuntimeError when HTTPError occurs
        with patch("veracode.api.VeracodeXMLAPI.http_get") as mock_http:
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                mock_http.side_effect = HTTPError()
                self.assertRaises(
                    RuntimeError,
                    submit_artifacts.check_if_build_exists,
                    upload_api=upload_api,
                )

        # Raise RuntimeError when HTTPError occurs
        with patch("veracode.api.VeracodeXMLAPI.http_get") as mock_http:
            with patch(
                "veracode.submit_artifacts.element_contains_error", return_value=False
            ):
                mock_http.side_effect = HTTPError()
                self.assertRaises(
                    RuntimeError,
                    submit_artifacts.check_if_build_exists,
                    upload_api=upload_api,
                )

    @patch("veracode.submit_artifacts.begin_prescan")
    @patch("veracode.submit_artifacts.upload_large_file")
    @patch("veracode.submit_artifacts.filter_file")
    @patch("veracode.submit_artifacts.setup_scan_prereqs")
    @patch("pathlib.Path.iterdir")
    @patch("veracode.submit_artifacts.create_sandbox")
    @patch("veracode.submit_artifacts.get_sandbox_id")
    def test_submit_artifacts(  # pylint: disable=too-many-arguments, too-many-statements
        self,
        mock_get_sandbox_id,
        mock_create_sandbox,
        mock_iterdir,
        mock_setup_scan_prereqs,
        mock_filter_file,
        mock_upload_large_file,
        mock_begin_prescan,
    ):
        """
        Test the submit_artifacts function
        """
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        sandbox_api = SandboxAPI(
            app_id=test_constants.VALID_SANDBOX_API["app_id"],
            sandbox_name=test_constants.VALID_SANDBOX_API["sandbox_name"],
        )

        def iterdir_generator_valid():
            f = test_constants.VALID_FILE["Path"]
            yield f

        def iterdir_generator_invalid():
            f = test_constants.INVALID_FILE["Path"]
            yield f

        ## Testing with sandbox_api set
        # Return True if sandbox_api is set, the sandbox was already created,
        # and everything else follows the Happy Path
        mock_get_sandbox_id.return_value = test_constants.VALID_SANDBOX_API[
            "sandbox_id"
        ]
        mock_create_sandbox.return_value = None  # Unused
        mock_setup_scan_prereqs.return_value = True
        mock_iterdir.return_value = iterdir_generator_valid()
        mock_filter_file.return_value = True
        mock_upload_large_file.return_value = True
        mock_begin_prescan.return_value = True
        self.assertTrue(
            submit_artifacts.submit_artifacts(
                upload_api=upload_api, sandbox_api=sandbox_api
            )
        )

        # Return True if sandbox_api is set, the sandbox wasn't yet created in
        # Veracode, and everything else follows the Happy Path
        mock_get_sandbox_id.return_value = None
        mock_create_sandbox.return_value = test_constants.VALID_SANDBOX_API[
            "sandbox_id"
        ]
        mock_setup_scan_prereqs.return_value = True
        mock_iterdir.return_value = iterdir_generator_valid()
        mock_filter_file.return_value = True
        mock_upload_large_file.return_value = True
        mock_begin_prescan.return_value = True
        self.assertTrue(
            submit_artifacts.submit_artifacts(
                upload_api=upload_api, sandbox_api=sandbox_api
            )
        )

        # Return False if sandbox_api is set, and get_sandbox_id raises a
        # RuntimeError
        with patch(
            "veracode.submit_artifacts.get_sandbox_id", side_effect=RuntimeError
        ):
            mock_get_sandbox_id.return_value = None
            mock_create_sandbox.return_value = None  # Unused
            mock_setup_scan_prereqs.return_value = True  # Unused
            mock_iterdir.return_value = iterdir_generator_valid()  # Unused
            mock_filter_file.return_value = True  # Unused
            mock_upload_large_file.return_value = True  # Unused
            mock_begin_prescan.return_value = True  # Unused
            self.assertFalse(
                submit_artifacts.submit_artifacts(
                    upload_api=upload_api, sandbox_api=sandbox_api
                )
            )

        # Return False if sandbox_api is set, get_sandbox_id returns None, but
        # create_sandbox raises a RuntimeError
        with patch(
            "veracode.submit_artifacts.create_sandbox", side_effect=RuntimeError
        ):
            mock_get_sandbox_id.return_value = None
            mock_create_sandbox.return_value = None
            mock_setup_scan_prereqs.return_value = True  # Unused
            mock_iterdir.return_value = iterdir_generator_valid()  # Unused
            mock_filter_file.return_value = True  # Unused
            mock_upload_large_file.return_value = True  # Unused
            mock_begin_prescan.return_value = True  # Unused
            self.assertFalse(
                submit_artifacts.submit_artifacts(
                    upload_api=upload_api, sandbox_api=sandbox_api
                )
            )

        ## Testing without sandbox_api set
        # Return True if sandbox_api isn't set and everything follows the Happy
        # Path
        mock_get_sandbox_id.return_value = None  # Unused
        mock_create_sandbox.return_value = None  # Unused
        mock_setup_scan_prereqs.return_value = True
        mock_iterdir.return_value = iterdir_generator_valid()
        mock_filter_file.return_value = True
        mock_upload_large_file.return_value = True
        mock_begin_prescan.return_value = True
        self.assertTrue(submit_artifacts.submit_artifacts(upload_api=upload_api))

        # Return False if setup_scan_prereqs returns False
        mock_get_sandbox_id.return_value = None  # Unused
        mock_create_sandbox.return_value = None  # Unused
        mock_setup_scan_prereqs.return_value = False
        mock_iterdir.return_value = iterdir_generator_valid()
        mock_filter_file.return_value = True
        mock_upload_large_file.return_value = True
        mock_begin_prescan.return_value = True
        self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))

        # Return False if filter_file always returns False, meaning artifacts
        # is empty
        mock_get_sandbox_id.return_value = None  # Unused
        mock_create_sandbox.return_value = None  # Unused
        mock_setup_scan_prereqs.return_value = True
        mock_iterdir.return_value = iterdir_generator_invalid()
        mock_filter_file.return_value = False
        mock_upload_large_file.return_value = True
        mock_begin_prescan.return_value = True
        self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))

        # Return False if upload_large_file always returns False, meaning
        # something is wrong with the file upload
        mock_get_sandbox_id.return_value = None  # Unused
        mock_create_sandbox.return_value = None  # Unused
        mock_setup_scan_prereqs.return_value = True
        mock_iterdir.return_value = iterdir_generator_valid()
        mock_filter_file.return_value = True
        mock_upload_large_file.return_value = False
        mock_begin_prescan.return_value = True
        self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))

        # Return False if begin_prescan returns False, meaning the prescan was
        # unable to be started
        mock_get_sandbox_id.return_value = None  # Unused
        mock_create_sandbox.return_value = None  # Unused
        mock_setup_scan_prereqs.return_value = True
        mock_iterdir.return_value = iterdir_generator_valid()
        mock_filter_file.return_value = True
        mock_upload_large_file.return_value = True
        mock_begin_prescan.return_value = False
        self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))
