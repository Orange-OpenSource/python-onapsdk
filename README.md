# Python ONAP SDK

an SDK to use ONAP programmatically with Python code

[![Maintainability](https://api.codeclimate.com/v1/badges/858bb5b1aed4b42da2d2/maintainability)](https://codeclimate.com/github/Orange-OpenSource/python-onapsdk/maintainability)
[![Code Coverage](https://gitlab.com/Orange-OpenSource/lfn/onap/python-onapsdk/badges/master/coverage.svg)](https://gitlab.com/Orange-OpenSource/lfn/onap/python-onapsdk/)
[![Documentation Status](https://readthedocs.org/projects/python-onapsdk/badge/?version=latest)](https://python-onapsdk.readthedocs.io/en/latest/?badge=latest)

## Custom settings

It's possible to use custom settings to overwrite custom values or add new one
to `onapsdk.configuration.settings` module. Pass the path to your settings
module as an environment variable `ONAP_PYTHON_SDK_SETTINGS`. If your file
structure looks:

```shell
module
|
|-- my_settings.py
|
|-- my_awesome_script.py
```

you can just call:

```shell
ONAP_PYTHON_SDK_SETTINGS=my_settings my_awesome_script.py
```

and then all uppercase attributes from `my_settings.py` will be available in
`onapsdk.configuration.settings` module.

[~ Dependencies scanned by PyUp.io ~]
