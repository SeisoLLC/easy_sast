#!/usr/bin/env python3
"""
Unit tests for config.py
"""

# built-ins
import copy
import logging
import sys
from unittest import TestCase
from unittest.mock import patch, mock_open
from pathlib import Path
from argparse import ArgumentParser, Namespace

# custom
from tests import constants as test_constants
from veracode import config
from veracode.__init__ import __version__ as veracode_version
from veracode.api import ResultsAPI, UploadAPI, SandboxAPI

# Setup a logger
logging.getLogger()
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=FORMAT)
logging.raiseExceptions = True
LOG = logging.getLogger(__name__)


def return_unmodified_config(*, config: dict):  # pylint: disable=redefined-outer-name
    """
    A helper test function to help when mocking functions such as filter_config

    Returns the provided config dict
    """
    return config


def return_config_without_apis(*, config: dict):  # pylint: disable=redefined-outer-name
    """
    A helper test function to help when mocking functions such as filter_config

    Returns the provided config dict after removing the "apis" keys
    """
    del config["apis"]
    return config


class CLITestCase(TestCase):
    """
    Create a class method for the argparse testing of config.py
    """

    @classmethod
    def setUpClass(cls):
        parser = config.create_arg_parser()
        cls.parser = parser


class TestVeracodeConfig(CLITestCase):
    """
    Test config.py
    """

    ## remove_nones tests
    def test_remove_nones(self):
        """
        Test the remove_nones function
        """
        before = test_constants.INVALID_CONFIG_DIRTY
        after = test_constants.INVALID_CONFIG_NO_NONE

        # Succeed when calling the remove_nones function with a config dict and
        # return a dict that contains no Nones
        self.assertEqual(config.remove_nones(obj=before), after)

    ## remove_empty_dicts tests
    def test_remove_empty_dicts(self):
        """
        Test the remove_empty_dicts function
        """
        before = test_constants.INVALID_CONFIG_DIRTY
        after = test_constants.INVALID_CONFIG_NO_EMPTY_DICT

        # Succeed when calling the remove_empty_dicts function with a config
        # dict and return a dict that contains no empty dicts
        self.assertEqual(config.remove_empty_dicts(obj=before), after)

    ## filter_config tests
    @patch("veracode.config.remove_nones")
    @patch("veracode.config.remove_empty_dicts")
    def test_filter_config_no_iteration(
        self, mock_remove_empty_dicts, mock_remove_nones
    ):
        """
        Test the filter_config function when no iteration is necessary
        """
        # Succeed when calling the filter_config function with a config dict
        # and return a dict that contains no Nones or empty dicts
        mock_remove_nones.return_value = test_constants.INVALID_CONFIG_NO_NONE
        mock_remove_empty_dicts.return_value = test_constants.INVALID_CONFIG_CLEAN
        before = test_constants.INVALID_CONFIG_DIRTY
        after = test_constants.INVALID_CONFIG_CLEAN
        self.assertEqual(config.filter_config(config=before), after)

        # Succeed when calling the filter_config function with a config dict
        # that was already filtered
        mock_remove_nones.return_value = test_constants.INVALID_CONFIG_CLEAN
        mock_remove_empty_dicts.return_value = test_constants.INVALID_CONFIG_CLEAN
        before = test_constants.INVALID_CONFIG_CLEAN
        after = test_constants.INVALID_CONFIG_CLEAN
        self.assertEqual(config.filter_config(config=before), after)

    def test_filter_config_w_iteration(self):
        """
        Test the filter_config function when iteration is necessary

        Note that this test does not mock the calls to the remove_nones and
        remove_empty_dicts functions in veracode/config.py
        """
        # Succeed when calling the filter_config function with a config dict
        # that contains variety of empty dicts and Nones, removing them
        # recursively in the returned dict
        before = {
            "a": {},
            None: "b",
            "thing": {"c": {}, "d": {"e": None}},
            "f": {"g": {"h": {1.2: {3: {}}}}},
        }
        output = config.filter_config(config=before)
        after = {}
        self.assertEqual(output, after)

        # Succeed when calling the normalize_config function with a variety of
        # empty dicts, Nones, and a single list, ensuring filtered_config was
        # called the expected number of times
        before = {
            "a": {"b": {}, "c": {"d": [None, {}, None]}},
            "a1": {"b1": {"c1": {9.8: {7: {}}}}},
        }
        output = config.filter_config(config=before)
        after = {"a": {"c": {"d": []}}}
        self.assertEqual(output, after)

    ## get_default_config tests
    def test_get_default_config(self):
        """
        Test the get_default_config function
        """
        # Succeed in returning the default configuration dict
        self.assertIsInstance(config.get_default_config(), dict)

    ## get_file_config tests
    @patch("veracode.config.parse_file_config")
    @patch("veracode.config.normalize_config")
    def test_get_file_config(self, mock_normalize_config, mock_parse_file_config):
        """
        Test the get_file_config function
        """
        # Succeed when calling the get_file_config function with a valid
        # config_file argument
        mock_normalize_config.return_value = test_constants.VALID_CLEAN_FILE_CONFIG_NORMALIZED[
            "dict"
        ]
        mock_parse_file_config.return_value = test_constants.VALID_CLEAN_FILE_CONFIG[
            "dict"
        ]

        self.assertEqual(
            test_constants.VALID_CLEAN_FILE_CONFIG_NORMALIZED["dict"],
            config.get_file_config(
                config_file=test_constants.SIMPLE_CONFIG_FILE["Path"]
            ),
        )

        # Succeed when calling the get_file_config function with a valid
        # config_file argument, and parse_file_config returns an empty dict
        mock_normalize_config.return_value = {"loglevel": "WARNING"}
        mock_parse_file_config.return_value = {"loglevel": "WARNING"}

        self.assertEqual(
            {"loglevel": "WARNING"},
            config.get_file_config(
                config_file=test_constants.SIMPLE_CONFIG_FILE["Path"]
            ),
        )

        # Fail when calling the get_file_config function with an invalid
        # config_file argument
        self.assertRaises(ValueError, config.get_file_config, config_file=1)
        self.assertRaises(ValueError, config.get_file_config, config_file=1.2)
        self.assertRaises(
            ValueError, config.get_file_config, config_file="/path/easy_sast.yml"
        )
        self.assertRaises(ValueError, config.get_file_config, config_file=None)
        self.assertRaises(
            ValueError, config.get_file_config, config_file=["/path/", "easy_sast.yml"]
        )
        self.assertRaises(
            ValueError,
            config.get_file_config,
            config_file={"Path": "/path/easy_sast.yml"},
        )
        self.assertRaises(
            ValueError, config.get_file_config, config_file=set("easy_sast.yml")
        )

    ## parse_file_config tests
    def test_parse_file_config(self):
        """
        Test the parse_file_config function
        """
        # Succeed when calling the parse_file_config function with a valid
        # config_file argument
        with patch(
            "veracode.config.open",
            new=mock_open(read_data=test_constants.SIMPLE_CONFIG_FILE["bytes"]),
        ):
            self.assertEqual(
                {"loglevel": "WARNING"},
                config.parse_file_config(
                    config_file=test_constants.SIMPLE_CONFIG_FILE["Path"]
                ),
            )

        # Get an empty dict when calling the parse_file_config function with a
        # config_file that doesn't pass the suffix whitelist
        for invalid_config_file_name in test_constants.INVALID_CONFIG_FILES:
            self.assertEqual(
                {}, config.parse_file_config(config_file=invalid_config_file_name)
            )

        # Get an empty dict after calling the parse_file_config function with a
        # config_file argument that causes a FileNotFoundError on read
        with patch("veracode.config.open") as mock_file_open:
            mock_file_open.side_effect = FileNotFoundError
            self.assertEqual(
                {},
                config.parse_file_config(
                    config_file=test_constants.SIMPLE_CONFIG_FILE["Path"]
                ),
            )

        # Fail when attempting to call the parse_file_config function with a
        # config_file argument that causes a PermissionError on read
        with patch("veracode.config.open") as mock_file_open:
            mock_file_open.side_effect = PermissionError
            self.assertRaises(
                PermissionError,
                config.parse_file_config,
                config_file=test_constants.SIMPLE_CONFIG_FILE["Path"],
            )

        # Fail when attempting to call the parse_file_config function with a
        # config_file argument that causes a IsADirectoryError on read
        with patch("veracode.config.open") as mock_file_open:
            mock_file_open.side_effect = IsADirectoryError
            self.assertRaises(
                IsADirectoryError,
                config.parse_file_config,
                config_file=test_constants.SIMPLE_CONFIG_FILE["Path"],
            )

        # Fail when attempting to call the parse_file_config function with a
        # config_file argument that causes a OSError on read
        with patch("veracode.config.open") as mock_file_open:
            mock_file_open.side_effect = OSError
            self.assertRaises(
                OSError,
                config.parse_file_config,
                config_file=test_constants.SIMPLE_CONFIG_FILE["Path"],
            )

    ## get_env_config tests
    def test_get_env_config(self):
        """
        Test the get_env_config function
        """
        # Succeed when calling the get_env_config function no pre-existing
        # relevant environment variables
        values = {}
        expected = {"api_key_id": None, "api_key_secret": None}
        with patch.dict("os.environ", values=values, clear=True):
            self.assertEqual(expected, config.get_env_config())

        # Succeed when calling the get_env_config function a pre-existing
        # VERACODE_API_KEY_SECRET environment variable
        values = {
            "VERACODE_API_KEY_SECRET": test_constants.VALID_RESULTS_API[
                "api_key_secret"
            ]
        }
        with patch.dict("os.environ", values=values, clear=True):
            self.assertEqual(
                {
                    "api_key_id": None,
                    "api_key_secret": test_constants.VALID_RESULTS_API[
                        "api_key_secret"
                    ],
                },
                config.get_env_config(),
            )

        # Succeed when calling the get_env_config function a pre-existing
        # VERACODE_API_KEY_ID environment variable
        values = {"VERACODE_API_KEY_ID": test_constants.VALID_RESULTS_API["api_key_id"]}
        with patch.dict("os.environ", values=values, clear=True):
            self.assertEqual(
                {
                    "api_key_id": test_constants.VALID_RESULTS_API["api_key_id"],
                    "api_key_secret": None,
                },
                config.get_env_config(),
            )

        # Succeed when calling the get_env_config function pre-existing
        # VERACODE_API_KEY_ID and VERACODE_API_KEY_SECRET environment variables
        values = {
            "VERACODE_API_KEY_ID": test_constants.VALID_RESULTS_API["api_key_id"],
            "VERACODE_API_KEY_SECRET": test_constants.VALID_RESULTS_API[
                "api_key_secret"
            ],
        }
        with patch.dict("os.environ", values=values, clear=True):
            self.assertEqual(
                {
                    "api_key_id": test_constants.VALID_RESULTS_API["api_key_id"],
                    "api_key_secret": test_constants.VALID_RESULTS_API[
                        "api_key_secret"
                    ],
                },
                config.get_env_config(),
            )

    ## normalize_config tests
    @patch("veracode.config.is_valid_attribute")
    @patch("veracode.config.filter_config", side_effect=return_unmodified_config)
    def test_normalize_config(self, mock_filter_config, mock_is_valid_attribute):
        """
        Test the normalize_config function
        """
        # For linting.  See mock `side_effect` and the
        # `return_unmodified_config` function above
        mock_filter_config.return_value = None

        # Succeed when calling the normalize_config function with a
        # non-normalized config dict, a string loglevel, build_dir, and
        # sandbox_name, and return that dict properly normalized
        before = {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "app_id": "31337",
            "loglevel": "WARNING",
            "workflow": ["submit_artifacts", "check_compliance"],
            "apis": {
                "upload": {"build_dir": "/build/"},
                "sandbox": {"sandbox_name": "easy_sast/fb/jonzeolla/testing"},
            },
        }
        after = {
            "loglevel": "WARNING",
            "workflow": ["submit_artifacts", "check_compliance"],
            "apis": {
                "sandbox": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                    "sandbox_name": "easy_sast/fb/jonzeolla/testing",
                },
                "results": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                },
                "upload": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                    "build_dir": Path("/build/"),
                },
            },
        }
        mock_is_valid_attribute.return_value = True
        before_normalized = config.normalize_config(config=before)
        self.assertEqual(before_normalized, after)

        # Succeed when calling the normalize_config function with a
        # non-normalized config dict, a lowercase loglevel, and a Path
        # build_dir, and return that dict properly normalized
        before = {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "app_id": "31337",
            "loglevel": "info",
            "workflow": ["submit_artifacts", "check_compliance"],
            "apis": {
                "upload": {"build_dir": Path("/build/")},
                "results": {"ignore_compliance_status": False},
            },
        }
        after = {
            "loglevel": "INFO",
            "workflow": ["submit_artifacts", "check_compliance"],
            "apis": {
                "sandbox": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                },
                "results": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                    "ignore_compliance_status": False,
                },
                "upload": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                    "build_dir": Path("/build/"),
                },
            },
        }
        mock_is_valid_attribute.return_value = True
        before_normalized = config.normalize_config(config=before)
        self.assertEqual(before_normalized, after)

        # Succeed when calling the normalize_config function with a
        # non-normalized config dict, a missing loglevel, and a Path build_dir,
        # and return that dict properly normalized
        before = {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "app_id": "31337",
            "workflow": ["submit_artifacts", "check_compliance"],
            "apis": {
                "upload": {"build_dir": Path("/build/")},
                "results": {"ignore_compliance_status": False},
            },
        }
        after = {
            "workflow": ["submit_artifacts", "check_compliance"],
            "apis": {
                "sandbox": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                },
                "results": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                    "ignore_compliance_status": False,
                },
                "upload": {
                    "app_id": "31337",
                    "base_url": "https://analysiscenter.veracode.com/api/",
                    "build_dir": Path("/build/"),
                },
            },
        }
        mock_is_valid_attribute.return_value = True
        before_normalized = config.normalize_config(config=before)
        self.assertEqual(before_normalized, after)

        # Fail when attempting to call the normalize_config function with a
        # config that contains an invalid loglevel
        before = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        before["loglevel"] = "unknown_loglevel"
        mock_is_valid_attribute.return_value = True
        self.assertRaises(AttributeError, config.normalize_config, config=before)

        # Raise a ValueError when calling the normalize_config function with a
        # dict containing an invalid config and after receiving a mocked
        # response that it is invalid
        before = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        before["apis"]["upload"]["app_id"] = "abcdef"
        mock_is_valid_attribute.return_value = False
        self.assertRaises(ValueError, config.normalize_config, config=before)

    # test normalize_config with different patching
    @patch("veracode.config.filter_config", side_effect=return_config_without_apis)
    def test_normalize_config_redux(self, mock_filter_config):
        """
        Test the normalize_config function with different patching
        """
        # For linting.  See `side_effect` and `return_unmodified_config` above
        mock_filter_config.return_value = None

        # Succeed when calling the normalize_config function with a clean
        # config dict, but whose "apis" key is removed prior to the api config
        # values validation
        before = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        after = before  # No change
        before_normalized = config.normalize_config(config=before)
        self.assertEqual(before_normalized, after)

    ## get_args_config tests
    @patch("veracode.config.create_arg_parser")
    @patch("veracode.config.normalize_config")
    def test_get_args_config(self, mock_normalize_config, mock_create_arg_parser):
        """
        Test the get_args_config function
        """
        # Succeed when calling the get_args_config function with a valid
        # ArgumentParser mocked from the create_arg_parser function
        mock_create_arg_parser.return_value = ArgumentParser()
        parsed = {
            "api_key_id": test_constants.VALID_UPLOAD_API["api_key_id"],
            "api_key_secret": test_constants.VALID_UPLOAD_API["api_key_secret"],
            "loglevel": 30,
            "apis": {
                "results": {"app_id": "1337", "ignore_compliance_status": True},
                "upload": {
                    "app_id": "1337",
                    "build_id": "v1.2.3",
                    "scan_all_nonfatal_top_level_modules": True,
                    "auto_scan": True,
                    "build_dir": Path("/usr/local/bin/"),
                },
                "sandbox": {"sandbox_name": "easy_sast/fb/jonzeolla/testing"},
            },
        }
        mock_normalize_config.return_value = parsed
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
                sandbox_name=test_constants.VALID_SANDBOX_API["sandbox_name"],
                loglevel=logging.WARNING,
                ignore_compliance_status=True,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            self.assertEqual(config.get_args_config(), parsed)

        # Succeed when calling the get_args_config function with a valid
        # ArgumentParser mocked from the create_arg_parser function, without
        # any of the disable_keys provided
        mock_create_arg_parser.return_value = ArgumentParser()
        parsed = {
            "api_key_id": test_constants.VALID_UPLOAD_API["api_key_id"],
            "api_key_secret": test_constants.VALID_UPLOAD_API["api_key_secret"],
            "loglevel": 30,
            "apis": {
                "upload": {
                    "app_id": "1337",
                    "build_id": "v1.2.3",
                    "build_dir": Path("/usr/local/bin/"),
                },
            },
        }
        mock_normalize_config.return_value = parsed
        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=Namespace(
                app_id=test_constants.VALID_UPLOAD_API["app_id"],
                build_dir=test_constants.VALID_UPLOAD_API["build_dir"],
                build_id=test_constants.VALID_UPLOAD_API["build_id"],
                loglevel=logging.WARNING,
                api_key_id=test_constants.VALID_UPLOAD_API["api_key_id"],
                api_key_secret=test_constants.VALID_UPLOAD_API["api_key_secret"],
            ),
        ):
            self.assertEqual(config.get_args_config(), parsed)

    ## create_arg_parser tests
    # pylint: disable=too-many-statements
    @patch("argparse.ArgumentParser._print_message")
    def test_create_arg_parser(self, mock__print_message):
        """
        Test the create_arg_parser function
        """
        # Succeed when calling the create_arg_parser function and pass only
        # --api-key-id as an argument
        output = self.parser.parse_args(
            ["--api-key-id=" + test_constants.VALID_UPLOAD_API["api_key_id"]]
        )
        self.assertEqual(
            output.api_key_id, test_constants.VALID_UPLOAD_API["api_key_id"]
        )

        # Succeed when calling the create_arg_parser function and do not pass
        # --api-key-id as an argument
        output = self.parser.parse_args(["--verbose"])
        self.assertIsNone(output.api_key_id)

        # Succeed when calling the create_arg_parser function and pass only
        # --api-key-secret as an argument
        output = self.parser.parse_args(
            ["--api-key-secret=" + test_constants.VALID_UPLOAD_API["api_key_secret"]]
        )
        self.assertEqual(
            output.api_key_secret, test_constants.VALID_UPLOAD_API["api_key_secret"]
        )

        # Succeed when calling the create_arg_parser function and do not pass
        # --api-key-secret as an argument
        output = self.parser.parse_args(["--verbose"])
        self.assertIsNone(output.api_key_secret)

        # Succeed when calling the create_arg_parser function wnd pass only
        # --app-id as an argument
        output = self.parser.parse_args(["--app-id=31337"])
        self.assertEqual(output.app_id, "31337")

        # Succeed when calling the create_arg_parser function and do not pass
        # --app-id as an argument
        output = self.parser.parse_args(["--verbose"])
        self.assertIsNone(output.app_id)

        # Succeed when calling the create_arg_parser function and pass only
        # --build-dir as an argument
        output = self.parser.parse_args(["--build-dir=./"])
        self.assertEqual(output.build_dir, Path("./").absolute())

        # Succeed when calling the create_arg_parser function and pass only
        # --build-id as an argument
        output = self.parser.parse_args(
            ["--build-id=" + test_constants.VALID_UPLOAD_API["build_id"]]
        )
        self.assertEqual(output.build_id, test_constants.VALID_UPLOAD_API["build_id"])

        # Succeed when calling the create_arg_parser function and pass only
        # --sandbox-name as an argument
        output = self.parser.parse_args(
            ["--sandbox-name=" + test_constants.VALID_SANDBOX_API["sandbox_name"]]
        )
        self.assertEqual(
            output.sandbox_name, test_constants.VALID_SANDBOX_API["sandbox_name"]
        )

        # Succeed when calling the create_arg_parser function and do not pass
        # --build-id as an argument
        output = self.parser.parse_args(["--verbose"])
        self.assertIsNone(output.build_id)

        # Succeed when calling the create_arg_parser function and pass only
        # --config-file as an argument
        output = self.parser.parse_args(
            ["--config-file=" + str(Path("./easy_sast.yml").absolute())]
        )
        self.assertEqual(output.config_file, Path("./easy_sast.yml").absolute())

        # Succeed and return the default config file when calling the
        # create_arg_parser function without passing --config-file as an
        # argument
        output = self.parser.parse_args(["--verbose"])
        self.assertEqual(output.config_file, Path("./easy_sast.yml").absolute())

        # Succeed when calling the create_arg_parser function and pass only
        # --disable-auto-scan as an argument
        output = self.parser.parse_args(["--disable-auto-scan"])
        self.assertEqual(output.disable_auto_scan, True)

        # Succeed and return the default value for disable-auto-scan when
        # calling the create_arg_parser function without passing
        # --disable-auto-scan as an argument
        output = self.parser.parse_args(
            ["--build-id=" + test_constants.VALID_UPLOAD_API["build_id"]]
        )
        self.assertEqual(output.disable_auto_scan, False)

        # Succeed when calling the create_arg_parser function and pass only
        # --disable-scan-nonfatal-modules as an argument
        output = self.parser.parse_args(["--disable-scan-nonfatal-modules"])
        self.assertEqual(output.disable_scan_nonfatal_modules, True)

        # Succeed and return the default value for
        # disable-scan-nonfatal-modules when calling the create_arg_parser
        # function without passing --disable-scan-nonfatal-modules as an
        # argument
        output = self.parser.parse_args(["--disable-auto-scan"])
        self.assertEqual(output.disable_scan_nonfatal_modules, False)

        # Succeed when calling the create_arg_parser function and pass only
        # --ignore-compliance-status as an argument
        output = self.parser.parse_args(["--ignore-compliance-status"])
        self.assertEqual(output.ignore_compliance_status, True)

        # Succeed when calling the create_arg_parser function and pass only
        # --ignore-compliance-status as an argument
        output = self.parser.parse_args(["--disable-auto-scan"])
        self.assertEqual(output.ignore_compliance_status, False)

        # Succeed when calling the create_arg_parser function and pass only
        # --version as an argument
        with self.assertRaises(SystemExit) as contextmanager:
            output = self.parser.parse_args(["--version"])
        self.assertEqual(contextmanager.exception.code, 0)
        # Using sys instead of _sys because it is the same thing per
        # https://github.com/python/cpython/blob/6a263cf1adfc18cdba65c788dd76d35997a89acf/Lib/argparse.py#L90
        mock__print_message.assert_called_once_with(veracode_version + "\n", sys.stdout)

        # Succeed when calling the create_arg_parser function and do not pass
        # --version as an argument
        output = self.parser.parse_args(["--disable-auto-scan"])
        with self.assertRaises(SystemExit) as contextmanager:
            output = self.parser.parse_args(["--version"])
        self.assertEqual(contextmanager.exception.code, 0)

        # Succeed when calling the create_arg_parser function and pass only
        # --workflow as an argument
        output = self.parser.parse_args(["--workflow", "submit_artifacts"])
        self.assertEqual(output.workflow, ["submit_artifacts"])
        output = self.parser.parse_args(["--workflow", "check_compliance"])
        self.assertEqual(output.workflow, ["check_compliance"])
        output = self.parser.parse_args(["--workflow", "literally any string"])
        self.assertEqual(output.workflow, ["literally any string"])

        # Succeed when calling the create_arg_parser function and do not pass
        # --workflow as an argument
        output = self.parser.parse_args(["--verbose"])
        self.assertIsNone(output.workflow)

        # Succeed when calling the create_arg_parser function and pass only
        # --verbose as an argument
        output = self.parser.parse_args(["--verbose"])
        self.assertEqual(output.loglevel, "INFO")

        # Succeed when calling the create_arg_parser function and do not pass
        # --verbose or --debug as arguments
        output = self.parser.parse_args(["--disable-auto-scan"])
        self.assertIsNone(output.loglevel)

        # Succeed when calling the create_arg_parser function and pass only
        # --debug as an argument
        output = self.parser.parse_args(["--debug"])
        self.assertEqual(output.loglevel, "DEBUG")

        # Fail when calling the create_arg_parser function and pass both
        # --debug and --verbose as an argument, as they are mutually exclusive
        with self.assertRaises(SystemExit) as contextmanager:
            output = self.parser.parse_args(["--debug", "--verbose"])
        self.assertEqual(contextmanager.exception.code, 2)

    ## is_valid_non_api_config tests
    @patch("veracode.config.is_valid_attribute")
    def test_is_valid_non_api_config(self, mock_is_valid_attribute):
        """
        Test the is_valid_non_api_config function
        """
        # Succeed when calling the is_valid_non_api_config function with a
        # valid config
        mock_is_valid_attribute.return_value = True
        configuration = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        configuration["config_file"] = Path("./easy_sast.yml").absolute()
        self.assertTrue(config.is_valid_non_api_config(config=configuration))

        # Return False after calling the is_valid_api_config function with a
        # config that doesn't contain a required config attribute
        mock_is_valid_attribute.return_value = True
        configuration = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        del configuration["loglevel"]
        self.assertFalse(config.is_valid_non_api_config(config=configuration))

        # Return False after calling the is_valid_api_config function with a
        # config that contains an invalid config attribute
        mock_is_valid_attribute.return_value = False
        configuration = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        configuration["config_file"] = Path("./easy_sast.yml").absolute()
        self.assertFalse(config.is_valid_non_api_config(config=configuration))

    ## is_valid_api_config tests
    @patch("veracode.config.is_valid_attribute")
    def test_is_valid_api_config(self, mock_is_valid_attribute):
        """
        Test the is_valid_api_config function
        """
        # Succeed when calling the is_valid_api_config function with a valid
        # config
        mock_is_valid_attribute.return_value = True
        configuration = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        # This step would normally would be handled via normalize_config
        configuration["apis"]["upload"]["build_dir"] = Path(
            configuration["apis"]["upload"]["build_dir"]
        )
        self.assertTrue(config.is_valid_api_config(config=configuration))

        # Return False after calling the is_valid_api_config function with a
        # config that doesn't contain a required config attribute
        mock_is_valid_attribute.return_value = True
        configuration = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        del configuration["apis"]["upload"]["app_id"]
        self.assertFalse(config.is_valid_api_config(config=configuration))

        # Return False after calling the is_valid_api_config function with a
        # config that contains an invalid config attribute
        mock_is_valid_attribute.return_value = False
        configuration = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        self.assertFalse(config.is_valid_api_config(config=configuration))

    ## get_config tests
    @patch("veracode.config.get_default_config")
    @patch("veracode.config.get_args_config")
    @patch("veracode.config.get_file_config")
    @patch("veracode.config.get_env_config")
    @patch("veracode.config.is_valid_non_api_config")
    @patch("veracode.config.is_valid_api_config")
    def test_get_config(  # pylint: disable=too-many-arguments
        self,
        mock_is_valid_api_config,
        mock_is_valid_non_api_config,
        mock_get_env_config,
        mock_get_file_config,
        mock_get_args_config,
        mock_get_default_config,
    ):
        """
        Test the get_config function
        """
        # Succeed when calling the get_config function with all conditionals
        # returning True
        mock_is_valid_non_api_config.return_value = True
        mock_is_valid_api_config.return_value = True
        mock_get_env_config.return_value = test_constants.CLEAN_ENV_CONFIG
        mock_get_file_config.return_value = test_constants.CLEAN_FILE_CONFIG
        mock_get_args_config.return_value = test_constants.CLEAN_ARGS_CONFIG
        mock_get_default_config.return_value = test_constants.CLEAN_DEFAULT_CONFIG
        self.assertEqual(test_constants.CLEAN_EFFECTIVE_CONFIG, config.get_config())

        # Return not None when calling the get_config function with all
        # conditionals returning True, but the file and args do not have an
        # "apis" top level key
        mock_is_valid_non_api_config.return_value = True
        mock_is_valid_api_config.return_value = True
        mock_get_env_config.return_value = test_constants.CLEAN_ENV_CONFIG
        file_config = copy.deepcopy(test_constants.VALID_CLEAN_FILE_CONFIG["dict"])
        del file_config["apis"]
        mock_get_file_config.return_value = file_config
        args_config = copy.deepcopy(test_constants.CLEAN_ARGS_CONFIG)
        del args_config["apis"]
        mock_get_args_config.return_value = args_config
        mock_get_default_config.return_value = test_constants.CLEAN_DEFAULT_CONFIG
        expected = {
            "workflow": ["submit_artifacts", "check_compliance"],
            "loglevel": "warning",
            "apis": {"upload": {}, "results": {}, "sandbox": {}},
            "api_key_id": "95e637f1a25d453cdfdc30a338287ba8",
            "api_key_secret": "f7bb8c01bce05290ac8939f1d27d90ab84d2e05bb4671ca2f88d609d07afa723265348d708bdd0a1707a499528f6aa5c83133f4c5aca06a528d30b61fd4b6b28",
            "config_file": Path("/easy_sast/easy_sast.yml"),
        }
        self.assertEqual(config.get_config(), expected)

        # Raise a ValueError when calling the get_config function with all
        # conditionals returning True except for is_valid_non_api_config
        mock_is_valid_non_api_config.return_value = False
        mock_is_valid_api_config.return_value = True
        mock_get_env_config.return_value = test_constants.CLEAN_ENV_CONFIG
        mock_get_file_config.return_value = test_constants.VALID_CLEAN_FILE_CONFIG[
            "dict"
        ]
        mock_get_args_config.return_value = test_constants.CLEAN_ARGS_CONFIG
        mock_get_default_config.return_value = test_constants.CLEAN_DEFAULT_CONFIG
        self.assertRaises(ValueError, config.get_config)

        # Raise a ValueError when calling the get_config function with all
        # conditionals returning True except for is_valid_api_config
        mock_is_valid_non_api_config.return_value = True
        mock_is_valid_api_config.return_value = False
        mock_get_env_config.return_value = test_constants.CLEAN_ENV_CONFIG
        mock_get_file_config.return_value = test_constants.VALID_CLEAN_FILE_CONFIG[
            "dict"
        ]
        mock_get_args_config.return_value = test_constants.CLEAN_ARGS_CONFIG
        mock_get_default_config.return_value = test_constants.CLEAN_DEFAULT_CONFIG
        self.assertRaises(ValueError, config.get_config)

        # Raise a ValueError when calling the get_config function with all
        # conditionals returning True except for is_valid_api_config and
        # is_valid_non_api_config
        mock_is_valid_non_api_config.return_value = False
        mock_is_valid_api_config.return_value = False
        mock_get_env_config.return_value = test_constants.CLEAN_ENV_CONFIG
        mock_get_file_config.return_value = test_constants.VALID_CLEAN_FILE_CONFIG[
            "dict"
        ]
        mock_get_args_config.return_value = test_constants.CLEAN_ARGS_CONFIG
        mock_get_default_config.return_value = test_constants.CLEAN_DEFAULT_CONFIG
        self.assertRaises(ValueError, config.get_config)

    ## apply_config tests
    def test_apply_config(self):
        """
        Test the apply_config function
        """
        configuration = copy.deepcopy(test_constants.CLEAN_EFFECTIVE_CONFIG)

        # Succeed when calling the apply_config function with a valid
        # Upload API object and config
        upload_api = UploadAPI(app_id="31337")
        applied_upload_api = config.apply_config(api=upload_api, config=configuration)
        self.assertEqual(applied_upload_api, upload_api)

        # Succeed when calling the apply_config function with a valid
        # Results API object and config
        results_api = ResultsAPI(app_id="31337")
        applied_results_api = config.apply_config(api=results_api, config=configuration)
        self.assertEqual(applied_results_api, results_api)

        # Succeed when calling the apply_config function with a valid
        # Sandbox API object and config
        sandbox_api = SandboxAPI(
            app_id="31337", sandbox_name="easy_sast/fb/jonzeolla/testing"
        )
        applied_sandbox_api = config.apply_config(api=sandbox_api, config=configuration)
        self.assertEqual(applied_sandbox_api, sandbox_api)

        # Ensure calling the apply_config function with different `app_id`s
        # does not result in an object with the same version string (which is
        # unique per-API)
        upload_api = UploadAPI(app_id="31337")
        applied_upload_api = config.apply_config(api=upload_api, config=configuration)
        # Note: This must be different than the above app_id
        results_api = ResultsAPI(app_id="1337")
        applied_results_api = config.apply_config(api=results_api, config=configuration)
        self.assertNotEqual(applied_results_api.version, applied_upload_api.version)

        # Fail when calling the apply_config function with a string instead of
        # an API object
        astring = "wrong type"
        self.assertRaises(
            TypeError, config.apply_config, api=astring, config=configuration
        )

        # Succeed when calling the apply_config function with a valid
        # Results API object and config
        configuration["apis"]["unknown"] = {"a": "b"}
        results_api = ResultsAPI(app_id="31337")
        self.assertEqual(
            config.apply_config(api=results_api, config=configuration), results_api
        )
