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

Please make sure all the test are passing before creating merge request.