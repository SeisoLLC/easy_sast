#!/usr/bin/env python3
"""
Constants for use during tests
"""

# built-ins
import copy
import secrets
from pathlib import Path
from typing import Dict, List, Union
from xml.etree import (  # nosec (Used only when TYPE_CHECKING)
    ElementTree as InsecureElementTree,
)

# third party
from defusedxml import ElementTree
import yaml

## Sample results API environmental information
VALID_RESULTS_API: Dict[str, Union[str, bool, Dict[str, str]]] = {}
VALID_RESULTS_API["base_url"] = "https://analysiscenter.veracode.com/api/"
VALID_RESULTS_API["version"] = {
    "detailedreport.do": "5.0",
    "detailedreportpdf.do": "4.0",
    "getaccountcustomfieldlist.do": "5.0",
    "getappbuilds.do": "4.0",
    "getcallstacks.do": "5.0",
    "summaryreport.do": "4.0",
    "summaryreportpdf.do": "4.0",
    "thirdpartyreportpdf.do": "4.0",
}
VALID_RESULTS_API["app_id"] = "1337"
VALID_RESULTS_API["api_key_id"] = secrets.token_hex(16)
VALID_RESULTS_API["api_key_secret"] = secrets.token_hex(64)  # nosec
VALID_RESULTS_API["ignore_compliance_status"] = False


VALID_RESULTS_API_DIFFERENT_APP_ID = {}
VALID_RESULTS_API_DIFFERENT_APP_ID.update(VALID_RESULTS_API)
VALID_RESULTS_API_DIFFERENT_APP_ID["app_id"] = "31337"


INVALID_RESULTS_API_MISSING_VERSION_KEY = {}
INVALID_RESULTS_API_MISSING_VERSION_KEY.update(VALID_RESULTS_API)
del INVALID_RESULTS_API_MISSING_VERSION_KEY["version"]


INVALID_RESULTS_API_INCORRECT_APP_ID: Dict[
    str, Union[str, bool, int, Dict[str, str]]
] = {}
INVALID_RESULTS_API_INCORRECT_APP_ID.update(VALID_RESULTS_API)
INVALID_RESULTS_API_INCORRECT_APP_ID["app_id"] = 1337


INVALID_RESULTS_API_INCORRECT_VERSION_VALUES: Dict[
    str, Union[str, bool, Union[Dict[str, str], Dict[str, float]]]
] = {}
INVALID_RESULTS_API_INCORRECT_VERSION_VALUES.update(VALID_RESULTS_API)
INVALID_RESULTS_API_INCORRECT_VERSION_VALUES["version"] = {
    "detailedreport.do": 5.0,
    "detailedreportpdf.do": 4.0,
    "getaccountcustomfieldlist.do": 5.0,
    "getappbuilds.do": 4.0,
    "getcallstacks.do": 5.0,
    "summaryreport.do": 4.0,
    "summaryreportpdf.do": 4.0,
    "thirdpartyreportpdf.do": 4.0,
}


INVALID_RESULTS_API_MISSING_DOMAIN = {}
INVALID_RESULTS_API_MISSING_DOMAIN.update(VALID_RESULTS_API)
INVALID_RESULTS_API_MISSING_DOMAIN["base_url"] = "https:///api/"

INVALID_RESULTS_API_INCORRECT_COMPLIANCE_STATUS = {}
INVALID_RESULTS_API_INCORRECT_COMPLIANCE_STATUS.update(VALID_RESULTS_API)
INVALID_RESULTS_API_INCORRECT_COMPLIANCE_STATUS["ignore_compliance_status"] = "True"

INVALID_RESULTS_API_INVALID_PORT = {}
INVALID_RESULTS_API_INVALID_PORT.update(VALID_RESULTS_API)
INVALID_RESULTS_API_INVALID_PORT[
    "base_url"
] = "https://analysiscenter.veracode.com:65536/api/"

VALID_RESULTS_API_WITH_PORT_IN_URL = {}
VALID_RESULTS_API_WITH_PORT_IN_URL.update(VALID_RESULTS_API)
VALID_RESULTS_API_WITH_PORT_IN_URL[
    "base_url"
] = "https://analysiscenter.veracode.com:443/api/"


