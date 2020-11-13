# Python ONAP SDK

an SDK to use ONAP programmatically with Python code

[![Maintainability](https://api.codeclimate.com/v1/badges/858bb5b1aed4b42da2d2/maintainability)](https://codeclimate.com/github/Orange-OpenSource/python-onapsdk/maintainability)
[![Code Coverage](https://gitlab.com/Orange-OpenSource/lfn/onap/python-onapsdk/badges/master/coverage.svg)](https://gitlab.com/Orange-OpenSource/lfn/onap/python-onapsdk/)
[![Documentation Status](https://readthedocs.org/projects/python-onapsdk/badge/?version=latest)](https://python-onapsdk.readthedocs.io/en/latest/?badge=latest)

## Description

ONAP SDK is a client library written in Python for building applications to work with ONAP. The project aims to provide a consistent and complete set of interactions with ONAP’s many services, along with complete documentation, examples, and tools.

Using few python commands, you should be able to onboard, distribute models, instantiate xNFs and many others. Check [doc](https://python-onapsdk.readthedocs.io/en/latest/index.html) site to find out all the features.

## Installation

You can install it using `pip` tool

```
$ pip install onapsdk
```

## Development

Before you start, ensure you have Python installation in version 3.7 or higher.
Please see [the official Python documentation](https://docs.python.org/3/using/index.html) 
in case you have to upgrade or install certain Python version.

### Setting up development environment

Clone the project. Inside the project folder create a new virtual environment and activate
it:

```
$ python -m venv env
$ source env/bin/activate
```
On Windows, activate by executing the following:

```
$ .\env\Scripts\activate
```

When your virtual environment is ready, install required dependencies:

```
$ pip install -r requirements.txt
```

### Developing

To use library functions directly from the source code, execute the following
to point to the source folder in *PYTHONPATH* variable and run the interpreter:


```
$ PYTHONPATH=$PYTHONPATH:src/ python
```

On Windows:

```
$ $env:PYTHONPATH='src\';python
```

Verify that packages are accessible:

```
>>> import onapsdk
```
You can then start working with library functions as needed.

### Testing

Install [tox](https://tox.readthedocs.io/en/latest/index.html):

```
$ pip install tox
```

To run all unit test, lint and docstyle checks, inside the project folder simply
execute *tox*:

```
$ tox
```

Please note that the above runs unit tests on all major versions of Python available on your
OS (3.7, 3.8, 3.9). To limit execution to only specific version of Python interpreter,
use the following example:

```
$ tox -e py37
```

### Integration testing

It is possible to run integration tests using [mock-servers](https://gitlab.com/Orange-OpenSource/lfn/onap/mock_servers)
project. 
Make sure Docker Compose is available on your system. Install required dependencies:
```
$ pip install pytest mock
```

Go to *integration_tests/* directory and execute:
```
$ docker-compose up
```
Please note that *docker-compose* attempts to create subnet 172.20.0.0/24, so it can not be run if the scope is already allocated.
Also, containers are not reachable by their IP addresses on Windows host since 
Docker for Windows [does not support](https://docs.docker.com/docker-for-windows/networking/#known-limitations-use-cases-and-workarounds) 
bridged network interface for Linux containers.

Once containers are running, execute the following in the project's directory:
```
$ PYTHONPATH=$PYTHONPATH:integration_tests/:src/ ONAP_PYTHON_SDK_SETTINGS="local_urls" pytest -c /dev/null --verbose --junitxml=pytest-integration.xml integration_tests
```

Please make sure all the test are passing before creating merge request.