Installation
############



Installing with pip
--------------------

.. code:: shell

    $ pip install onapsdk


Customize the configuration
---------------------------

You can customize the global settings of onapsdk by creating an environment
variable ONAP_PYTHON_SDK_SETTINGS and a file my_settings.py.

By default the global settings are retrieved from the file located in
src/onapsdk/configuration/global_settings.py. You can create your own customized
configuration file and reference it through the environement variable.
You can thus copy/paste the existing global_settings.py file, rename it as
my_settings.py, adapt it with your favorite editor and export the environnement
variable accordingly.

It can be useful to move from a nodeport to an an ingress based configuration
or test different API versions.

  .. code:: shell

      $ export ONAP_PYTHON_SDK_SETTINGS="onapsdk.configuration.my_settings"