# Valid Results API getappbuilds.do information, but no
# policy_compliance_status
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS: Dict[
    str, Union[str, bytes, InsecureElementTree.Element]
] = {}
# Unfortunately, this varies slightly from the Veracode-provided example
# because (1) the xml library cannot parse the XML using a XSD file, and (2)
# the placeholders Veracode provided in its documentation result in invalid XML
# regardless.
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
    "string"
] = """<?xml version="1.0" encoding="UTF-8"?>

<applicationbuilds xmlns:xsi="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance"
         xmlns="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applicationbuilds"
         xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applicationbuilds
         https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;2.0&#x2f;applicationbuilds.xsd"
         account_id="00000000001">
    <application app_name="app name" app_id="1337" industry_vertical="Manufacturing" assurance_level="Very High"
         business_criticality="Very High" origin="Not Specified" modified_date="2019-08-13T14&#x3a;00&#x3a;10-04&#x3a;00"
         cots="false" business_unit="Not Specified" tags="">
      <customfield name="Custom 1" value=""/>
      <customfield name="Custom 2" value=""/>
      <customfield name="Custom 3" value=""/>
      <customfield name="Custom 4" value=""/>
      <customfield name="Custom 5" value=""/>
      <customfield name="Custom 6" value=""/>
      <customfield name="Custom 7" value=""/>
      <customfield name="Custom 8" value=""/>
      <customfield name="Custom 9" value=""/>
      <customfield name="Custom 10" value=""/>
   </application>
</applicationbuilds>
<!-- Parameters&#x3a; report_changed_since&#x3d;08&#x2f;25&#x2f;2019 only_latest&#x3d;true include_in_progress&#x3d;false -->"""  # pylint: disable=line-too-long
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS["bytes"] = bytes(
    VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS["string"], "utf-8"
)
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS[
    "Element"
] = ElementTree.fromstring(
    VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS["bytes"]
)

# Valid Results API getappbuilds.do information, with a failing
# policy_compliance_status
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS = {}
# Variant of
# VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS to
# add a failing policy_compliance_status
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS[
    "string"
] = """<?xml version="1.0" encoding="UTF-8"?>

<applicationbuilds xmlns:xsi="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance"
         xmlns="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applicationbuilds"
         xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applicationbuilds
         https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;2.0&#x2f;applicationbuilds.xsd"
         account_id="00000000001">
    <application app_name="app name" app_id="1337" industry_vertical="Manufacturing" assurance_level="Very High"
         business_criticality="Very High" origin="Not Specified" modified_date="2019-08-13T14&#x3a;00&#x3a;10-04&#x3a;00"
         cots="false" business_unit="Not Specified" tags="">
      <customfield name="Custom 1" value=""/>
      <customfield name="Custom 2" value=""/>
      <customfield name="Custom 3" value=""/>
      <customfield name="Custom 4" value=""/>
      <customfield name="Custom 5" value=""/>
      <customfield name="Custom 6" value=""/>
      <customfield name="Custom 7" value=""/>
      <customfield name="Custom 8" value=""/>
      <customfield name="Custom 9" value=""/>
      <customfield name="Custom 10" value=""/>
      <build version="2019-10 Testing" build_id="1234321" submitter="Jon Zeolla" platform="Not Specified" lifecycle_stage="Deployed &#x28;In production and actively developed&#x29;" results_ready="true" policy_name="Veracode Recommended Medium" policy_version="1" policy_compliance_status="Did Not Pass" rules_status="Did Not Pass" grace_period_expired="false" scan_overdue="false">
         <analysis_unit analysis_type="Static" published_date="2019-10-13T16&#x3a;20&#x3a;30-04&#x3a;00" published_date_sec="1570998030" status="Results Ready"/>
      </build>
   </application>
</applicationbuilds>
<!-- Parameters&#x3a; report_changed_since&#x3d;08&#x2f;25&#x2f;2019 only_latest&#x3d;true include_in_progress&#x3d;false -->"""  # pylint: disable=line-too-long
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS[
    "bytes"
] = bytes(
    VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS[
        "string"
    ],
    "utf-8",
)
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS[
    "Element"
] = ElementTree.fromstring(
    VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_FAILING_POLICY_COMPLIANCE_STATUS[
        "bytes"
    ]
)

