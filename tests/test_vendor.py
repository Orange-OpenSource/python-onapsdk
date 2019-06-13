#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test vendor module."""
import mock
import pytest

from onapsdk.vendor import Vendor
import onapsdk.constants as const
from onapsdk.sdc_element import SdcElement

@mock.patch.object(Vendor, 'send_message_json')
def test_get_all_no_vendors(mock_send):
    """Returns empty array if no vendors."""
    mock_send.return_value = {}
    assert Vendor.get_all() == []
    mock_send.assert_called_once_with("GET", 'get vendors', mock.ANY)

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
    assert vendor_1.created
    vendor_2 = Vendor.get_all()[1]
    assert vendor_2.name == "two"
    assert vendor_2.identifier == "1235"
    assert vendor_2.created
    mock_send.assert_called_with("GET", 'get vendors', mock.ANY)

def test_init_no_name():
    """Check init with no names."""
    vendor = Vendor()
    assert isinstance(vendor, SdcElement)
    assert vendor.identifier == None
    assert vendor.version == None
    assert vendor.name == "Generic-Vendor"
    assert vendor.created == False
    assert vendor.header["USER_ID"] == "cs0008"
    assert isinstance(vendor._base_url(), str)
    assert "sdc1/feProxy/onboarding-api/v1.0" in vendor._base_url()

def test_init_with_name():
    """Check init with no names."""
    vendor = Vendor(name="YOLO")
    assert vendor.identifier == None
    assert vendor.version == None
    assert vendor.name == "YOLO"
    assert vendor.created == False
    assert vendor.header["USER_ID"] == "cs0008"
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
    vendor_1.created = True
    mock_get_all.return_value = [vendor_1]
    vendor = Vendor(name="two")
    assert not vendor.exists()

@mock.patch.object(Vendor, 'get_all')

def test_exists_exists(mock_get_all):
    """Return True if vendor exists in SDC."""
    vendor_1 = Vendor(name="one")
    vendor_1.identifier = "1234"
    vendor_1.created = True
    mock_get_all.return_value = [vendor_1]
    vendor = Vendor(name="one")
    assert vendor.exists()

@mock.patch.object(Vendor, 'send_message_json')
def test_load_created(mock_send):
    mock_send.return_value = {'results':
        [{'status': 'state_one', 'id': "5678"}]}
    vendor = Vendor(name="one")
    vendor.created = True
    vendor.identifier = "1234"
    vendor.load()
    mock_send.assert_called_once_with('GET', 'get vendors', mock.ANY)
    assert vendor.status == "state_one"
    assert vendor.version == "5678"

@mock.patch.object(Vendor, 'send_message_json')
def test_load_not_created(mock_send):
    mock_send.return_value = {'results':
        [{'status': 'state_one', 'id': "5678"}]}
    vendor = Vendor(name="one")
    vendor.created = False
    vendor.load()
    mock_send.assert_not_called()
    assert vendor.status == None
    assert vendor.version == None

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
    mock_send.return_value = {}
    vendor.create()
    mock_send.assert_called_once_with("POST", "create vendor", mock.ANY, data=expected_data)
    assert vendor.created == False

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
    mock_send.assert_called_once_with("POST", "create vendor", mock.ANY, data=expected_data)
    assert vendor.created == True
    assert vendor.status == "state_created"
    assert vendor.identifier == "1234"
    assert vendor.version == "5678"

@mock.patch.object(Vendor, 'send_message')
def test_submit_already_certified(mock_send):
    """Do nothing if already certified."""
    vendor = Vendor()
    vendor._status = const.CERTIFIED
    vendor.submit()
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'send_message')
def test_submit_not_created(mock_send):
    """Do nothing if not created."""
    vendor = Vendor()
    vendor.created = False
    vendor.submit()
    mock_send.assert_not_called()

@mock.patch.object(Vendor, 'send_message')
def test_submit_certified_NOK(mock_send):
    """Don't update status if submission NOK."""
    vendor = Vendor()
    vendor.created = True
    mock_send.return_value = None
    expected_data = '{\n  "action": "Submit"\n}'
    vendor._status = "Draft"
    vendor._version = "1234"
    vendor.submit()
    mock_send.assert_called_once_with("PUT", "submit vendor", mock.ANY, data=expected_data)
    assert vendor.status != const.CERTIFIED

@mock.patch.object(Vendor, 'send_message')
def test_submit_certified_OK(mock_send):
    """Set status to CERTIFIED if submission OK."""
    vendor = Vendor()
    vendor.created = True
    vendor._status = "Draft"
    vendor._version = "1234"
    mock_send.return_value = mock.Mock()
    expected_data = '{\n  "action": "Submit"\n}'
    vendor.submit()
    mock_send.assert_called_once_with("PUT", "submit vendor", mock.ANY, data=expected_data)
    assert vendor.status == const.CERTIFIED

@mock.patch.object(Vendor, 'load')
def test_version_no_load_no_created(mock_load):
    vendor = Vendor()
    vendor.created = False
    assert vendor.version == None
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'load')
def test_version_no_load_created(mock_load):
    vendor = Vendor()
    vendor.created = True
    vendor._version = "64"
    assert vendor.version == "64"
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'load')
def test_version_with_load(mock_load):
    vendor = Vendor()
    vendor.created = True
    assert vendor.version == None
    mock_load.assert_called_once()

@mock.patch.object(Vendor, 'load')
def test_status_no_load_no_created(mock_load):
    vendor = Vendor()
    vendor.created = False
    assert vendor.status == None
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'load')
def test_status_no_load_created(mock_load):
    vendor = Vendor()
    vendor.created = True
    vendor._status = "Draft"
    assert vendor.status == "Draft"
    mock_load.assert_not_called()

@mock.patch.object(Vendor, 'load')
def test_status_with_load(mock_load):
    vendor = Vendor()
    vendor.created = True
    assert vendor.status == None
    mock_load.assert_called_once()
