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
from veracode.api import UploadAPI

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

    @patch("requests.post")
    def test_create_build_successful(self, mock_post):
        """Test the create_build function with a successful response"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()

        self.assertTrue(submit_artifacts.create_build(upload_api=upload_api))

    @patch("requests.post")
    def test_create_build_failure(self, mock_post):
        """Test the create_build function with an error response"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VERACODE_ERROR_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()

        self.assertFalse(submit_artifacts.create_build(upload_api=upload_api))

    @patch("requests.post")
    def test_begin_prescan_success(self, mock_post):
        """Test the begin_prescan function with a successful response"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        self.assertTrue(submit_artifacts.begin_prescan(upload_api=upload_api))

    @patch("requests.post")
    def test_begin_prescan_failure(self, mock_post):
        """Test the begin_prescan function with a 403 response"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.status_code = 403
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        self.assertRaises(
            HTTPError, submit_artifacts.begin_prescan, upload_api=upload_api,
        )

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

    @patch("requests.post")
    def test_upload_large_file_happy_path(self, mock_post):
        """Test the upload_large_file function happy path"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        valid_artifact = test_constants.VALID_FILE["Path"]
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()

        with patch(
            "veracode.submit_artifacts.open",
            new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
        ):
            self.assertTrue(
                submit_artifacts.upload_large_file(
                    upload_api=upload_api, artifact=valid_artifact
                )
            )

    @patch("requests.post")
    def test_upload_large_file_unhappy_path(self, mock_post):
        """Test the upload_large_file function unhappy path"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        valid_artifact = test_constants.VALID_FILE["Path"]
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 403
        mock_post.return_value.raise_for_status.side_effect = HTTPError()

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

    @patch("pathlib.Path.iterdir")
    @patch("requests.post")
    def test_submit_artifacts_happy_path(self, mock_post, mock_iterdir):
        """Test the submit_artifacts function happy path"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()

        def iterdir_generator():
            f = test_constants.VALID_FILE["Path"]
            yield f

        mock_iterdir.return_value = iterdir_generator()

        with patch(
            "veracode.submit_artifacts.open",
            new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
        ):
            self.assertTrue(submit_artifacts.submit_artifacts(upload_api=upload_api))

    @patch("veracode.submit_artifacts.create_build")
    def test_submit_artifacts_fail_at_create_build(self, mock_create_build):
        """Test the submit_artifacts function when create_build returns False"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_create_build.return_value = False

        self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))

    @patch("pathlib.Path.iterdir")
    @patch("requests.post")
    def test_submit_artifacts_no_files_to_upload(self, mock_post, mock_iterdir):
        """
        Test the submit_artifacts function when filter_file returns False for
        all artifacts
        """
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()

        def iterdir_generator():
            f = test_constants.INVALID_FILE["Path"]
            yield f

        mock_iterdir.return_value = iterdir_generator()

        with patch(
            "veracode.submit_artifacts.open",
            new=mock_open(read_data=test_constants.INVALID_FILE["bytes"]),
        ):
            self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))

    @patch("veracode.submit_artifacts.upload_large_file")
    @patch("pathlib.Path.iterdir")
    @patch("requests.post")
    def test_submit_artifacts_fail_at_upload_large_file(
        self, mock_post, mock_iterdir, mock_upload_large_file
    ):
        """Test the submit_artifacts function when upload_large_file returns False"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        mock_upload_large_file.return_value = False

        def iterdir_generator():
            f = test_constants.VALID_FILE["Path"]
            yield f

        mock_iterdir.return_value = iterdir_generator()

        with patch(
            "veracode.submit_artifacts.open",
            new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
        ):
            self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))

    @patch("veracode.submit_artifacts.begin_prescan")
    @patch("pathlib.Path.iterdir")
    @patch("requests.post")
    def test_submit_artifacts_fail_at_begin_prescan(
        self, mock_post, mock_iterdir, mock_begin_prescan
    ):
        """Test the submit_artifacts function when begin_prescan returns False"""
        upload_api = UploadAPI(app_id=test_constants.VALID_UPLOAD_API["app_id"])
        mock_post.return_value.content = test_constants.VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
            "bytes"
        ]
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        mock_begin_prescan.return_value = False

        def iterdir_generator():
            f = test_constants.VALID_FILE["Path"]
            yield f

        mock_iterdir.return_value = iterdir_generator()

        with patch(
            "veracode.submit_artifacts.open",
            new=mock_open(read_data=test_constants.VALID_FILE["bytes"]),
        ):
            self.assertFalse(submit_artifacts.submit_artifacts(upload_api=upload_api))
