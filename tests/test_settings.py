import os
import sys
from pathlib import PurePath

import pytest

from onapsdk.configuration import settings, SETTINGS_ENV
from onapsdk.configuration.loader import SettingsLoader


def test_global_settings():
    """Test global settings."""
    assert len(settings._settings) == 13
    assert settings.AAI_URL == "https://aai.api.sparky.simpledemo.onap.org:30233"
    assert settings.CDS_URL == "http://portal.api.simpledemo.onap.org:30449"
    assert settings.SDNC_URL == "https://sdnc.api.simpledemo.onap.org:30267"
    assert settings.SO_URL == "http://so.api.simpledemo.onap.org:30277"
    assert settings.MSB_URL == "https://msb.api.simpledemo.onap.org:30283"
    assert settings.SDC_FE_URL == "https://sdc.api.fe.simpledemo.onap.org:30207"
    assert settings.SDC_BE_URL == "https://sdc.api.be.simpledemo.onap.org:30204"
    assert settings.VID_URL == "https://vid.api.simpledemo.onap.org:30200"
    assert settings.CLAMP_URL == "https://clamp.api.simpledemo.onap.org:30258"
    assert settings.VES_URL == "https://ves.api.simpledemo.onap.org:30417"


def test_settings_load_custom():
    """Test if custom settings is loaded correctly."""
    sys.path.append(str(PurePath(__file__).parent))
    os.environ[SETTINGS_ENV] = "data.tests_settings"
    custom_settings = SettingsLoader()
    assert custom_settings.AAI_URL == "http://tests.settings.py:1234"
    assert custom_settings.TEST_VALUE == "test"


def test_invalid_custom_settings():
    """Test if loading invalid custom settings raises ValueError."""
    os.environ[SETTINGS_ENV] = "non.existings.package"
    with pytest.raises(ValueError):
        SettingsLoader()
