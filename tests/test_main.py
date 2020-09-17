#!/usr/bin/env python3
# pylint: disable=too-many-public-methods
"""
Unit tests for main.py
"""

# built-ins
import copy
import logging
from argparse import Namespace
from unittest.mock import patch
from unittest import TestCase
from typing import Union

# custom
from tests import constants as test_constants
import main
from veracode.api import ResultsAPI, UploadAPI

# Setup a logger
logging.getLogger()
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=FORMAT)
logging.raiseExceptions = True
LOG = logging.getLogger(__name__)


def return_unmodified_api_object(
    *, api: Union[ResultsAPI, UploadAPI], config: dict
):  # pylint: disable=unused-argument
    """
    A helper test function to help when mocking functions such as apply_config

    Returns the provided api object
    """
    return api


class TestMain(TestCase):
    """
    Test main.py
    """

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_happy_path(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test the main happy path with defaults
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = True
        mock_submit_artifacts.return_value = True
        mock_get_config.return_value = test_constants.CLEAN_EFFECTIVE_CONFIG

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_name=test_constants.VALID_UPLOAD_API["app_name"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with patch("veracode.api.get_app_id", return_value="1337"):
                self.assertIsNone(main.main())

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_unknown_config_step(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test main with an unknown config step
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = True
        mock_submit_artifacts.return_value = True
        config = copy.deepcopy(test_constants.CLEAN_EFFECTIVE_CONFIG)
        config["workflow"] = ["unknown", "check_compliance", "unknown"]
        mock_get_config.return_value = config

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_name=test_constants.VALID_UPLOAD_API["app_name"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with patch("veracode.api.get_app_id", return_value="1337"):
                self.assertIsNone(main.main())

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_failed_submit_artifacts(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test main when submit_artifacts fails
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = True
        mock_submit_artifacts.return_value = False
        mock_get_config.return_value = test_constants.CLEAN_EFFECTIVE_CONFIG

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_name=test_constants.VALID_UPLOAD_API["app_name"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with self.assertRaises(SystemExit) as contextmanager:
                with patch("veracode.api.get_app_id", return_value="1337"):
                    main.main()
                self.assertEqual(contextmanager.exception.code, 1)

    # pylint: disable=too-many-arguments
    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    @patch("main.configure_environment")
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_failed_check_compliance(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_configure_environment,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test main when check_compliance fails
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = False
        mock_submit_artifacts.return_value = True
        mock_get_config.return_value = test_constants.CLEAN_EFFECTIVE_CONFIG
        mock_configure_environment.return_value = True

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_name=test_constants.VALID_UPLOAD_API["app_name"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with self.assertRaises(SystemExit) as contextmanager:
                with patch("veracode.api.get_app_id", return_value="1337"):
                    main.main()
            self.assertEqual(contextmanager.exception.code, 1)

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_ignore_unknown_api(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test the main happy path with defaults
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = True
        mock_submit_artifacts.return_value = True
        config = copy.deepcopy(test_constants.CLEAN_EFFECTIVE_CONFIG)
        config["apis"].update({"unknown_api": {"something": "here"}})
        mock_get_config.return_value = config

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_name=test_constants.VALID_UPLOAD_API["app_name"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with patch("veracode.api.get_app_id", return_value="1337"):
                self.assertIsNone(main.main())

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    def test_veracode_main_get_config_value_error(
        self,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test main.py when get_config returns a ValueError
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_get_config.side_effect = ValueError

        with self.assertRaises(SystemExit) as contextmanager:
            with patch("veracode.api.get_app_id", return_value="1337"):
                main.main()
        self.assertEqual(contextmanager.exception.code, 1)

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=TypeError)
    @patch("main.configure_environment")
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_main_apply_config_type_error(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_configure_environment,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test main.py when apply_config returns a TypeError
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = True
        mock_submit_artifacts.return_value = True
        mock_get_config.return_value = test_constants.CLEAN_EFFECTIVE_CONFIG
        mock_configure_environment.return_value = True

        with self.assertRaises(SystemExit) as contextmanager:
            with patch("veracode.api.get_app_id", return_value="1337"):
                main.main()
        self.assertEqual(contextmanager.exception.code, 1)

    @patch("main.get_config")
    @patch("main.apply_config", side_effect=return_unmodified_api_object)
    @patch("main.submit_artifacts")
    @patch("main.check_compliance")
    def test_veracode_main_no_sandbox_name(
        self,
        mock_check_compliance,
        mock_submit_artifacts,
        mock_apply_config,
        mock_get_config,
    ):
        """
        Test main with an effective config lacking a sandbox_name
        """
        # For the linter, this is unused
        mock_apply_config.return_value = None

        # Actual test
        mock_check_compliance.return_value = True
        mock_submit_artifacts.return_value = True
        config = copy.deepcopy(test_constants.CLEAN_EFFECTIVE_CONFIG)
        del config["apis"]["sandbox"]["sandbox_name"]
        mock_get_config.return_value = config

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_name=test_constants.VALID_UPLOAD_API["app_name"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with patch("veracode.api.get_app_id", return_value="1337"):
                self.assertIsNone(main.main())

        # Test for UnboundLocalError
        mock_apply_config.side_effect = UnboundLocalError

        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_id=test_constants.VALID_UPLOAD_API["app_id"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                disable_auto_scan=not test_constants.VALID_UPLOAD_API["auto_scan"],
                disable_scan_nonfatal_modules=not test_constants.VALID_UPLOAD_API[
                    "scan_all_nonfatal_top_level_modules"
                ],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            with patch("veracode.api.get_app_id", return_value="1337"):
                with self.assertRaises(SystemExit) as contextmanager:
                    main.main()
                self.assertEqual(contextmanager.exception.code, 1)
