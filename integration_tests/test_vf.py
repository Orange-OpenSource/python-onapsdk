#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Vendor module."""
import os

import pytest

import requests

from onapsdk.vendor import Vendor
from onapsdk.vsp import Vsp
from onapsdk.vf import Vf
import onapsdk.constants as const


@pytest.mark.integration
def test_vsp_unknown():
    """Integration tests for Vf."""
    response = requests.post("{}/reset".format(Vendor.base_front_url))
    response.raise_for_status()
    Vf.base_back_url = Vf.base_front_url
    vendor = Vendor(name="test")
    vendor.create()
    vendor.submit()
    vsp = Vsp(name="test")
    vsp.vendor = vendor
    vsp.create()
    vsp.upload_files(open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.validate()
    vsp.commit()
    vsp.submit()
    vsp.create_csar()
    vf = Vf(name='test')
    vf.vsp = vsp
    vf.create()
    assert vf.identifier is not None
    assert vf.status == const.DRAFT
    assert vf.version == "0.1"
    vf.submit()
    assert vsp.status == const.CERTIFIED
    assert vf.version == "1.0"
    vf.load()
    assert vsp.status == const.CERTIFIED
    assert vf.version == "1.0"
