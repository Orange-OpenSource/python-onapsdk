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
from onapsdk.sdc.service import Service
import onapsdk.constants as const


@pytest.mark.integration
def test_service_unknown():
    """Integration tests for Service."""
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test', vsp=vsp)
    vf.onboard()
    svc = Service(name='test')
    assert svc.identifier is None
    assert svc.status is None
    svc.create()
    assert svc.identifier is not None
    assert svc.status == const.DRAFT
    svc.add_resource(vf)
    svc.checkin()
    assert svc.status == const.CHECKED_IN
    svc.certify()
    assert svc.status == const.CERTIFIED
    svc.distribute()
    assert svc.status == const.DISTRIBUTED
    assert svc.distributed

@pytest.mark.integration
def test_service_onboard_unknown():
    """Integration tests for Service."""
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test', vsp=vsp)
    vf.onboard()
    svc = Service(name='test', resources=[vf])
    svc.onboard()
    assert svc.distributed

@pytest.mark.integration
def test_service_upload_tca_artifact():
    """Integration tests for Service."""
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test', vsp=vsp)
    vf.onboard()
    svc = Service(name='test')
    svc.create()
    svc.add_resource(vf)
    assert svc.status == const.DRAFT
    payload_file = open("{}/tca_clampnode.yaml".format(os.path.dirname(os.path.abspath(__file__))), 'rb')
    data = payload_file.read()
    svc.add_artifact_to_vf(vnf_name="test", 
                               artifact_type="DCAE_INVENTORY_BLUEPRINT",
                               artifact_name="tca_clampnode.yaml",
                               artifact=data)
    payload_file.close()

@pytest.mark.integration
def test_service_properties():
    """Integration test to check properties assignment for Service."""
    response = requests.post("{}/reset".format(SDC.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.onboard()
    vsp = Vsp(name="test", package=open("{}/ubuntu16.zip".format(
        os.path.dirname(os.path.abspath(__file__))), 'rb'))
    vsp.vendor = vendor
    vsp.onboard()
    vf = Vf(name='test', vsp=vsp)
    vf.onboard()
    properties = [
        Property(name="test1", property_type="string", value="123"),
        Property(name="test2", property_type="integer")
    ]
    svc = Service(name='test', resources=[vf], properties=properties, inputs=[properties[1]])
    svc.onboard()
    service_properties = list(svc.properties)
    service_inputs = list(svc.inputs)
    assert len(service_properties) == 2
    assert len(service_inputs) == 1
