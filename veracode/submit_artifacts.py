#!/usr/bin/env python3
"""
A python module to submit artifacts to an app in Veracode via their XML Upload API
"""

# built-ins
import logging
from pathlib import Path
from typing import List, Union

# third party
from requests.exceptions import HTTPError, Timeout, RequestException, TooManyRedirects

# custom
from veracode.api import UploadAPI, SandboxAPI
from veracode.utils import validate, element_contains_error
from veracode import constants
from veracode import __project_name__

LOG = logging.getLogger(__project_name__ + "." + __name__)


@validate
def create_build(*, upload_api: UploadAPI) -> bool:
    """
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/vhuQ5lMdxRNQWUK1br1mDg
    """
    try:
        endpoint = "createbuild.do"
        params = {"app_id": upload_api.app_id, "version": upload_api.build_id}

        # If a sandbox_id is specified, add it to the params
        if isinstance(upload_api.sandbox_id, str):
            params["sandbox_id"] = upload_api.sandbox_id

        # Create the build
        response = upload_api.http_post(endpoint=endpoint, params=params)
        if element_contains_error(parsed_xml=response):
            LOG.error("Veracode returned an error when attempting to call %s", endpoint)
            return False
        return True
    except (
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
    ):
        LOG.error("Exception encountered when calling the Veracode API")
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

    # If a sandbox_id is specified, add it to the params
    if isinstance(upload_api.sandbox_id, str):
        params["sandbox_id"] = upload_api.sandbox_id

    try:
        response = upload_api.http_post(endpoint=endpoint, params=params)
        if element_contains_error(parsed_xml=response):
            LOG.error("Veracode returned an error when attempting to call %s", endpoint)
            return False
        return True
    except (
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
    ):
        LOG.error("Exception encountered when calling the Veracode API")
        return False


def filter_file(*, artifact: Path) -> bool:
    """
    Filter file upload artifacts
    https://help.veracode.com/reader/4EKhlLSMHm5jC8P8j3XccQ/YP2ecJQmr9vE7~AkYNZJlg

    Would prefer an API to call to pull the Veracode supported suffix(es)
    dynamically, but that doesn't seem to exist
    """
    allowed = False

    if artifact.suffix in constants.WHITELIST_FILE_SUFFIX_SET:
        LOG.debug("Suffix for %s is in the whitelist", artifact)
        allowed = True

    if artifact.suffixes[-2:] == constants.WHITELIST_FILE_SUFFIXES_LIST:
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

    endpoint = "uploadlargefile.do"
    params = {"app_id": upload_api.app_id, "filename": filename}
    headers = {"Content-Type": "binary/octet-stream"}

    # If a sandbox_id is specified, add it to the params
    if isinstance(upload_api.sandbox_id, str):
        params["sandbox_id"] = upload_api.sandbox_id

    try:
        with open(artifact, "rb") as f:
            data = f.read()
            upload_api.http_post(
                endpoint=endpoint, data=data, params=params, headers=headers,
            )
        return True
    except:
        LOG.error(
            "Error encountered when attempting to upload %s to the Veracode Upload API",
            filename,
        )
        raise


@validate
def get_sandbox_id(*, sandbox_api: SandboxAPI) -> Union[str, None]:
    """
    Query for and return the sandbox_id
    """
    try:
        endpoint = "getsandboxlist.do"
        params = {"app_id": sandbox_api.app_id}

        sandboxes = sandbox_api.http_get(endpoint=endpoint, params=params)

        if element_contains_error(parsed_xml=sandboxes):
            LOG.error("Veracode returned an error when attempting to call %s", endpoint)
            raise RuntimeError

        for sandbox in sandboxes:
            if sandbox_api.sandbox_name == sandbox.attrib["sandbox_name"]:
                # Returns the first sandbox_name match as duplicates are not
                # allowed by Veracode
                return sandbox.attrib["sandbox_id"]

        # No sandbox_id exists with the provided sandbox_name
        LOG.info(
            "A sandbox named %s does not exist in application id %s",
            sandbox_api.sandbox_name,
            sandbox_api.app_id,
        )
        return None
    except (
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
        RuntimeError,
    ):
        raise RuntimeError


