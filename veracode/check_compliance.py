#!/usr/bin/env python3
"""
A python module to check the compliance status of an app in Veracode via their XML Results API
"""

# built-ins
import logging
from typing import Union, Optional
from xml.etree import (  # nosec (Used only when TYPE_CHECKING)
    ElementTree as InsecureElementTree,
)

# custom
from veracode.api import ResultsAPI, validate

LOG = logging.getLogger(__name__)


@validate
def get_latest_completed_build(
    *, results_api: ResultsAPI, only_latest: Optional[bool] = True
) -> Union[InsecureElementTree.Element, None]:
    """
    Get the latest completed build build_id for a given app_id
    https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/Q8E6r4JDAN1lykB08oGDSA
    """
    params = {"only_latest": only_latest}
    appbuilds = results_api.http_get(endpoint="getappbuilds.do", params=params)

    # Filter on the provided app_id
    for app in appbuilds:
        if app.attrib["app_id"] == results_api.app_id:
            LOG.debug("Found app_id %s, returning %s", results_api.app_id, app)
            return app

    LOG.debug(
        "Unable to find a completed build for app_id %s, returning None",
        results_api.app_id,
    )
    return None


@validate
def get_policy_compliance_status(*, results_api: ResultsAPI) -> Union[str, None]:
    """
    Retrieve the policy compliance status
    """
    tag = "{https://analysiscenter.veracode.com/schema/2.0/applicationbuilds}build"
    # See https://analysiscenter.veracode.com/resource/2.0/applicationbuilds.xsd
    policy_compliance_status = "Unknown"

    LOG.debug("Calling get_latest_completed_scan")
    latest_completed_build = get_latest_completed_build(results_api=results_api)
    if latest_completed_build:
        for build in latest_completed_build.iter(tag=tag):
            policy_compliance_status = build.attrib["policy_compliance_status"]
    else:
        LOG.warning("No builds detected for app_id %s", results_api.app_id)

    return policy_compliance_status


@validate
def in_compliance(*, results_api: ResultsAPI) -> bool:
    """
    Identify if a policy compliance status is sufficient
    """
    LOG.debug("Calling get_policy_compliance_status")
    compliance_status = get_policy_compliance_status(results_api=results_api)
    if compliance_status != "Unknown":
        LOG.debug(
            "app_id %s has a compliance status of %s",
            results_api.app_id,
            compliance_status,
        )
    else:
        raise ValueError

    return bool(compliance_status == "Pass")


@validate
def check_compliance(*, results_api: ResultsAPI) -> bool:
    """
    Check the compliance status of an app in Veracode
    """
    LOG.debug(
        "Checking to see if the latest build for app_id %s is in compliance",
        results_api.app_id,
    )
    try:
        if not in_compliance(results_api=results_api):
            LOG.warning(
                "The latest build for app %s was not in compliance", results_api.app_id
            )
            if results_api.ignore_compliance_status:
                return True

            return False
    except ValueError:
        LOG.error(
            "Unable to determine the compliance status of app_id %s", results_api.app_id
        )
        return False

    # App was in compliance
    return True
