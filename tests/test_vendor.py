#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test vendor module."""
from unittest import mock

import pytest
from onapsdk.exceptions import RequestError

from onapsdk.sdc.vendor import Vendor
import onapsdk.constants as const
from onapsdk.sdc.sdc_element import SdcElement

@mock.patch.object(Vendor, 'send_message_json')
def test_get_all_no_vendors(mock_send):
    """Returns empty array if no vendors."""
    mock_send.return_value = {}
    assert Vendor.get_all() == []
    mock_send.assert_called_once_with("GET", 'get Vendors', 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models')

@mock.patch.object(Vendor, 'send_message_json')
def test_get_all_some_vendors(mock_send):
    """Returns a list of vendors."""
    mock_send.return_value = {'results':[
        {'name': 'one', 'id': '1234'},
        {'name': 'two', 'id': '1235'}]}
    assert len(Vendor.get_all()) == 2
    vendor_1 = Vendor.get_all()[0]
    assert vendor_1.name == "one"
    assert vendor_1.identifier == "1234"
    assert vendor_1.created() == True
    vendor_2 = Vendor.get_all()[1]
    assert vendor_2.name == "two"
    assert vendor_2.identifier == "1235"
    assert vendor_2.created()
    mock_send.assert_called_with("GET", 'get Vendors', 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models')

@mock.patch.object(Vendor, 'exists')
def test_init_no_name(mock_exists):
    """Check init with no names."""
    mock_exists.return_value = False
    vendor = Vendor()
    assert isinstance(vendor, SdcElement)
    assert vendor._identifier == None
    assert vendor._version == None
    assert vendor.name == "Generic-Vendor"
    assert vendor.created() == False
    assert vendor.headers["USER_ID"] == "cs0008"
    assert isinstance(vendor._base_url(), str)
    assert "sdc1/feProxy/onboarding-api/v1.0" in vendor._base_url()

def test_init_with_name():
    """Check init with no names."""
    vendor = Vendor(name="YOLO")
    assert vendor._identifier == None
    assert vendor._version == None
    assert vendor.name == "YOLO"
    assert vendor.headers["USER_ID"] == "cs0008"
    assert isinstance(vendor._base_url(), str)
    assert "sdc1/feProxy/onboarding-api/v1.0" in vendor._base_url()

def test_equality_really_equals():
    """Check two Vendors are equals if name is the same."""
    vendor_1 = Vendor(name="equal")
    vendor_1.identifier  = "1234"
    vendor_2 = Vendor(name="equal")
    vendor_2.identifier  = "1235"
    assert vendor_1 == vendor_2

def test_equality_not_equals():
    """Check two Vendors are not equals if name is not the same."""
    vendor_1 = Vendor(name="equal")
    vendor_1.identifier  = "1234"
    vendor_2 = Vendor(name="not_equal")
    vendor_2.identifier  = "1234"
    assert vendor_1 != vendor_2

def test_equality_not_equals_not_same_object():
    """Check a Vendor and something different are not equals."""
    vendor_1 = Vendor(name="equal")
    vendor_1.identifier  = "1234"
    vendor_2 = "equal"
    assert vendor_1 != vendor_2

@mock.patch.object(Vendor, 'get_all')
def test_exists_not_exists(mock_get_all):
    """Return False if vendor doesn't exist in SDC."""
    vendor_1 = Vendor(name="one")
    vendor_1.identifier = "1234"
    mock_get_all.return_value = [vendor_1]
    vendor = Vendor(name="two")
    assert not vendor.exists()

@mock.patch.object(Vendor, 'get_all')
def test_exists_exists(mock_get_all):
    """Return True if vendor exists in SDC."""
    vendor_1 = Vendor(name="one")
    vendor_1.identifier = "1234"
    vendor_1.version = "1.1"
    mock_get_all.return_value = [vendor_1]
    vendor = Vendor(name="one")
    assert vendor.exists()

@mock.patch.object(Vendor, 'get_all')
@mock.patch.object(Vendor, 'send_message_json')
def test_load_created(mock_send, mock_get_all):
    mock_send.return_value = {'results':
        [{'status': 'state_one', 'id': "5678"}], "listCount": 1}
    vendor = Vendor(name="one")
    vendor.identifier = "1234"
    vendor.load()
    mock_get_all.assert_not_called()
    mock_send.assert_called_once_with('GET', 'get item', 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/onboarding-api/v1.0/items/1234/versions')
    assert vendor.status == "state_one"
    assert vendor.version == "5678"

@mock.patch.object(Vendor, 'get_all')
@mock.patch.object(Vendor, 'send_message_json')
def test_load_not_created(mock_send, mock_get_all):
    mock_send.return_value = {'results':
        [{'status': 'state_one', 'id': "5678"}], "listCount": 1}
    vendor = Vendor(name="one")
    vendor.load()
    mock_get_all.return_value = []
    mock_send.assert_not_called()
    assert vendor._status == None
    assert vendor.version == None
    assert vendor._identifier == None

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'send_message_json')
def test_create_already_exists(mock_send, mock_exists):
    """Do nothing if already created in SDC."""
    vendor = Vendor()
    mock_exists.return_value = True
    vendor.create()
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'send_message_json')
def test_create_issue_in_creation(mock_send, mock_exists):
    """Do nothing if not created but issue during creation."""
    vendor = Vendor()
    expected_data = '{\n  "iconRef": "icon",\n  "vendorName": "Generic-Vendor",\n  "description": "vendor"\n}'
    mock_exists.return_value = False
    mock_send.side_effect = RequestError
    with pytest.raises(RequestError) as exc:
        vendor.create()
    mock_send.assert_called_once_with("POST", "create Vendor", mock.ANY, data=expected_data)
    assert vendor.created() == False

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'send_message_json')
def test_create_OK(mock_send, mock_exists):
    """Create and update object."""
    vendor = Vendor()
    expected_data = '{\n  "iconRef": "icon",\n  "vendorName": "Generic-Vendor",\n  "description": "vendor"\n}'
    mock_exists.return_value = False
    mock_send.return_value = {
        'itemId': "1234",
        'version': {'id': "5678", 'status': 'state_created'}}
    vendor.create()
    mock_send.assert_called_once_with("POST", "create Vendor", mock.ANY, data=expected_data)
    assert vendor.status == const.DRAFT
    assert vendor.identifier == "1234"
    assert vendor.version == "5678"

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'load')
@mock.patch.object(Vendor, 'send_message')
def test_submit_already_certified(mock_send, mock_load, mock_exists):
    """Do nothing if already certified."""
    mock_exists.return_value = True
    vendor = Vendor()
    vendor._status = const.CERTIFIED
    vendor.submit()
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'load')
@mock.patch.object(Vendor, 'send_message')
def test_submit_not_created(mock_send, mock_load, mock_exists):
    """Do nothing if not created."""
    mock_exists.return_value = False
    vendor = Vendor()
    vendor.submit()
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'load')
@mock.patch.object(Vendor, 'send_message')
def test_submit_certified_NOK(mock_send, mock_load, mock_exists):
    """Don't update status if submission NOK."""
    mock_exists.return_value = True
    vendor = Vendor()
    vendor._identifier = "12345"
    mock_send.side_effect = RequestError
    expected_data = '{\n\n  "action": "Submit"\n}'
    vendor._status = "Draft"
    vendor._version = "1234"
    with pytest.raises(RequestError) as err:
        vendor.submit()
    assert err.type == RequestError
    mock_send.assert_called_once_with("PUT", "Submit Vendor", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models/12345/versions/1234/actions', data=expected_data)
    assert vendor._status != const.CERTIFIED

@mock.patch.object(Vendor, 'exists')
@mock.patch.object(Vendor, 'load')
@mock.patch.object(Vendor, 'send_message')
def test_submit_certified_OK(mock_send, mock_load, mock_exists):
    """Set status to CERTIFIED if submission OK."""
    mock_exists.return_value = True
    vendor = Vendor()
    vendor._status = "Draft"
    vendor._version = "1234"
    vendor.identifier = "12345"
    mock_send.return_value = mock.Mock()
    expected_data = '{\n\n  "action": "Submit"\n}'
    vendor.submit()
    mock_send.assert_called_once_with("PUT", "Submit Vendor", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models/12345/versions/1234/actions', data=expected_data)
    assert vendor.status == const.CERTIFIED

@mock.patch.object(Vendor, 'created')
@mock.patch.object(Vendor, 'load')
def test_version_no_load_no_created(mock_load, mock_created):
    mock_created.return_value = False
    vendor = Vendor()
    assert vendor.version == None
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'created')
@mock.patch.object(Vendor, 'load')
def test_version_no_load_created(mock_load, mock_created):
    mock_created.return_value = True
    vendor = Vendor()
    vendor._version = "64"
    assert vendor.version == "64"
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'load')
def test_version_with_load(mock_load):
    vendor = Vendor()
    vendor.identifier = "12345"
    assert vendor.version == None
    mock_load.assert_called_once()