@validate
def create_sandbox(*, sandbox_api: SandboxAPI) -> str:
    """
    Create a sandbox and return the sandbox_id
    """
    try:
        endpoint = "createsandbox.do"
        params = {
            "app_id": sandbox_api.app_id,
            "sandbox_name": sandbox_api.sandbox_name,
        }

        response = sandbox_api.http_post(endpoint=endpoint, params=params)

        if element_contains_error(parsed_xml=response):
            LOG.error("Veracode returned an error when attempting to call %s", endpoint)
            raise RuntimeError

        try:
            # Because we only make one sandbox at a time, we can use index 0 to
            # extract and then return the sandbox_id
            return response[0].attrib["sandbox_id"]
        except (KeyError, IndexError):
            LOG.error("Unable to extract the sandbox_id from the Veracode response")
            raise RuntimeError
    except (
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
        RuntimeError,
    ):
        raise RuntimeError


@validate
def cancel_build(*, upload_api: UploadAPI) -> bool:
    """
    Cancel an application build
    """
    try:
        endpoint = "deletebuild.do"
        params = {"app_id": upload_api.app_id}

        # If a sandbox_id is specified, add it to the params
        if isinstance(upload_api.sandbox_id, str):
            params["sandbox_id"] = upload_api.sandbox_id

        # https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/rERUQewXKGx2D_zaoi6wGw
        response = upload_api.http_get(endpoint=endpoint, params=params)

        if element_contains_error(parsed_xml=response):
            LOG.error("Veracode returned an error when attempting to call %s", endpoint)
            return False

        if isinstance(upload_api.sandbox_id, str):
            LOG.info(
                "Successfully cancelled the build in sandbox id %s of application id %s",
                upload_api.sandbox_id,
                upload_api.app_id,
            )
            return True

        LOG.info(
            "Successfully cancelled the build application id %s", upload_api.app_id
        )
        return True
    except (
        HTTPError,
        ConnectionError,
        Timeout,
        TooManyRedirects,
        RequestException,
        RuntimeError,
    ):
        return False


@validate
def setup_scan_prereqs(*, upload_api: UploadAPI) -> bool:
    """
    Setup the scan environment prereqs
    """
    # Check to see if this is a Policy scan
    if not isinstance(upload_api.sandbox_id, str):
        if create_build(upload_api=upload_api):
            LOG.debug(
                "Successfully created an application build for app id %s",
                upload_api.app_id,
            )
            return True

        LOG.error("Failed create an application build for app id %s", upload_api.app_id)
        return False

    # This is a sandbox scan
    if create_build(upload_api=upload_api):
        LOG.debug(
            "Successfully created an application build for app id %s sandbox id %s",
            upload_api.app_id,
            upload_api.sandbox_id,
        )
        return True


    # Application build creation was unsuccessful and this is a sandbox
    # scan, attempt to cancel the existing scan and retry
    LOG.info(
        "Failed to create an application build. Attempting to cancel an existing build for app_id %s sandbox %s and retry",
        upload_api.app_id,
        upload_api.sandbox_id,
    )
    if cancel_build(upload_api=upload_api):
        LOG.debug(
            "Retrying the build creation for app_id %s sandbox %s",
            upload_api.app_id,
            upload_api.sandbox_id,
        )
    else:
        LOG.error(
            "Unable to cancel the build for app_id %s sandbox_id %s",
            upload_api.app_id,
            upload_api.sandbox_id,
        )
        return False

    if create_build(upload_api=upload_api):
        LOG.info(
            "Successfully created an application build for app id %s", upload_api.app_id
        )
        return True

    LOG.error("Failed to create an application build for app id %s", upload_api.app_id)
    return False


@validate
def submit_artifacts(  # pylint: disable=too-many-return-statements, too-many-branches
    *, upload_api: UploadAPI, sandbox_api: SandboxAPI = None
) -> bool:
    """
    Submit build artifacts to Veracode for SAST
    """
    artifacts: List[Path] = []

    # If we were provided a sandbox_api object, attempt to get the sandbox_id
    # that maps to the sandbox_name and if it doesn't exist, make one
    if sandbox_api:
        try:
            upload_api.sandbox_id = get_sandbox_id(sandbox_api=sandbox_api)
        except RuntimeError:
            LOG.warning(
                "Unable to get the sandbox_id for sandbox_name %s",
                sandbox_api.sandbox_name,
            )
            return False

        if not upload_api.sandbox_id:
            try:
                upload_api.sandbox_id = create_sandbox(sandbox_api=sandbox_api)
            except RuntimeError:
                LOG.error(
                    "Unable to create a sandbox named %s in app_id %s",
                    sandbox_api.sandbox_name,
                    sandbox_api.app_id,
                )
                return False

    # Setup the scan prereqs
    if not setup_scan_prereqs(upload_api=upload_api):
        # Scan prereq setup failed
        return False
    LOG.info("Successfully setup the scan prerequisites in Veracode")

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
