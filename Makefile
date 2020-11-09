## Initialization
FROM_IMAGE     := python
FROM_IMAGE_TAG := 3.8-alpine
VENDOR         := veracode

COMMIT_HASH    := $(shell git rev-parse HEAD)
IMAGE_NAME     := $(shell python3 -c "from $(VENDOR) import __project_name__; print(__project_name__)")
VERSION        := $(shell python3 -c "from $(VENDOR) import __version__; print(__version__)")


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
.PHONY: all
all: lint test build

.PHONY: clean
clean: clean_python

.PHONY: init
init: init_git

# lint_python may cause issues until https://github.com/psf/black/issues/1194
# is resolved
.PHONY: lint
lint: clean lint_docker lint_git lint_make lint_python lint_yaml

.PHONY: test
test: test_unit test_security

.PHONY: report
report: report_coverage report_security

.PHONY: codecov
codecov: test_unit
	@docker run --rm -e CODECOV_TOKEN=$${CODECOV_TOKEN} -v $$(pwd):/usr/src/app/ --entrypoint "codecov" $(IMAGE_NAME):latest-test_unit --token=$${CODECOV_TOKEN} --file reports/coverage.xml

.PHONY: build
build: clean
	@DOCKER_BUILDKIT=1 docker build --rm -t $(IMAGE_NAME):latest -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):$(COMMIT_HASH) --build-arg "ARG_FROM_IMAGE=$(FROM_IMAGE)" --build-arg "ARG_FROM_IMAGE_TAG=$(FROM_IMAGE_TAG)" --build-arg "ARG_VENDOR=$(VENDOR)" --build-arg "ARG_VERSION=$(VERSION)" .

.PHONY: format
format: clean
	@python3 -c 'print("Reformatting the code...")'
	@find . -type f -name '*.py' -exec docker run --rm -v $$(pwd):/data cytopia/black@sha256:20af8eecc054b0bf321ff5cbaf2a3b4bab7611fb093620b42d61a866206c7b6e {} +


## Individual Rules
# Python clean-up
.PHONY: clean_python
clean_python:
	@# Prepending each recipe with - to continue regardless of errors per
	@# https://www.gnu.org/software/make/manual/html_node/Errors.html
	@-find . -type d -name '__pycache__' -exec rm -rf {} +
	@-find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@-find . -type d -name '.pytest_cache' -exec rm -rf {} +
	@-find . -type f -name '*.pyc' -delete

.PHONY: init_git
init_git:
	@if ! grep -q "make lint || exit 1" .git/hooks/pre-commit 2>/dev/null ; then echo '# $@ \nmake lint || exit 1' >> .git/hooks/pre-commit && chmod a+x .git/hooks/pre-commit && echo 'Successfully installed `make lint || exit 1` in a pre-commit hook'; fi
	@if ! grep -q "make test || exit 1" .git/hooks/pre-commit 2>/dev/null ; then echo '# $@ \nmake test || exit 1' >> .git/hooks/pre-commit && chmod a+x .git/hooks/pre-commit && echo 'Successfully installed `make test || exit 1` in a pre-commit hook'; fi
	@if ! grep -q "make hook_commit-msg || exit 1" .git/hooks/commit-msg 2>/dev/null ; then echo '# $@ \nmake hook_commit-msg || exit 1' >> .git/hooks/commit-msg && chmod a+x .git/hooks/commit-msg && echo 'Successfully installed `make hook_commit-msg || exit 1` in a commit-msg hook'; fi
	@if ! grep -q "make lint_git || exit 1" .git/hooks/post-rewrite 2>/dev/null ; then echo '# $@ \nmake lint_git || exit 1' >> .git/hooks/post-rewrite && chmod a+x .git/hooks/post-rewrite && echo 'Successfully installed `make lint_git || exit 1` in a post-rewrite hook'; fi

# Helper Rules
.PHONY: requirements
requirements: requirements-to-freeze.txt $(VENDOR)/requirements-to-freeze.txt
	@python3 -c 'print("Updating the requirements.txt files...")'
	@docker run --rm -v $$(pwd):/usr/src/app/ python:3.8 /bin/bash -c "pip3 install -r /usr/src/app/requirements-to-freeze.txt && pip3 freeze > /usr/src/app/requirements.txt"
	@docker run --rm -v $$(pwd):/usr/src/app/ python:3.8 /bin/bash -c "pip3 install -r /usr/src/app/$(VENDOR)/requirements-to-freeze.txt && pip3 freeze > /usr/src/app/$(VENDOR)/requirements.txt"

.PHONY: hook_commit-msg
hook_commit-msg:
	@python3 -c 'print("Linting the latest git commit message...")'
	@docker run --rm -v $$(pwd)/:/usr/src/app/ --entrypoint python $(IMAGE_NAME):latest-test_unit -m gitlint.cli -c title-max-length.line-length=64 --msg-filename ".git/COMMIT_EDITMSG"

.PHONY: push_tag
push_tag:
	@git tag v$(VERSION)
	@git push origin v$(VERSION)

# Linters
.PHONY: lint_docker
lint_docker:
	@python3 -c 'print("Linting the Dockerfile...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

.PHONY: lint_git
lint_git:
	@python3 -c 'print("Linting all git commit messages...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

.PHONY: lint_make
lint_make:
	@python3 -c 'print("Linting the Makefile...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

.PHONY: lint_python
lint_python:
	@python3 -c 'print("Linting Python files...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@
	@find . -type f -name '*.py' -exec docker run --rm -v $$(pwd):/data cytopia/black@sha256:20af8eecc054b0bf321ff5cbaf2a3b4bab7611fb093620b42d61a866206c7b6e --check {} +

.PHONY: lint_types
lint_types:
	@python3 -c 'print("Running a Python static type checker...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

.PHONY: lint_yaml
lint_yaml:
	@python3 -c 'print("Linting the yaml files...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

# Tests
.PHONY: test_complexity
test_complexity:
	@python3 -c 'print("Running complexity tests...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

.PHONY: test_security
test_security:
	@python3 -c 'print("Running security tests...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

.PHONY: test_unit
test_unit:
	@python3 -c 'print("Running unit tests...")'
	@DOCKER_BUILDKIT=1 docker build --rm --target $@ -t $(IMAGE_NAME):latest-$@ .
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-$@

# Report Generators
.PHONY: report_coverage
report_coverage: test_unit
	@python3 -c 'print("Updating the code coverage reports...")'
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_unit report --include='main.py,$(VENDOR)/*.py'
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_unit html --include='main.py,$(VENDOR)/*.py'
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_unit xml --include='main.py,$(VENDOR)/*.py' -o reports/coverage.xml

.PHONY: report_security
report_security: test_security
	@python3 -c 'print("Updating the security testing reports...")'
	@docker run --rm -v $$(pwd):/usr/src/app/ $(IMAGE_NAME):latest-test_security \
		&& /bin/bash -c "find . -type f -name '*.py' -exec bandit --format json -o reports/bandit_report.json {} + \
		&& semgrep --config=p/r2c-ci --exclude='tests' --exclude='reports' --output=reports/semgrep_report.json --strict --verbose ."
