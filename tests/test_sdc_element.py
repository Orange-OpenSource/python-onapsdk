#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcElement module."""
from unittest import mock

import pytest

from onapsdk.onap_service import OnapService
from onapsdk.sdc.sdc_element import SdcElement
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp

def test_init():
    """Test the initialization."""
    element = Vendor()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert SdcElement.server == "SDC"
    assert SdcElement.base_front_url == "https://sdc.api.fe.simpledemo.onap.org:30207"
    assert SdcElement.base_back_url == "https://sdc.api.be.simpledemo.onap.org:30204"
    assert SdcElement.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

@mock.patch.object(Vendor, 'created')
@mock.patch.object(Vendor, 'send_message_json')
def test__get_item_details_not_created(mock_send, mock_created):
    vendor = Vendor()
    mock_created.return_value = False
    assert vendor._get_item_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vsp, 'send_message_json')
def test__get_item_details_created(mock_send):
    vsp = Vsp()
    vsp.identifier = "1234"
    mock_send.return_value = {'return': 'value'}
    assert vsp._get_item_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item', "{}/items/1234/versions".format(vsp._base_url()))

@mock.patch.object(Vsp, 'created')
@mock.patch.object(Vsp, 'send_message_json')
def test__get_items_version_details_not_created(mock_send, mock_created):
    vsp = Vsp()
    mock_created.return_value = False
    assert vsp._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'load')
@mock.patch.object(Vendor, 'send_message_json')
def test__get_items_version_details_no_version(mock_send, mock_load):
    vendor = Vendor()
    vendor.identifier = "1234"
    assert vendor._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'send_message_json')
def test__get_items_version_details(mock_send):
    vendor = Vendor()
    vendor.identifier = "1234"
    vendor._version = "4567"
    mock_send.return_value = {'return': 'value'}
    assert vendor._get_item_version_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item version', "{}/items/1234/versions/4567".format(vendor._base_url()))