# Valid Results API getappbuilds.do information, with a passing
# policy_compliance_status
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS = {}
# Variant of
# VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_NO_BUILDS to
# add a passing policy_compliance_status
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
    "string"
] = """<?xml version="1.0" encoding="UTF-8"?>

<applicationbuilds xmlns:xsi="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance"
         xmlns="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applicationbuilds"
         xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applicationbuilds
         https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;2.0&#x2f;applicationbuilds.xsd"
         account_id="00000000001">
    <application app_name="app name" app_id="1337" industry_vertical="Manufacturing" assurance_level="Very High"
         business_criticality="Very High" origin="Not Specified" modified_date="2019-08-13T14&#x3a;00&#x3a;10-04&#x3a;00"
         cots="false" business_unit="Not Specified" tags="">
      <customfield name="Custom 1" value=""/>
      <customfield name="Custom 2" value=""/>
      <customfield name="Custom 3" value=""/>
      <customfield name="Custom 4" value=""/>
      <customfield name="Custom 5" value=""/>
      <customfield name="Custom 6" value=""/>
      <customfield name="Custom 7" value=""/>
      <customfield name="Custom 8" value=""/>
      <customfield name="Custom 9" value=""/>
      <customfield name="Custom 10" value=""/>
      <build version="2019-10 Testing" build_id="1234321" submitter="Jon Zeolla" platform="Not Specified" lifecycle_stage="Deployed &#x28;In production and actively developed&#x29;" results_ready="true" policy_name="Veracode Recommended Medium" policy_version="1" policy_compliance_status="Pass" rules_status="Pass" grace_period_expired="false" scan_overdue="false">
         <analysis_unit analysis_type="Static" published_date="2019-10-13T16&#x3a;20&#x3a;30-04&#x3a;00" published_date_sec="1570998030" status="Results Ready"/>
      </build>
   </application>
</applicationbuilds>
<!-- Parameters&#x3a; report_changed_since&#x3d;08&#x2f;25&#x2f;2019 only_latest&#x3d;true include_in_progress&#x3d;false -->"""  # pylint: disable=line-too-long
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
    "bytes"
] = bytes(
    VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
        "string"
    ],
    "utf-8",
)
VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
    "Element"
] = ElementTree.fromstring(
    VALID_RESULTS_API_GETAPPBUILDS_RESPONSE_XML_PASSING_POLICY_COMPLIANCE_STATUS[
        "bytes"
    ]
)

