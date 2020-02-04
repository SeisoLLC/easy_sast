<h1 align="center">Easy SAST</h1>
<p align="center">
<a href="https://github.com/SeisoLLC/easy_sast/actions"><img alt="CI: GitHub Actions" src="https://github.com/seisollc/easy_sast/workflows/Docker%20Image%20CI/badge.svg"></a>
<a href="https://codecov.io/gh/seisollc/easy_sast"><img alt="CI: Code Coverage" src="https://codecov.io/gh/seisollc/easy_sast/branch/master/graph/badge.svg"></a>
<a href="https://snyk.io/test/github/seisollc/easy_sast"><img alt="Security: Snyk Vulnerabilities" src="https://snyk.io/test/github/seisollc/easy_sast/badge.svg"></a>
<a href="https://github.com/PyCQA/bandit"><img alt="Security: Bandit" src="https://img.shields.io/badge/security-bandit-yellow.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://opensource.org/licenses/BSD-3-Clause"><img alt="License: BSD 3-Clause" src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg"></a>
</p>

easy_sast is a docker container for use in integration pipelines to submit an application's build artifacts to a static analysis tool. This has been developed in a way to serve as a build pattern for other containers meant to facilitate similar functionality, and natively integrates with Veracode's Static Analysis product.

 - [Features](#features)
 - [Quickstart](#quickstart)
 - [Usage](#usage)
 - [Contributing](#contributing)

easy_sast is available from [Docker Hub](https://hub.docker.com/r/seiso/easy_sast) by running `docker pull seiso/easy_sast`

For advanced usage and more information, see [the wiki](https://github.com/SeisoLLC/easy_sast/wiki/).

## Features
This code base was developed in line with the <b>[Rugged Manifesto](https://ruggedsoftware.org)</b>.  As such, it is:
 - <b>Simple to use</b>: With workflow options and configurations that intuitively understand DevOps.
 - <b>Easily configurable</b>: Practical defaults, and numerous configuration options such as a config file, environment variables, and/or CLI arguments.
 - <b>Clear and understandable code</b>: Regular use of type hints, keyword arguments, and a normalized code style make understanding the code intent easy.
 - <b>Engineered to be robust</b>: Error handling, automated security validation, and pervasive validation.
 - <b>100% tested</b>: 100% code coverage for unit tests on all commits.
 - <b>100% consistently formatted</b>: Linting of Docker, make, YAML, git commits, and Python on all commits.

## Quickstart
### Prerequisites
In order to build and run this project, we recommend you have Docker 18.09 or newer, find, git, GNU make, and Python 3.

### Setup
#### Integration requirements
In order to integrate with Veracode, you will need to:
 - Be able to produce a [debug build of your application](https://help.veracode.com/reader/wySvh2U7LWNYqeVS7PQm_g/4FE4jcdxZZ3kUqdR1aSZqA).
 - Have a valid account and license to use [Veracode's SAST product](https://www.veracode.com/products/binary-static-analysis-sast) APIs outlined [below](#supported-veracode-apis).
 - Have an application in [Veracode's Analysis Center](https://analysiscenter.veracode.com) that you intend to use.

#### Getting started
1. Build the docker image:
    ```bash
    make build
    ```
1. Run the docker container, passing it your API credentials and mounting the directory containing your build artifacts into /build:
    ```bash
    docker run -e VERACODE_API_KEY_ID=EXAMPLE -e VERACODE_API_KEY_SECRET=EXAMPLE -v "/path/to/build":/build easy_sast:latest
    ```

Additional details and configuration options are outlined in [usage](#usage) and on the [wiki](https://github.com/SeisoLLC/easy_sast/wiki/).

## Usage
### Command-line
```bash
usage: main.py [-h] [--api-key-id API_KEY_ID] [--api-key-secret API_KEY_SECRET]
               [--app-id APP_ID] [--build-dir BUILD_DIR] [--build-id BUILD_ID]
               [--config-file CONFIG_FILE] [--disable-auto-scan]
               [--disable-scan-nonfatal-modules] [--ignore-compliance-status]
               [--sandbox-name SANDBOX_NAME] [--version]
               [--workflow WORKFLOW [WORKFLOW ...]] [--debug | --verbose]

optional arguments:
  -h, --help                          show this help message and exit
  --api-key-id API_KEY_ID             veracode api key id
  --api-key-secret API_KEY_SECRET     veracode api key secret
  --app-id APP_ID                     application id as provided by Veracode
  --build-dir BUILD_DIR               a Path containing build artifacts
  --build-id BUILD_ID                 application build id
  --config-file CONFIG_FILE           specify a config file
  --disable-auto-scan                 disable auto_scan
  --disable-scan-nonfatal-modules     disable scan_all_nonfatal_top_level_modules
  --ignore-compliance-status          ignore (but still check) the compliance status
  --sandbox-name SANDBOX_NAME         sandbox_name for the Veracode application
  --version                           show program's version number and exit
  --workflow WORKFLOW [WORKFLOW ...]  specify the workflow steps to enable and order
  --debug                             enable debug level logging
  --verbose                           enable info level logging
```
There are numerous ways to pass information into a running docker container.  For instance:
 1. Pass environment variables to `docker run` using [`-e`](https://docs.docker.com/engine/reference/run/#env-environment-variables). For example:
     ```bash
     docker run -e VERACODE_API_KEY_ID=EXAMPLE -v "/path/to/build":/build easy_sast:latest
     ```
 1. You may also want to pass an argument to the Python in the container by appending your arguments to `docker run`. For example:
     ```bash
     docker run -e VERACODE_API_KEY_ID=EXAMPLE easy_sast:latest --workflow check_compliance --app-id=31337
     ```
 1. Finally, you can pass your environment variables to `docker run` using an [`env-file`](https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file), for example:
     ```bash
     docker run --env-file=example_env_file -v "/path/to/build":/build easy_sast:latest
     ```

Want to learn about more advanced usage, such as optimizing SAST for pull requests?  Check out [the wiki](https://github.com/SeisoLLC/easy_sast/wiki/).

### Supported Veracode APIs
 - [Upload API](https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/G1Nd5yH0QSlT~vPccPhtRQ)
 - [Results API](https://help.veracode.com/reader/LMv_dtSHyb7iIxAQznC~9w/Mp2BEkLx6rD87k465BWqQg)

If you'd like to see support for more Veracode APIs or workflows to interact with those APIs, please [open an issue](https://github.com/SeisoLLC/easy_sast/issues) and let us know!

## Contributing
1. [Fork the repository](https://github.com/SeisoLLC/easy_sast/fork)
1. Create a feature branch via `git checkout -b feature/description`
1. Make your changes
1. Commit your changes via `git commit -am 'Summarize the changes here'`
1. Create a new pull request ([how-to](https://help.github.com/articles/creating-a-pull-request/))
