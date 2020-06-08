#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Vendor module."""
import os

import pytest

import requests

from onapsdk.sdc import SDC
from onapsdk.vendor import Vendor
from onapsdk.vsp import Vsp
from onapsdk.vf import Vf
import onapsdk.constants as const

from .urls import SDC_MOCK_URL


@pytest.mark.integration
def test_vf_unknown():
    """Integration tests for Vf."""
    SDC.base_front_url = SDC_MOCK_URL
    SDC.base_back_url = SDC_MOCK_URL
    response = requests.post("{}/reset".format(Vendor.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
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

@pytest.mark.integration
def test_vf_onboard_unknown():
    """Integration tests for Vf."""
    SDC.base_front_url = SDC_MOCK_URL
    SDC.base_back_url = SDC_MOCK_URL
    response = requests.post("{}/reset".format(Vendor.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test')
    vf.vsp = vsp
    vf.onboard()
    assert vsp.status == const.CERTIFIED
    assert vf.version == "1.0"
