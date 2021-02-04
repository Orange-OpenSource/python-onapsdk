Development
############



Setting up development environment
----------------------------------
Before you start, ensure you have Python installation in version 3.7 or higher.
Please see the official Python documentation_ in case you have to upgrade or install
certain Python version.

.. _documentation: https://docs.python.org/3/using/index.html

Clone the project. Inside the project folder create a new virtual environment and activate
it:

.. code:: shell

    $ python -m venv env
    $ source env/bin/activate

On Windows, activate by executing the following:

.. code:: powershell

    $ .\env\Scripts\activate

When your virtual environment is ready, install required dependencies:

.. code:: shell

    $ pip install -r requirements.txt

Developing
----------

To use library functions directly from the source code, execute the following
to point to the source folder in *PYTHONPATH* variable and run the interpreter:


.. code:: shell

    $ PYTHONPATH=$PYTHONPATH:src/ python


On Windows:

.. code:: powershell

    $ $env:PYTHONPATH='src\';python

Verify that packages are accessible:

.. code:: python

    >>> import onapsdk

You can then start working with library functions as needed.

New ONAP component package
--------------------------

When you create a new ONAP component package and wants to use Jinja templates you need to create `templates` directory
to store them in a newly created package. Furthermore you need to add a `PackageLoader` in `utils.jinja` module.

Testing
-------

Install tox:

.. code:: shell

    $ pip install tox

To run all unit test, lint and docstyle checks, inside the project folder simply
execute *tox*:

.. code:: shell

    $ tox

Please note that the above runs unit tests on all major versions of Python available on your
OS (3.7, 3.8, 3.9). To limit execution to only specific version of Python Interpreter,
use the following example:

.. code:: shell

    $ tox -e py37

Integration testing
-------------------

It is possible to run integration tests using mock-servers_ project.

.. _mock-servers: https://gitlab.com/Orange-OpenSource/lfn/onap/mock_servers

Make sure Docker Compose is available on your system. Install required dependencies:

.. code:: shell

    $ pip install pytest mock

Go to *integration_tests/* directory and execute:

.. code:: shell

    $ docker-compose up

Please note that *docker-compose* attempts to create subnet 172.20.0.0/24, so it can not be run if the scope is already allocated.
Also, containers are not reachable by their IP addresses on Windows host since
Docker for Windows does not support bridged network interface for Linux containers.
For reference, please see Docker docs_.

.. _docs: https://docs.docker.com/docker-for-windows/networking/#known-limitations-use-cases-and-workarounds

Once containers are running, execute the following in the project's directory:

.. code:: shell

    $ PYTHONPATH=$PYTHONPATH:integration_tests/:src/ ONAP_PYTHON_SDK_SETTINGS="local_urls" pytest -c /dev/null --verbose --junitxml=pytest-integration.xml integration_tests

Please make sure all the test are passing before creating merge request.