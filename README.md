# Python ONAP SDK

an SDK to use ONAP programmatically with Python code

[![Maintainability](https://api.codeclimate.com/v1/badges/858bb5b1aed4b42da2d2/maintainability)](https://codeclimate.com/github/Orange-OpenSource/python-onapsdk/maintainability)

## Custom settings

Is it possible to use custom settings to overwrite custom values or add new one to `onapsdk.configuration.settings` module. Pass the path to your settings module as an environment variable `ONAP_PYTHON_SDK_SETTINGS`. If your file structure looks:
```
module
|
|-- my_settings.py
|
|-- my_awesome_script.py
```
you can just call
```
$ ONAP_PYTHON_SDK_SETTINGS=my_settings my_awesome_script.py
```
and then all uppercase attributes from `my_settings.py` will be available in `onapsdk.configuration.settings` module.

[ ~ Dependencies scanned by PyUp.io ~ ]