## Sample upload API environmental information
VALID_UPLOAD_API: Dict[str, Union[str, Dict[str, str], Path, bool]] = {}
VALID_UPLOAD_API["base_url"] = "https://analysiscenter.veracode.com/api/"
VALID_UPLOAD_API["version"] = {
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
VALID_UPLOAD_API["app_id"] = "1337"
VALID_UPLOAD_API["build_dir"] = Path("/usr/local/bin/").absolute()
VALID_UPLOAD_API["build_id"] = "v1.2.3"
VALID_UPLOAD_API["scan_all_nonfatal_top_level_modules"] = True
VALID_UPLOAD_API["auto_scan"] = True
VALID_UPLOAD_API["api_key_id"] = secrets.token_hex(16)
VALID_UPLOAD_API["api_key_secret"] = secrets.token_hex(64)  # nosec


INVALID_UPLOAD_API_MISSING_BUILD_DIR = {}
INVALID_UPLOAD_API_MISSING_BUILD_DIR.update(VALID_UPLOAD_API)
del INVALID_UPLOAD_API_MISSING_BUILD_DIR["build_dir"]


INVALID_UPLOAD_API_BUILD_DIR = {}
INVALID_UPLOAD_API_BUILD_DIR.update(VALID_UPLOAD_API)
INVALID_UPLOAD_API_BUILD_DIR["build_dir"] = "/usr/local/bin/"


INVALID_UPLOAD_API_MISSING_DOMAIN = {}
INVALID_UPLOAD_API_MISSING_DOMAIN.update(VALID_UPLOAD_API)
INVALID_UPLOAD_API_MISSING_DOMAIN["base_url"] = "https:///api/"


INVALID_UPLOAD_API_INCORRECT_VERSION_VALUES: Dict[
    str, Union[str, Union[Dict[str, str], Dict[str, float]], Path, bool]
] = {}
INVALID_UPLOAD_API_INCORRECT_VERSION_VALUES.update(VALID_UPLOAD_API)
INVALID_UPLOAD_API_INCORRECT_VERSION_VALUES["version"] = {
    "beginprescan.do": 5.0,
    "beginscan.do": 5.0,
    "createapp.do": 5.0,
    "createbuild.do": 5.0,
    "deleteapp.do": 5.0,
    "deletebuild.do": 5.0,
    "getappinfo.do": 5.0,
    "getapplist.do": 5.0,
    "getbuildinfo.do": 5.0,
    "getbuildlist.do": 5.0,
    "getfilelist.do": 5.0,
    "getpolicylist.do": 5.0,
    "getprescanresults.do": 5.0,
    "getvendorlist.do": 5.0,
    "removefile.do": 5.0,
    "updateapp.do": 5.0,
    "updatebuild.do": 5.0,
    "uploadfile.do": 5.0,
    "uploadlargefile.do": 5.0,
}


INVALID_UPLOAD_API_BUILD_ID = {}
INVALID_UPLOAD_API_BUILD_ID.update(VALID_UPLOAD_API)
INVALID_UPLOAD_API_BUILD_ID["build_id"] = "invalid(build_id)"


INVALID_UPLOAD_API_SCAN_ALL_NONFATAL_TOP_LEVEL_MODULES = {}
INVALID_UPLOAD_API_SCAN_ALL_NONFATAL_TOP_LEVEL_MODULES.update(VALID_UPLOAD_API)
INVALID_UPLOAD_API_SCAN_ALL_NONFATAL_TOP_LEVEL_MODULES[
    "scan_all_nonfatal_top_level_modules"
] = "True"


INVALID_UPLOAD_API_AUTO_SCAN = {}
INVALID_UPLOAD_API_AUTO_SCAN.update(VALID_UPLOAD_API)
INVALID_UPLOAD_API_AUTO_SCAN["auto_scan"] = "False"

# Valid Upload API uploadlargefile.do information
# https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/lzZ1eON0Bkr8iYjNVD9tqw
VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML = {}
# Unfortunately, this varies slightly from the Veracode-provided example
# because (1) the xml library cannot parse the XML using a XSD file, and (2)
# the placeholders Veracode provided in its documentation result in invalid XML
# regardless.
VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML[
    "string"
] = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>

<filelist xmlns="https://analysiscenter.veracode.com/schema/2.0/filelist"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      account_id="00000000001" app_id="1337" build_id="3131313131" filelist_version="1.1"
      xsi:schemaLocation="https://analysiscenter.veracode.com/schema/2.0/filelist
      https://analysiscenter.veracode.com/resource/2.0/filelist.xsd">
   <file file_id="-9223372036854775808" file_name="valid_file.pdb" file_status="Uploaded"/>
</filelist>"""
VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML["bytes"] = bytes(
    VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML["string"], "utf-8"
)
VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML["Element"] = ElementTree.fromstring(
    VALID_UPLOAD_API_UPLOADLARGEFILE_RESPONSE_XML["bytes"]
)

# Valid Upload API beginprescan.do information
# https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/PX5ReM5acqjM~IOVEg2~rA
VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML = {}
# Unfortunately, this varies slightly from the Veracode-provided example
# because (1) the xml library cannot parse the XML using a XSD file, and (2)
# the placeholders Veracode provided in its documentation result in invalid XML
# regardless.
VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML[
    "string"
] = """<?xml version="1.0" encoding="UTF-8"?>

<buildinfo xmlns:xsi="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance" 
      xmlns="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;4.0&#x2f;buildinfo" 
      xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;4.0&#x2f;buildinfo 
      https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;4.0&#x2f;buildinfo.xsd" 
      buildinfo_version="1.4" account_id="00000000001" app_id="1337" build_id="3131313131"> 
   <build version="v1" build_id="3131313131" submitter="JoeUser" platform="Not Specified" 
      lifecycle_stage="Not Specified" results_ready="false" policy_name="Veracode Transitional Very High" 
      policy_version="1" policy_compliance_status="Not Assessed" rules_status="Not Assessed" 
      grace_period_expired="false" scan_overdue="false" legacy_scan_engine="false">
      <analysis_unit analysis_type="Static" status="Pre-Scan Submitted"/>
   </build>
</buildinfo>"""
VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML["bytes"] = bytes(
    VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML["string"], "utf-8"
)
VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML["Element"] = ElementTree.fromstring(
    VALID_UPLOAD_API_BEGINPRESCAN_RESPONSE_XML["bytes"]
)

# Valid Upload API createbuild.do information
# https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/vhuQ5lMdxRNQWUK1br1mDg
VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML = {}
# Unfortunately, this varies slightly from the Veracode-provided example
# because (1) the xml library cannot parse the XML using a XSD file, and (2)
# the placeholders Veracode provided in its documentation result in invalid XML
# regardless.
VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML[
    "string"
] = """<?xml version="1.0" encoding="UTF-8"?>

<buildinfo xmlns:xsi="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance"
      xmlns="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;4.0&#x2f;buildinfo"
      xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;4.0&#x2f;buildinfo
      https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;4.0&#x2f;buildinfo.xsd" buildinfo_version="1.4"
      account_id="00000000001" app_id="1337" sandbox_id="1122" build_id="3131313131"><build version="2019-10 Testing"
      build_id="3131313131" submitter="JoeUser" platform="Not Specified" lifecycle_stage="Not Specified"
      results_ready="false" policy_name="Veracode Transitional Very High" policy_version="1" policy_compliance_status="Not Assessed"
      rules_status="Not Assessed" grace_period_expired="false" scan_overdue="false" legacy_scan_engine="false">
      <analysis_unit analysis_type="Static" status="Incomplete"/>
   </build>
</buildinfo>"""
VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML["bytes"] = bytes(
    VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML["string"], "utf-8"
)
VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML["Element"] = ElementTree.fromstring(
    VALID_UPLOAD_API_CREATEBUILD_RESPONSE_XML["bytes"]
)

# Valid Upload API getappinfo.do information
# https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/kb2SM9net26_L91VploQGw
VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML = {}
# Unfortunately, this varies slightly from the Veracode-provided example
# because (1) the xml library cannot parse the XML using a XSD file, and (2)
# the placeholders Veracode provided in its documentation result in invalid XML
# regardless.
VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML[
    "string"
] = """<?xml version="1.0" encoding="UTF-8"?>

<appinfo xmlns:xsi="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance" 
      xmlns="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;appinfo" 
      xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;appinfo 
      https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;2.0&#x2f;appinfo.xsd" appinfo_version="1.1" 
      account_id="00000000001">
   <application app_id="1337" app_name="app name" description="app description" business_criticality="Very High" 
      policy="Veracode Transitional Very High" policy_updated_date="2019-08-13T14&#x3a;02&#x3a;08-04&#x3a;00" 
      teams="Demo Team" origin="Not Specified" industry_vertical="Other" app_type="Other" deployment_method="Not Specified" 
      is_web_application="false" archer_app_name="archer app name" modified_date="2019-08-15T11&#x3a;27&#x3a;47-04&#x3a;00" 
      cots="false" vast="false" business_unit="Not Specified" tags="">
      <customfield name="Custom 1" value=""/>
      <customfield name="Custom 2" value=""/>
      <customfield name="Custom 3" value=""/>
      <customfield name="Custom 4" value=""/>
      <customfield name="Custom 5" value=""/>
      <customfield name="Custom 6" value=""/>
      <customfield name="Custom 7" value=""/>
      <customfield name="Custom 8" value=""/>
      <customfield name="Custom 9" value=""/>
      <customfield name="Custom 10" value="foo"/>
   </application>
</appinfo>"""
VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML["bytes"] = bytes(
    VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML["string"], "utf-8"
)
VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML["Element"] = ElementTree.fromstring(
    VALID_UPLOAD_API_GETAPPINFO_RESPONSE_XML["bytes"]
)

## Example file info
VALID_FILE: Dict[str, Union[str, List[str], bytes, Path]] = {}
VALID_FILE["name"] = "valid_file.pdb"
VALID_FILE["names"] = [
    "valid_file.exe",
    "valid_file.pdb",
    "valid_file.dll",
    "valid_file.jar",
    "valid_file.zip",
    "valid_file.tar",
    "valid_file.tgz",
    "valid_file.war",
    "valid_file.ear",
    "valid_file.jar",
    "valid_file.apk",
    "valid_file.ipa",
    "valid_file.tar.gz",
    "this.is.a.valid.file.dll",
    "this.is..also..valid.jar",
]
VALID_FILE["bytes"] = b"Seiso was here!\n"
VALID_FILE["Path"] = Path("/path/" + str(VALID_FILE["name"]))

INVALID_FILE: Dict[str, Union[str, List[str], bytes, Path]] = {}
INVALID_FILE["name"] = "invalid_file.tar.gz.bar"
INVALID_FILE["names"] = [
    "invalid_file.thingy",
    "invalid_file",
    "invalid_file.tar.gz.bar",
    "invalid_file.dll.gz",
    "invalid_file.exe.docx",
]
INVALID_FILE["bytes"] = b"Seiso was here!\n"
INVALID_FILE["Path"] = Path("/path/" + str(INVALID_FILE["name"]))


## Veracode error responses
VERACODE_ERROR_RESPONSE_XML: Dict[str, bytes] = {}
VERACODE_ERROR_RESPONSE_XML[
    "bytes"
] = b'<?xml version="1.0" encoding="UTF-8"?>\n\n<error>App not in state where new builds are allowed.</error>\n'  # pylint: disable=line-too-long
VERACODE_ERROR_RESPONSE_XML["Element"] = ElementTree.fromstring(
    VERACODE_ERROR_RESPONSE_XML["bytes"]
)

XML_API_VALID_RESPONSE_XML_ERROR: Dict[str, bytes] = {}
XML_API_VALID_RESPONSE_XML_ERROR[
    "bytes"
] = b'<?xml version="1.0" encoding="UTF-8"?>\n\n<error>Error Message.</error>\n'
XML_API_VALID_RESPONSE_XML_ERROR["Element"] = ElementTree.fromstring(
    XML_API_VALID_RESPONSE_XML_ERROR["bytes"]
)

XML_API_INVALID_RESPONSE_XML_ERROR: Dict[str, bytes] = {}
XML_API_INVALID_RESPONSE_XML_ERROR[
    "bytes"
] = b'<?xml version="1.0" encoding="UTF-8"?>\n\n<Invalid Error Message.</error>\n'


# Configs
INVALID_CONFIG_DIRTY = {
    "a": 1,
    "b": {},
    "c": {"hideme": None, "keepme": "KEEP", "list": ["a", {}, "b", None]},
    "emptydict": {},
    None: "hide",
}
INVALID_CONFIG_NO_NONE = {
    "a": 1,
    "b": {},
    "c": {"keepme": "KEEP", "list": ["a", {}, "b"]},
    "emptydict": {},
}
INVALID_CONFIG_NO_EMPTY_DICT = {
    "a": 1,
    "c": {"hideme": None, "keepme": "KEEP", "list": ["a", "b", None]},
    None: "hide",
}
INVALID_CONFIG_CLEAN = {
    "a": 1,
    "c": {"keepme": "KEEP", "list": ["a", "b"]},
}

SIMPLE_CONFIG_FILE = {}
SIMPLE_CONFIG_FILE["name"] = "easy_sast.yml"
SIMPLE_CONFIG_FILE["Path"] = Path("/path/" + str(SIMPLE_CONFIG_FILE["name"]))
SIMPLE_CONFIG_FILE[
    "string"
] = '''---
loglevel: "WARNING"'''
SIMPLE_CONFIG_FILE["bytes"] = bytes(SIMPLE_CONFIG_FILE["string"], "utf-8")

INVALID_CONFIG_FILES = [
    Path("./easy_sast.yml.gz"),
    Path("./config.txt.yml"),
    Path("./thing.notyml"),
    Path("./not_a_config.pdb"),
    Path("./config.yalm"),
    Path("./yaml.config"),
    Path("./setup.cfg"),
    Path("./config.ini"),
    Path("./file.json"),
    Path("./yaml"),
    Path("./yml"),
    Path("./config"),
]


VALID_CLEAN_FILE_CONFIG = {}
VALID_CLEAN_FILE_CONFIG[
    "string"
] = '''---
apis:
  results:
    base_url: "https://analysiscenter.veracode.com/api/"
    version: {
              "detailedreport.do": "5.0",
              "detailedreportpdf.do": "4.0",
              "getaccountcustomfieldlist.do": "5.0",
              "getappbuilds.do": "4.0",
              "getcallstacks.do": "5.0",
              "summaryreport.do": "4.0",
              "summaryreportpdf.do": "4.0",
              "thirdpartyreportpdf.do": "4.0",
             }
    app_id: "31337"
    ignore_compliance_status: False
  upload:
    base_url: "https://analysiscenter.veracode.com/api/"
    version: {
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
              "uploadlargefile.do": "5.0"
             }
    app_id: "31337"
    build_dir: "/build/"
    build_id: "2037-03-13_03-14-15"
    scan_all_nonfatal_top_level_modules: True
    auto_scan: True
loglevel: "WARNING"
workflow:
  - "submit_artifacts"
  - "check_compliance"'''
VALID_CLEAN_FILE_CONFIG["bytes"] = bytes(VALID_CLEAN_FILE_CONFIG["string"], "utf-8")
VALID_CLEAN_FILE_CONFIG["dict"] = yaml.safe_load(VALID_CLEAN_FILE_CONFIG["bytes"])

# VALID_CLEAN_FILE_CONFIG is already normalized, but separating it here in case
# in the future it isn't and we want to update the places where this is used to
# mock the response to normalized_file_config
VALID_CLEAN_FILE_CONFIG_NORMALIZED = {}
VALID_CLEAN_FILE_CONFIG_NORMALIZED.update(VALID_CLEAN_FILE_CONFIG)

CLEAN_DEFAULT_CONFIG = {
    "workflow": ["submit_artifacts", "check_compliance"],
    "loglevel": "WARNING",
    "apis": {"upload": {}, "results": {}},
}
CLEAN_FILE_CONFIG = {
    "apis": {
        "results": {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "version": {
                "detailedreport.do": "5.0",
                "detailedreportpdf.do": "4.0",
                "getaccountcustomfieldlist.do": "5.0",
                "getappbuilds.do": "4.0",
                "getcallstacks.do": "5.0",
                "summaryreport.do": "4.0",
                "summaryreportpdf.do": "4.0",
                "thirdpartyreportpdf.do": "4.0",
            },
            "app_id": "31337",
            "ignore_compliance_status": False,
        },
        "upload": {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "version": {
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
            },
            "app_id": "31337",
            "build_dir": Path("/build/").absolute(),
            "build_id": "2037-03-13_03-14-15",
            "scan_all_nonfatal_top_level_modules": True,
            "auto_scan": True,
        },
    },
    "loglevel": "WARNING",
    "workflow": ["submit_artifacts", "check_compliance"],
}
CLEAN_ENV_CONFIG = {
    "api_key_id": "95e637f1a25d453cdfdc30a338287ba8",
    "api_key_secret": "f7bb8c01bce05290ac8939f1d27d90ab84d2e05bb4671ca2f88d609d07afa723265348d708bdd0a1707a499528f6aa5c83133f4c5aca06a528d30b61fd4b6b28",
}
CLEAN_ARGS_CONFIG = {
    "config_file": Path("/easy_sast/easy_sast.yml"),
    "apis": {
        "results": {"ignore_compliance_status": False},
        "upload": {"scan_all_nonfatal_top_level_modules": True, "auto_scan": True},
    },
}

CLEAN_FILE_CONFIG_NO_RESULTS_API = copy.deepcopy(CLEAN_FILE_CONFIG)
CLEAN_FILE_CONFIG_NO_RESULTS_API["apis"] = {"upload": {}}

CLEAN_FILE_CONFIG_NO_UPLOAD_API = copy.deepcopy(CLEAN_FILE_CONFIG)
CLEAN_FILE_CONFIG_NO_UPLOAD_API["apis"] = {"results": {}}

CLEAN_EFFECTIVE_CONFIG = {
    "workflow": ["submit_artifacts", "check_compliance"],
    "loglevel": "WARNING",
    "apis": {
        "upload": {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "version": {
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
            },
            "app_id": "31337",
            "build_dir": Path("/build/").absolute(),
            "build_id": "2037-03-13_03-14-15",
            "scan_all_nonfatal_top_level_modules": True,
            "auto_scan": True,
        },
        "results": {
            "base_url": "https://analysiscenter.veracode.com/api/",
            "version": {
                "detailedreport.do": "5.0",
                "detailedreportpdf.do": "4.0",
                "getaccountcustomfieldlist.do": "5.0",
                "getappbuilds.do": "4.0",
                "getcallstacks.do": "5.0",
                "summaryreport.do": "4.0",
                "summaryreportpdf.do": "4.0",
                "thirdpartyreportpdf.do": "4.0",
            },
            "app_id": "31337",
            "ignore_compliance_status": False,
        },
    },
    "api_key_id": "95e637f1a25d453cdfdc30a338287ba8",
    "api_key_secret": "f7bb8c01bce05290ac8939f1d27d90ab84d2e05bb4671ca2f88d609d07afa723265348d708bdd0a1707a499528f6aa5c83133f4c5aca06a528d30b61fd4b6b28",
    "config_file": Path("/easy_sast/easy_sast.yml"),
}
