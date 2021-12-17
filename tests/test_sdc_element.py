#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcElement module."""
from unittest import mock

from onapsdk.onap_service import OnapService
from onapsdk.sdc.sdc_element import SdcElement
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp
from onapsdk.sdc import SDC
from onapsdk.utils.gui import GuiList

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
    mock_send.return_value = {'results': [{"creationTime": "2"}, {"creationTime": "3"}], "listCount": 2}
    assert vsp._get_item_details() == {"creationTime": "3"}
    mock_send.assert_called_once_with('GET', 'get item', "{}/items/1234/versions".format(vsp._base_url()))

@mock.patch.object(Vsp, 'created')
@mock.patch.object(Vsp, 'send_message_json')
def test__get_items_version_details_not_created(mock_send, mock_created):
    vsp = Vsp()
    mock_created.return_value = False
    assert vsp._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vsp, 'load')
@mock.patch.object(Vsp, 'send_message_json')
def test__get_items_version_details_no_version(mock_send, mock_load):
    vsp = Vsp()
    vsp.identifier = "1234"
    assert vsp._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vsp, 'send_message_json')
def test__get_items_version_details(mock_send):
    vsp = Vsp()
    vsp.identifier = "1234"
    vsp._version = "4567"
    mock_send.return_value = {'return': 'value'}
    assert vsp._get_item_version_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item version', "{}/items/1234/versions/4567".format(vsp._base_url()))

@mock.patch.object(SDC, "send_message")
def test_get_guis(send_message_mock):
    send_message_mock.return_value.status_code = 200
    send_message_mock.return_value.url = "https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/portal"
    gui_results = SDC.get_guis()
    assert type(gui_results) == GuiList
    assert gui_results.guilist[0].url == send_message_mock.return_value.url
    assert gui_results.guilist[0].status == send_message_mock.return_value.status_code

@mock.patch.object(SDC, "get_all")
@mock.patch.object(Vsp, "created")
def test_exists_versions(mock_vsp_created, mock_get_all):
    mock_vsp_created.return_value = True
    sdc_el1 = Vsp(name="test1")
    sdc_el1._version = "1.0"
    sdc_el1._identifier = "123"
    sdc_el2 = Vsp(name="test2")
    sdc_el2._version = "2.0"
    sdc_el2._identifier = "123"
    mock_get_all.return_value = [sdc_el1, sdc_el2]
    assert sdc_el1.exists()

    sdc_el1 = Vsp(name="test1")
    sdc_el1._version = "anything"
    sdc_el1._identifier = "123"
    sdc_el2 = Vsp(name="test2")
    sdc_el2._version = "what_is_not_a_float"
    sdc_el2._identifier = "123"
    mock_get_all.return_value = [sdc_el1, sdc_el2]
    assert sdc_el1.exists()
