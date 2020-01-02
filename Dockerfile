## Global
ARG ARG_FROM_IMAGE=python
ARG ARG_FROM_IMAGE_TAG=3.8-alpine

## Builder
# https://hub.docker.com/_/python?tab=tags
FROM python:3.8 AS builder
ARG ARG_VENDOR=veracode
ENV ENV_VENDOR=${ARG_VENDOR}
WORKDIR /usr/src/app/
# The requirements.txt files are separated to improve Docker caching
COPY ./requirements.txt /usr/src/app/requirements.txt
COPY ./${ENV_VENDOR}/requirements.txt /usr/src/app/${ENV_VENDOR}/requirements.txt
ENV PATH=/root/.local/bin:$PATH
RUN pip3 install --user -r requirements.txt && pip3 install --user -r ${ENV_VENDOR}/requirements.txt
COPY ./ ./

## Lint Docker
# https://hub.docker.com/r/hadolint/hadolint/tags
FROM hadolint/hadolint:v1 AS lint_docker
WORKDIR /usr/src/app/
COPY --from=builder /usr/src/app/ .
RUN ["hadolint", "Dockerfile"]

## Lint git
FROM builder AS lint_git
RUN ["gitlint", "--commits", "HEAD"]

## Lint Makefile
# https://hub.docker.com/r/cytopia/checkmake/tags
FROM cytopia/checkmake:0.1.0 AS lint_make
WORKDIR /usr/src/app/
COPY --from=builder /usr/src/app/ .
RUN ["checkmake", "Makefile"]

## Lint Python
FROM builder AS lint_python
RUN find . -type f -name '*.py' -exec pylint -j 0 {} +

## Lint yaml
FROM builder AS lint_yaml
RUN find . -type f \( -name '*.yml' -o -name '*.yaml' \) -exec yamllint {} +

## Type Annotations Linter
#FROM builder AS lint_types
#RUN find "${ENV_VENDOR}" -type f -name '*.py' -exec mypy {} +

## Complexity Linter
#FROM builder AS lint_complexity
#RUN find "${ENV_VENDOR}" -type f -name '*.py' -exec xenon --max-absolute B {} +

## Unit Tests
FROM builder AS test_unit
RUN coverage run -m unittest discover -s tests -p "test_*.py"

## Security Tests
FROM builder AS test_security
RUN find . -type f -name '*.py' -exec bandit {} + && \
  trufflehog --regex --entropy=False file:///usr/src/app/ --exclude_paths .truffleHog-exclude.txt

## easy_sast
FROM "${ARG_FROM_IMAGE}":"${ARG_FROM_IMAGE_TAG}" as Final

ARG ARG_VERSION
WORKDIR /usr/src/app/

LABEL MAINTAINER="Seiso"
LABEL AUTHOR="Jon Zeolla"
LABEL COPYRIGHT="(c) 2020 Seiso, LLC"
LABEL LICENSE="BSD-3-Clause"
LABEL VERSION="${ARG_VERSION}"

COPY --from=builder "/usr/src/app/${ENV_VENDOR}" "./${ENV_VENDOR}"
COPY --from=builder /usr/src/app/main.py main.py
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

# Assumes that the compiled files/debug symbols are in a folder which is volume
# mapped to /build
ENTRYPOINT ["/usr/src/app/main.py"]
