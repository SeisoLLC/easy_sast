#!/usr/bin/env python3
"""
Constants for easy_sast
"""
# Supported Sets
SUPPORTED_APIS = {"results", "upload", "sandbox"}
SUPPORTED_API_CLASSES = {"ResultsAPI", "UploadAPI", "SandboxAPI"}
SUPPORTED_WORKFLOWS = {"submit_artifacts", "check_compliance"}
SUPPORTED_VERBS = {"get", "post"}

## API Attributes
API_ATTRIBUTES = {
    "upload": {
        "base_url",
        "version",
        "app_id",
        "build_dir",
        "build_id",
        "sandbox_id",
        "scan_all_nonfatal_top_level_modules",
        "auto_scan",
    },
    "results": {
        "base_url",
        "version",
        "app_id",
        "ignore_compliance_status",
        "ignore_compliance_status",
    },
    "sandbox": {
        "base_url",
        "version",
        "app_id",
        "build_id",
        "sandbox_id",
        "sandbox_name",
    },
}
COMMON_API_ATTRIBUTES = API_ATTRIBUTES["upload"].intersection(
    API_ATTRIBUTES["results"], API_ATTRIBUTES["sandbox"]
)
ONLY_UPLOAD_ATTRIBUTES = API_ATTRIBUTES["upload"].difference(
    API_ATTRIBUTES["results"], API_ATTRIBUTES["sandbox"]
)
ONLY_RESULTS_ATTRIBUTES = API_ATTRIBUTES["results"].difference(
    API_ATTRIBUTES["upload"], API_ATTRIBUTES["sandbox"]
)
ONLY_SANDBOX_ATTRIBUTES = API_ATTRIBUTES["sandbox"].difference(
    API_ATTRIBUTES["results"], API_ATTRIBUTES["upload"]
)

## Config Options
REQUIRED_CONFIG_ATTRIBUTES_API = {"app_id"}
REQUIRED_CONFIG_ATTRIBUTES_TOP = {"loglevel", "workflow", "config_file"}
# Explicitly does not have api_key_id and api_key_secret to deter storing
# secrets in config files
LIMITED_OPTIONS_SET = {"loglevel", "workflow", "config_file"}
ALL_OPTIONS_SET = LIMITED_OPTIONS_SET | {"api_key_id", "api_key_secret"}
# https://docs.python.org/3/library/logging.html#logging-levels
ALLOWED_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

# Workflow Items
DEFAULT_WORKFLOW = ["submit_artifacts", "check_compliance"]
WORKFLOW_TO_API_MAP = {
    "submit_artifacts": {"upload", "sandbox"},
    "check_compliance": {"results"},
}

# submit_artifacts
WHITELIST_FILE_SUFFIX_SET = {
    ".exe",
    ".pdb",
    ".dll",
    ".jar",
    ".zip",
    ".tar",
    ".tgz",
    ".war",
    ".ear",
    ".jar",
    ".apk",
    ".ipa",
}
WHITELIST_FILE_SUFFIXES_LIST = [".tar", ".gz"]
