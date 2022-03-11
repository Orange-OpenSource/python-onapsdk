import os
import sys
from pathlib import PurePath

import pytest

from onapsdk.configuration import settings, SETTINGS_ENV
from onapsdk.configuration.loader import SettingsLoader
from onapsdk.exceptions import ModuleError


def test_global_settings():
    """Test global settings."""
    assert len(settings._settings) == 42
    assert settings.AAI_URL == "https://aai.api.sparky.simpledemo.onap.org:30233"
    assert settings.CDS_URL == "http://portal.api.simpledemo.onap.org:30449"
    assert settings.SDNC_URL == "https://sdnc.api.simpledemo.onap.org:30267"
    assert settings.SO_URL == "http://so.api.simpledemo.onap.org:30277"
    assert settings.MSB_URL == "https://msb.api.simpledemo.onap.org:30283"
    assert settings.SDC_FE_URL == "https://sdc.api.fe.simpledemo.onap.org:30207"
    assert settings.SDC_BE_URL == "https://sdc.api.be.simpledemo.onap.org:30204"
    assert settings.VID_URL == "https://vid.api.simpledemo.onap.org:30200"
    assert settings.CLAMP_URL == "https://clamp.api.simpledemo.onap.org:30258"
    assert settings.VES_URL == "http://ves.api.simpledemo.onap.org:30417"
    assert settings.DMAAP_URL   == "http://dmaap.api.simpledemo.onap.org:3904"
    assert settings.NBI_URL == "https://nbi.api.simpledemo.onap.org:30274"
    assert settings.DCAEMOD_URL == ""
    assert settings.HOLMES_URL == "https://aai.api.sparky.simpledemo.onap.org:30293"
    assert settings.POLICY_URL == ""
    assert settings.AAI_GUI_URL == "https://aai.api.sparky.simpledemo.onap.org:30220"
    assert settings.AAI_GUI_SERVICE == "https://aai.api.sparky.simpledemo.onap.org:30220/services/aai/webapp/index.html#/browse"
    assert settings.CDS_GUI_SERVICE == "http://portal.api.simpledemo.onap.org:30449/"
    assert settings.SO_MONITOR_GUI_SERVICE == "http://so.api.simpledemo.onap.org:30277/"
    assert settings.SDC_GUI_SERVICE == "https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/portal"
    assert settings.SDNC_DG_GUI_SERVICE == "https://sdnc.api.simpledemo.onap.org:30267/nifi/"
    assert settings.SDNC_ODL_GUI_SERVICE == "https://sdnc.api.simpledemo.onap.org:30267/odlux/index.html"
    assert settings.DCAEMOD_GUI_SERVICE == "/"
    assert settings.HOLMES_GUI_SERVICE == "https://aai.api.sparky.simpledemo.onap.org:30293/iui/holmes/default.html"
    assert settings.POLICY_GUI_SERVICE == "/onap/login.html"
    assert settings.POLICY_CLAMP_GUI_SERVICE == "https://clamp.api.simpledemo.onap.org:30258/"
    assert settings.PROJECT == "Onapsdk_project"
    assert settings.LOB == "Onapsdk_lob"
    assert settings.PLATFORM == "Onapsdk_platform"
    assert hasattr(settings, "AAI_AUTH")
    assert hasattr(settings, "CDS_AUTH")
    assert hasattr(settings, "SDC_AUTH")
    assert hasattr(settings, "SDNC_AUTH")
    assert hasattr(settings, "CLAMP_AUTH")
    assert hasattr(settings, "SO_AUTH")
    assert hasattr(settings, "SO_CAT_DB_AUTH")


def test_settings_load_custom():
    """Test if custom settings is loaded correctly."""
    sys.path.append(str(PurePath(__file__).parent))
    os.environ[SETTINGS_ENV] = "data.tests_settings"
    custom_settings = SettingsLoader()
    assert custom_settings.AAI_URL == "http://tests.settings.py:1234"
    assert custom_settings.TEST_VALUE == "test"


def test_invalid_custom_settings():
    """Test if loading invalid custom settings raises ModuleError."""
    os.environ[SETTINGS_ENV] = "non.existings.package"
    with pytest.raises(ModuleError):
        SettingsLoader()
