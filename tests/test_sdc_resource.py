#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcResource module."""
import mock
import pytest

from onapsdk.onap_service import OnapService
from onapsdk.sdc_resource import SdcResource
from onapsdk.vf import Vf
from onapsdk.vsp import Vsp
from onapsdk.constants import CERTIFIED, DRAFT

def test_init():
    """Test the initialization."""
    element = SdcResource()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert SdcResource.server == "SDC"
    assert SdcResource.base_front_url == "http://sdc.api.fe.simpledemo.onap.org:30206"
    assert SdcResource.base_back_url == "http://sdc.api.be.simpledemo.onap.org:30205"
    assert SdcResource.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

@mock.patch.object(Vf, 'send_message_json')
def test__get_item_details_not_created(mock_send):
    vf = Vf()
    assert vf._get_item_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vsp, 'send_message_json')
def test__get_item_details_created(mock_send):
    vsp = Vsp()
    vsp.identifier = "1234"
    mock_send.return_value = {'return': 'value'}
    assert vsp._get_item_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item', "{}/items/1234/versions".format(vsp._base_url()))

@mock.patch.object(Vsp, 'send_message_json')
def test__get_items_version_details_not_created(mock_send):
    vsp = Vsp()
    assert vsp._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details_no_version(mock_send, mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details(mock_send):
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "4567"
    mock_send.return_value = {'return': 'value'}
    assert vf._get_item_version_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item version', "{}/items/1234/versions/4567".format(vf._base_url()))

@mock.patch.object(Vf, 'load')
def test__unique_uuid_no_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    vf._unique_uuid = "4567"
    assert vf.unique_uuid == "4567"
    mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
def test__unique_uuid_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf.unique_uuid == None
    mock_load.assert_called_once()

def test__unique_uuid_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.unique_uuid = "4567"
    assert vf._unique_uuid == "4567"

def test__status_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.status = "4567"
    assert vf._status == "4567"

def test__parse_sdc_status_certified():
    assert SdcResource._parse_sdc_status("CERTIFIED") ==  CERTIFIED

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status("NOT_CERTIFIED_CHECKOUT") ==  DRAFT

def test__parse_sdc_status_unknown():
    assert SdcResource._parse_sdc_status("UNKNOWN") is None
