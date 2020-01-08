#!/usr/bin/env python3
"""
A python module to submit artifacts to an app in Veracode via their XML Upload API
"""

# built-ins
import logging
from pathlib import Path
from typing import List

# third party
from requests.exceptions import HTTPError, Timeout, RequestException, TooManyRedirects

# custom
from veracode.api import UploadAPI, validate
from veracode import constants
from veracode import __project_name__

LOG = logging.getLogger(__project_name__ + "." + __name__)


@validate
def create_build(*, upload_api: UploadAPI) -> bool:
    """
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/vhuQ5lMdxRNQWUK1br1mDg
    """
    endpoint = "createbuild.do"

    params = {"app_id": upload_api.app_id, "version": upload_api.build_id}

    try:
        upload_api.http_post(endpoint=endpoint, params=params)
        return True
    except (
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
        RuntimeError,
    ):
        LOG.exception("The Veracode API post to the %s endpoint failed", endpoint)
        return False


@validate
def begin_prescan(*, upload_api: UploadAPI) -> bool:
    """
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/PX5ReM5acqjM~IOVEg2~rA
    """
    endpoint = "beginprescan.do"

    params = {
        "app_id": upload_api.app_id,
        "scan_all_nonfatal_top_level_modules": upload_api.scan_all_nonfatal_top_level_modules,
        "auto_scan": upload_api.auto_scan,
    }

    try:
        upload_api.http_post(endpoint=endpoint, params=params)
        return True
    except:
        LOG.exception("The Veracode API post to the %s endpoint failed", endpoint)
        raise


def filter_file(*, artifact: Path) -> bool:
    """
    Filter file upload artifacts
    https://help.veracode.com/reader/4EKhlLSMHm5jC8P8j3XccQ/YP2ecJQmr9vE7~AkYNZJlg

    Would prefer an API to call to pull accepted suffix(es) dynamically, but I
    couldn't find one """
    allowed = False

    if (
        len(artifact.suffixes) == 1
        and artifact.suffix in constants.WHITELIST_FILE_SUFFIX_SET
    ):
        LOG.debug("Suffix for %s is in the whitelist", artifact)
        allowed = True

    if artifact.suffixes == constants.WHITELIST_FILE_SUFFIXES_LIST:
        LOG.debug("Suffixes for %s are in the whitelist", artifact)
        allowed = True

    if not allowed:
        LOG.warning(
            "%s was filtered out from being uploaded based on its file extension",
            artifact,
        )

    return allowed


@validate
def upload_large_file(*, upload_api: UploadAPI, artifact: Path) -> bool:
    """
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/lzZ1eON0Bkr8iYjNVD9tqw

    This API call will create a new SAST build for an existing app if one does
    not already exist.  However, it prefers to manage the build versions so it
    can be mapped to code across separate systems
    """
    filename = artifact.name

    headers = {"Content-Type": "binary/octet-stream"}
    params = {"app_id": upload_api.app_id, "filename": filename}

    try:
        with open(artifact, "rb") as f:
            data = f.read()
            upload_api.http_post(
                endpoint="uploadlargefile.do",
                data=data,
                params=params,
                headers=headers,
            )
        return True
    except:
        LOG.error(
            "Error encountered when attempting to upload %s to the Veracode Upload API",
            filename,
        )
        raise


@validate
def submit_artifacts(*, upload_api: UploadAPI) -> bool:
    """
    Submit build artifacts to Veracode for SAST
    """
    artifacts: List[Path] = []

    LOG.info("Attempting to create a build")
    if create_build(upload_api=upload_api):
        LOG.info("Successfully called create_build")
    else:
        LOG.error("Failed to call create_build")
        return False

    LOG.info("Beginning pre-upload file filtering")
    for artifact in upload_api.build_dir.iterdir():
        LOG.debug("Calling filter_file on %s", artifact)
        if filter_file(artifact=artifact):
            artifacts += [artifact]

    # Check to see if the artifacts list is empty
    if not artifacts:
        LOG.error("Nothing to upload")
        return False

    LOG.info("Beginning file uploads")
    for artifact in artifacts:
        if upload_large_file(upload_api=upload_api, artifact=artifact):
            LOG.info("Successfully uploaded %s", artifact)
        else:
            LOG.error("Failed to upload %s", artifact)
            return False

    LOG.info("File uploads complete")
    if begin_prescan(upload_api=upload_api):
        LOG.info("Successfully began the prescan")
    else:
        LOG.error("Failed to start the prescan")
        return False

    return True
