#!/usr/bin/env python3
"""
Integrate with Veracode's SAST APIs to allow the submission of artifacts for
scanning and checking an app for compliance against the configured policy
"""

# built-ins
import logging
import sys

# custom
from veracode.check_compliance import check_compliance
from veracode.submit_artifacts import submit_artifacts
from veracode.api import ResultsAPI, UploadAPI, configure_environment
from veracode.config import get_config, apply_config


def main() -> None:
    """
    Integration with Veracode Static Analysis
    """
    ## Setup logging, default to warn until the config is parsed
    formatting = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level="WARNING", format=formatting)
    logging.raiseExceptions = True
    log = logging.getLogger("veracode")

    # Get the effective config
    try:
        config = get_config()
    except ValueError:
        log.error("Unable to create a valid configuration")
        sys.exit(1)

    # Update the log level to whatever was set in the config
    logging.getLogger().setLevel(config["loglevel"])

    # Create the API objects and apply the config
    try:
        results_api = apply_config(
            api=ResultsAPI(app_id=config["apis"]["results"]["app_id"]), config=config
        )
        upload_api = apply_config(
            api=UploadAPI(app_id=config["apis"]["upload"]["app_id"]), config=config
        )
    except TypeError:
        log.error("Unable to create valid API objects")
        sys.exit(1)

    # Configure the environment
    for step in config["workflow"]:
        if step == "submit_artifacts":
            configure_environment(
                api_key_id=config["api_key_id"], api_key_secret=config["api_key_secret"]
            )
            if submit_artifacts(upload_api=upload_api):
                log.info("Successfully submit build artifacts for scanning")
            else:
                log.error("Failed to submit build artifacts for scanning")
                sys.exit(1)
        elif step == "check_compliance":
            configure_environment(
                api_key_id=config["api_key_id"], api_key_secret=config["api_key_secret"]
            )
            if not check_compliance(results_api=results_api):
                sys.exit(1)


if __name__ == "__main__":
    main()