@mock.patch.object(Vendor, 'created')
@mock.patch.object(Vendor, 'load')
def test_status_no_load_no_created(mock_load, mock_created):
    mock_created.return_value = False
    vendor = Vendor()
    assert vendor.status == None
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'created')
@mock.patch.object(Vendor, 'load')
def test_status_no_load_created(mock_load, mock_created):
    mock_created.return_value = True
    vendor = Vendor()
    vendor.identifier = "12345"
    vendor._status = "Draft"
    assert vendor.status == "Draft"
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'load')
def test_status_with_load(mock_load):
    vendor = Vendor()
    vendor.identifier = "12345"
    assert vendor.status == None
    mock_load.assert_called_once()

@mock.patch.object(Vendor, 'submit')
@mock.patch.object(Vendor, 'create')
def test_onboard_new_vendor(mock_create, mock_submit):
    getter_mock = mock.Mock(wraps=Vendor.status.fget)
    mock_status = Vendor.status.getter(getter_mock)
    with mock.patch.object(Vendor, 'status', mock_status):
        getter_mock.side_effect = [None, const.CERTIFIED, const.CERTIFIED]
        vendor = Vendor()
        vendor.onboard()
        mock_create.assert_called_once()
        mock_submit.assert_not_called()

@mock.patch.object(Vendor, 'submit')
@mock.patch.object(Vendor, 'create')
def test_onboard_created_vendor(mock_create, mock_submit):
    getter_mock = mock.Mock(wraps=Vendor.status.fget)
    mock_status = Vendor.status.getter(getter_mock)
    with mock.patch.object(Vendor, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, None]
        vendor = Vendor()
        vendor.onboard()
        mock_submit.assert_called_once()
        mock_create.assert_not_called()

@mock.patch.object(Vendor, 'submit')
@mock.patch.object(Vendor, 'create')
def test_onboard_whole_vendor(mock_create, mock_submit):
    getter_mock = mock.Mock(wraps=Vendor.status.fget)
    mock_status = Vendor.status.getter(getter_mock)
    with mock.patch.object(Vendor, 'status', mock_status):
        getter_mock.side_effect = [None, const.DRAFT, const.DRAFT, None]
        vendor = Vendor()
        vendor.onboard()
        mock_submit.assert_called_once()
        mock_create.assert_called_once()
