## Initialization
DOCKER         := docker
FIND           := find
FROM_IMAGE     := python
FROM_IMAGE_TAG := 3.8-alpine
PIP            := pip3
PYTHON         := python3
VENDOR         := veracode

COMMIT_HASH    := $(shell git rev-parse HEAD)
IMAGE_NAME     := $(shell $(PYTHON) -c "from $(VENDOR) import __project_name__; print(__project_name__)")
VERSION        := $(shell $(PYTHON) -c "from $(VENDOR) import __version__; print(__version__)")


## Validation
ifndef COMMIT_HASH
$(error COMMIT_HASH was not properly set)
endif

ifndef IMAGE_NAME
$(error IMAGE_NAME was not properly set)
endif

ifndef VERSION
$(error VERSION was not properly set)
endif


## Aggregate Rules
clean: clean_python

init: init_git

# lint_python may cause issues until https://github.com/psf/black/issues/1194
# is resolved
lint: clean lint_docker lint_git lint_make lint_python lint_yaml

test: test_unit test_security

report: report_coverage report_security

codecov: test_unit
	@$(DOCKER) run --rm -e CODECOV_TOKEN=$${CODECOV_TOKEN} -v $$(pwd):/usr/src/app/ --entrypoint "codecov" $(IMAGE_NAME):latest-test_unit --token=$${CODECOV_TOKEN} --file reports/coverage.xml

build: clean
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm -t $(IMAGE_NAME):latest -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):$(COMMIT_HASH) --build-arg "ARG_FROM_IMAGE=$(FROM_IMAGE)" --build-arg "ARG_FROM_IMAGE_TAG=$(FROM_IMAGE_TAG)" --build-arg "ARG_VENDOR=$(VENDOR)" --build-arg "ARG_VERSION=$(VERSION)" .

# Experimental feature - https://docs.docker.com/buildx/working-with-buildx/
buildx: clean
	@DOCKER_BUILDKIT=1 $(DOCKER) buildx --rm -t $(IMAGE_NAME):latest -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):$(COMMIT_HASH) --build-arg "ARG_FROM_IMAGE=$(FROM_IMAGE)" --build-arg "ARG_FROM_IMAGE_TAG=$(FROM_IMAGE_TAG)" --build-arg "ARG_VENDOR=$(VENDOR)" --build-arg "ARG_VERSION=$(VERSION)" .

format: clean
	@$(PYTHON) -c 'print("Reformatting the code...")'
	@$(FIND) . -type f -name '*.py' -exec $(DOCKER) run --rm -v $$(pwd):/data cytopia/black@sha256:20af8eecc054b0bf321ff5cbaf2a3b4bab7611fb093620b42d61a866206c7b6e {} +


## Individual Rules
# Python clean-up
clean_python:
	@# Prepending each recipe with - to continue regardless of errors per
	@# https://www.gnu.org/software/make/manual/html_node/Errors.html
	@-$(FIND) . -type d -name '__pycache__' -exec rm -rf {} +
	@-$(FIND) . -type d -name '.mypy_cache' -exec rm -rf {} +
	@-$(FIND) . -type d -name '.pytest_cache' -exec rm -rf {} +
	@-$(FIND) . -type f -name '*.pyc' -delete

init_git:
	@if ! grep -q "make lint || exit 1" .git/hooks/pre-commit 2>/dev/null ; then echo '# $@ \nmake lint || exit 1' >> .git/hooks/pre-commit && chmod a+x .git/hooks/pre-commit && echo 'Successfully installed `make lint || exit 1` in a pre-commit hook'; fi
	@if ! grep -q "make test || exit 1" .git/hooks/pre-commit 2>/dev/null ; then echo '# $@ \nmake test || exit 1' >> .git/hooks/pre-commit && chmod a+x .git/hooks/pre-commit && echo 'Successfully installed `make test || exit 1` in a pre-commit hook'; fi
	@if ! grep -q "make hook_commit-msg || exit 1" .git/hooks/commit-msg 2>/dev/null ; then echo '# $@ \nmake hook_commit-msg || exit 1' >> .git/hooks/commit-msg && chmod a+x .git/hooks/commit-msg && echo 'Successfully installed `make hook_commit-msg || exit 1` in a commit-msg hook'; fi
	@if ! grep -q "make lint_git || exit 1" .git/hooks/post-rewrite 2>/dev/null ; then echo '# $@ \nmake lint_git || exit 1' >> .git/hooks/post-rewrite && chmod a+x .git/hooks/post-rewrite && echo 'Successfully installed `make lint_git || exit 1` in a post-rewrite hook'; fi

# Helper Rules
requirements: requirements-to-freeze.txt $(VENDOR)/requirements-to-freeze.txt
	@$(PYTHON) -c 'print("Updating the requirements.txt files...")'
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ python:3.8 /bin/bash -c "$(PIP) install -r /usr/src/app/requirements-to-freeze.txt && $(PIP) freeze > /usr/src/app/requirements.txt"
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ python:3.8 /bin/bash -c "$(PIP) install -r /usr/src/app/$(VENDOR)/requirements-to-freeze.txt && $(PIP) freeze > /usr/src/app/$(VENDOR)/requirements.txt"

hook_commit-msg:
	@$(PYTHON) -c 'print("Linting the latest git commit message...")'
	@$(DOCKER) run --rm -v $$(pwd)/:/usr/src/app/ --entrypoint python $(IMAGE_NAME):latest-test_unit -m gitlint.cli -c title-max-length.line-length=64 --msg-filename ".git/COMMIT_EDITMSG"

shell:
	@$(DOCKER) run -it --entrypoint /bin/sh easy_sast:latest

push_tag:
	@git tag v$(VERSION)
	@git push origin v$(VERSION)

# Linters
lint_docker:
	@$(PYTHON) -c 'print("Linting the Dockerfile...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

lint_git:
	@$(PYTHON) -c 'print("Linting all git commit messages...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

lint_make:
	@$(PYTHON) -c 'print("Linting the Makefile...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

lint_python:
	@$(PYTHON) -c 'print("Linting Python files...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@
	@$(FIND) . -type f -name '*.py' -exec $(DOCKER) run --rm -v $$(pwd):/data cytopia/black@sha256:20af8eecc054b0bf321ff5cbaf2a3b4bab7611fb093620b42d61a866206c7b6e --check {} +

lint_types:
	@$(PYTHON) -c 'print("Running a Python static type checker...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

lint_yaml:
	@$(PYTHON) -c 'print("Linting the yaml files...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

# Tests
test_complexity:
	@$(PYTHON) -c 'print("Running complexity tests...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

test_security:
	@$(PYTHON) -c 'print("Running security tests...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

test_unit:
	@$(PYTHON) -c 'print("Running unit tests...")'
	@DOCKER_BUILDKIT=1 $(DOCKER) build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

# Report Generators
report_coverage: test_unit
	@$(PYTHON) -c 'print("Updating the code coverage reports...")'
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_unit report --include='main.py,$(VENDOR)/*.py'
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_unit html --include='main.py,$(VENDOR)/*.py'
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_unit xml --include='main.py,$(VENDOR)/*.py' -o reports/coverage.xml

report_security: test_security
	@$(PYTHON) -c 'print("Updating the security testing reports...")'
	@$(DOCKER) run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_security && find . -type f -name '*.py' -exec bandit --format json -o reports/bandit_report.json {} +

.PHONY: clean init lint test build report codecov format clean_python init_git requirements hook_commit-msg shell push_tag lint_docker lint_git lint_make lint_python lint_types lint_yaml test_complexity test_security test_unit report_coverage report_security all
