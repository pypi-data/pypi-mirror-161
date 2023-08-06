[![PyPI version](https://img.shields.io/pypi/v/sila2?color=blue)](https://pypi.org/project/sila2)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![coverage report](https://img.shields.io/gitlab/coverage/sila2/sila_python/master?job_name=coverage)](https://gitlab.com/sila2/sila_python/)
[![documentation](https://img.shields.io/gitlab/pipeline-status/sila2/sila_python?branch=master&label=docs)](https://sila2.gitlab.io/sila_python)

> :warning: On 2021-11-15, this project replaced a legacy Python implementation of SiLA 2. That project can be found [here](https://gitlab.com/SiLA2/legacy/sila_python_20211115) and is still installable via [`pip install sila2lib`](https://pypi.org/project/sila2lib/).

# SiLA 2 Python Implementation

|||
| ---------------| ----------------------------------------------------------- |
| SiLA Homepage  | [https://sila-standard.com](https://sila-standard.com)      |
| Chat group     | [Join the group on Slack](https://join.slack.com/t/sila-standard/shared_invite/enQtNDI0ODcxMDg5NzkzLTBhOTU3N2I0NTc4NDcyMjg2ZDIwZDc1Yjg4N2FmYjZkMzljZDAyZjAwNTc5OTVjYjIwZWJjYjA0YTY0NTFiNDA)|
| Maintainer     | [Niklas Mertsch](mailto:niklas.mertsch@wega-it.com) ([@NMertsch](https://gitlab.com/NMertsch)) |
| Maintainer     | [Mark Doerr](mailto:mark.doerr@uni-greifswald.de) ([@markdoerr](https://gitlab.com/markdoerr)) |

## Getting started
### Installation
Use `pip install sila2` to install the latest release of the library.

On Raspberry Pi systems, run the following to fix some `ImportErrors`:
- `pip uninstall -y lxml grpcio grpcio-tools`
- `sudo apt install -y python3-lxml python3-grpcio python3-grpc-tools`

### Documentation
A documentation on SiLA Server generation, feature implementation, and usage of SiLA Clients can be found [here](https://sila2.gitlab.io/sila_python/).

### Example
The directory [`example_server`](example_server/) contains an example SiLA Server application. [`example_client_scripts`](example_client_scripts/) contains multiple SiLA Client programs that interact with the example server.

## Implementation status
### Missing parts from SiLA 2 specification
- Lifetime handling for binary transfer
  - currently, large binaries are only deleted on request
- Lifetime handling for observable commands
  - currently, no lifetime is reported and execution UUIDs stay valid indefinitely
- Server-initiated connection (SiLA 2 v1.1)
  - currently, only client-initiated connections are supported

### Deviations from SiLA 2 specification
- [Duration](https://gitlab.com/SiLA2/sila_base/-/blob/master/protobuf/SiLAFramework.proto#L67) is rounded to microseconds, because [`datetime.timedelta`](https://docs.python.org/3.9/library/datetime.html#datetime.timedelta) does not support sub-microsecond precision
- Microseconds of [`datetime.time`](https://docs.python.org/3.9/library/datetime.html#datetime.time) and [`datetime.datetime`](https://docs.python.org/3.9/library/datetime.html#datetime.datetime) are ignored since [Time](https://gitlab.com/SiLA2/sila_base/-/blob/master/protobuf/SiLAFramework.proto#L38) and [Timestamp](https://gitlab.com/SiLA2/sila_base/-/blob/master/protobuf/SiLAFramework.proto#L45) don't support sub-second precision 

## Contributing
Contributions in the form of [issues](https://gitlab.com/SiLA2/sila_python/-/issues), [feature requests](https://gitlab.com/SiLA2/sila_python/-/issues) and merge requests are welcome. To reduce duplicate work, please create an issue and state that you are working on it before you spend significant time on writing code for a merge request.

###  Development
#### Multi-stage build process
Because the `sila2.features` submodule is auto-generated using the code generator included in this library, the build process has multiple steps:
1. Install the library without `sila2.feature`
2. Use the script [`generate-feature-submodule.py`](./generate-feature-submodule.py) to generate `sila2.feature`
3. Install again

#### Development tools
This project uses the following tools to improve code quality:
- [black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for sorting imports
- [flake8](https://flake8.pycqa.org/) for style guide enforcement
- [pytest](https://docs.pytest.org/) for testing
- [pytest-cov](https://github.com/pytest-dev/pytest-cov) for measuring code coverage

The following Python scripts are provided to guide the development process:
- [`run-formatting.py`](run-formatting.py) applies `black` and `isort`
- [`run-checks.py`](run-checks.py) checks for formatting and code style problems, and runs the tests
- [`install-pre-commit-hook.py`](install-pre-commit-hook.py) installs a `pre-commit` [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) to automatically execute a fast-running subset of all checks on each commit

To install all these tools, use `pip install .[dev]`.

#### Documentation build process
To build the documentation, first install this library with `pip install .[docs]`, the run [`docs/make-docs.py`](docs/make-docs.py).
The HTML documentation can then be found at `docs/_build/html`

#### Setup code
The full development setup using the [setuptools development mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) looks like this:
```shell
# clone repository
git clone --recurse-submodules https://gitlab.com/sila2/sila_python
cd sila2

# install sila2 in development mode
pip install -e .[full]  # install without sila2.feature submodule and all optional dependencies
python generate-feature-submodule.py  # generate sila2.feature code (generates src/sila2/feature/...)

# build documentation (generates docs/_build/html)
python docs/make-docs.py

# install example server in development mode (required for tests)
pip install -e example_server

# run test suite
python run-checks.py

# run code formatting
python run-formatting.py

# install git pre-commit hook (generates .git/hooks/pre-commit)
python install-pre-commit-hook.py

# build wheel and source distribution (generates build/ and dist/)
pip install build
python -m build -ws
```
