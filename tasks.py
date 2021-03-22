#!/usr/bin/env python3
"""
Task execution tool & library
"""

import json
import sys
from logging import basicConfig, getLogger
from pathlib import Path

import docker
import git
from invoke import task
from veracode.__init__ import __version__

LOG_FORMAT = json.dumps(
    {
        "timestamp": "%(asctime)s",
        "namespace": "%(name)s",
        "loglevel": "%(levelname)s",
        "message": "%(message)s",
    }
)
basicConfig(level="INFO", format=LOG_FORMAT)
LOG = getLogger("easy_sast")

CWD = Path(".").absolute()
REPO = git.Repo(CWD)
CLIENT = docker.from_env()
IMAGE = "seiso/easy_sast"

# Tasks
@task
def publish(c, tag):  # pylint: disable=unused-argument
    """Publish easy_sast"""
    if tag not in ["latest", "release"]:
        LOG.error("Please provide a tag of either latest or release")
        sys.exit(1)
    elif tag == "release":
        tag = "v" + __version__

    repository = IMAGE + ":" + tag
    LOG.info("Pushing %s to docker hub...", repository)
    CLIENT.images.push(repository=repository)
    LOG.info("Done publishing the %s Docker image", repository)
