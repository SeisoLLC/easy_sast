#!/usr/bin/env python3
"""
Constants for easy_sast
"""
# Supported Sets
SUPPORTED_APIS = {"results", "upload", "sandbox"}
SUPPORTED_API_CLASSES = {"ResultsAPI", "UploadAPI", "SandboxAPI"}
SUPPORTED_WORKFLOWS = {"submit_artifacts", "check_compliance"}
SUPPORTED_VERBS = {"get", "post"}

API_BASE_URL = "https://analysiscenter.veracode.com/api/"

## API Attributes
API_ATTRIBUTES = {
    "upload": {
        "base_url",
        "version",
        "app_name",
        "build_dir",
        "build_id",
        "sandbox_id",
        "scan_all_nonfatal_top_level_modules",
        "auto_scan",
    },
    "results": {
        "base_url",
        "version",
        "app_name",
        "ignore_compliance_status",
        "ignore_compliance_status",
    },
    "sandbox": {
        "base_url",
        "version",
        "app_name",
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

# Upload API
UPLOAD_API_VERSIONS = {
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

# Results API
RESULTS_API_VERSIONS = {
    "detailedreport.do": "5.0",
    "detailedreportpdf.do": "4.0",
    "getaccountcustomfieldlist.do": "5.0",
    "getappbuilds.do": "4.0",
    "getcallstacks.do": "5.0",
    "summaryreport.do": "4.0",
    "summaryreportpdf.do": "4.0",
    "thirdpartyreportpdf.do": "4.0",
}

# Sandbox API
SANDBOX_API_VERSIONS = {
    "createsandbox.do": "5.0",
    "getsandboxlist.do": "5.0",
    "promotesandbox.do": "5.0",
    "updatesandbox.do": "5.0",
    "deletesandbox.do": "5.0",
}

## Config Options
REQUIRED_CONFIG_ATTRIBUTES_API = {"app_name"}
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
