#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Vendor module."""
import os

import pytest

import requests

from onapsdk.sdc import SDC
from onapsdk.sdc.properties import Property
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp
from onapsdk.sdc.vf import Vf
import onapsdk.constants as const


@pytest.mark.integration
def test_vf_unknown():
    """Integration tests for Vf."""
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

@pytest.mark.integration
def test_vf_properties():
    """Integration test to check properties assignment for Vf."""
    response = requests.post("{}/reset".format(Vendor.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    prop = Property(name="test1", property_type="string", value="123")
    vf = Vf(name="test", vsp=vsp, properties=[
        prop,
        Property(name="test2", property_type="integer")],
        inputs=[prop])
    vf.onboard()
    vf_properties = list(vf.properties)
    vf_inputs = list(vf.inputs)
    assert len(vf_properties) == 2
    assert len(vf_inputs) == 1
