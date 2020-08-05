#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test vf module."""

from unittest import mock
from unittest.mock import MagicMock

import pytest

import onapsdk.constants as const
from onapsdk.sdc.properties import Property
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vsp import Vsp
from onapsdk.sdc.vsp import Vendor


@mock.patch.object(Vf, 'send_message_json')
def test_get_all_no_vf(mock_send):
    """Returns empty array if no vfs."""
    mock_send.return_value = {}
    assert Vf.get_all() == []
    mock_send.assert_called_once_with("GET", 'get Vfs', 'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/resources?resourceType=VF')


@mock.patch.object(Vf, 'send_message_json')
def test_get_all_some_vfs(mock_send):
    """Returns a list of vf."""
    mock_send.return_value = [
        {'resourceType': 'VF', 'name': 'one', 'uuid': '1234', 'invariantUUID': '5678', 'version': '1.0', 'lifecycleState': 'CERTIFIED'},
        {'resourceType': 'VF', 'name': 'two', 'uuid': '1235', 'invariantUUID': '5679', 'version': '1.0', 'lifecycleState': 'NOT_CERTIFIED_CHECKOUT'}]
    all_vfs = Vf.get_all()
    assert len(all_vfs) == 2
    vf_1 = all_vfs[0]
    assert vf_1.name == "one"
    assert vf_1.identifier == "1234"
    assert vf_1.unique_uuid == "5678"
    assert vf_1.version == "1.0"
    assert vf_1.status == const.CERTIFIED
    assert vf_1.created()
    vf_2 = all_vfs[1]
    assert vf_2.name == "two"
    assert vf_2.identifier == "1235"
    assert vf_2.unique_uuid == "5679"
    assert vf_2.status == const.DRAFT
    assert vf_2.version == "1.0"
    assert vf_2.created()
    mock_send.assert_called_once_with("GET", 'get Vfs', 'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/resources?resourceType=VF')


def test_init_no_name():
    """Check init with no names."""
    vf = Vf()
    assert isinstance(vf, SdcResource)
    assert vf._identifier is None
    assert vf._version is None
    assert vf.name == "ONAP-test-VF"
    assert vf.headers["USER_ID"] == "cs0008"
    assert vf.vsp is None
    assert isinstance(vf._base_url(), str)

@mock.patch.object(Vf, 'exists')
def test_init_with_name(mock_exists):
    """Check init with no names."""
    mock_exists.return_value = False
    vf = Vf(name="YOLO")
    assert vf._identifier == None
    assert vf._version == None
    assert vf.name == "YOLO"
    assert vf.created() == False
    assert vf.headers["USER_ID"] == "cs0008"
    assert vf.vsp == None
    assert isinstance(vf._base_url(), str)


def test_equality_really_equals():
    """Check two vfs are equals if name is the same."""
    vf_1 = Vf(name="equal")
    vf_1.identifier = "1234"
    vf_2 = Vf(name="equal")
    vf_2.identifier = "1235"
    assert vf_1 == vf_2


def test_equality_not_equals():
    """Check two vfs are not equals if name is not the same."""
    vf_1 = Vf(name="equal")
    vf_1.identifier = "1234"
    vf_2 = Vf(name="not_equal")
    vf_2.identifier = "1234"
    assert vf_1 != vf_2


def test_equality_not_equals_not_same_object():
    """Check a vf and something different are not equals."""
    vf_1 = Vf(name="equal")
    vf_1.identifier = "1234"
    vf_2 = SdcResource()
    vf_2.name = "equal"
    assert vf_1 != vf_2


@mock.patch.object(Vf, 'get_all')
def test_exists_not_exists(mock_get_all):
    """Return False if vf doesn't exist in SDC."""
    vf_1 = Vf(name="one")
    vf_1.identifier = "1234"
    mock_get_all.return_value = [vf_1]
    vf = Vf(name="two")
    assert not vf.exists()


@mock.patch.object(Vf, 'get_all')
def test_exists_exists(mock_get_all):
    """Return True if vf exists in SDC."""
    vf_1 = Vf(name="one")
    vf_1.identifier = "1234"
    vf_1.unique_uuid = "5689"
    vf_1.unique_identifier = "71011"
    vf_1.status = const.DRAFT
    vf_1.version = "1.1"
    mock_get_all.return_value = [vf_1]
    vf = Vf(name="one")
    assert vf.exists()
    assert vf.identifier == "1234"
    assert vf.unique_uuid == "5689"
    assert vf.unique_identifier == "71011"
    assert vf.status == const.DRAFT
    assert vf.version == "1.1"


@mock.patch.object(Vf, 'exists')
def test_load_created(mock_exists):
    """Load is a wrapper around exists()."""
    vf = Vf(name="one")
    vf.load()
    mock_exists.assert_called_once()


@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
def test_create_no_vsp(mock_send, mock_exists):
    """Do nothing if no vsp."""
    vf = Vf()
    mock_exists.return_value = False
    vf.create()
    mock_send.assert_not_called()


@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
def test_create_already_exists(mock_send, mock_exists):
    """Do nothing if already created in SDC."""
    vf = Vf()
    vsp = Vsp()
    vsp._identifier = "1232"
    vf.vsp = vsp
    mock_exists.return_value = True
    vf.create()
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
def test_create_issue_in_creation(mock_send, mock_exists):
    """Do nothing if not created but issue during creation."""
    vf = Vf()
    vsp = Vsp()
    vendor = Vendor()
    vsp._identifier = "1232"
    vsp.create_csar = MagicMock(return_value=True)
    vsp.vendor = vendor
    vf.vsp = vsp
    expected_data = '{\n    "artifacts": {},\n    "attributes": [],\n    "capabilities": {},\n    "categories":[\n        {\n            "name": "Generic",\n            "normalizedName": "generic",\n            "uniqueId": "resourceNewCategory.generic",\n            "icons": null,\n            "subcategories":[\n                {\n                    "name": "Abstract",\n                    "normalizedName": "abstract",\n                    "uniqueId": "resourceNewCategory.generic.abstract",\n                    "icons":[\n                        "objectStorage",\n                        "compute"\n                    ],\n                    "groupings": null,\n                    "ownerId": null,\n                    "empty": false\n                }\n            ],\n            "ownerId": null,\n            "empty": false\n        }\n    ],\n    "componentInstances": [],\n    "componentInstancesAttributes": {},\n    "componentInstancesProperties": {},\n    "componentType": "RESOURCE",\n    "contactId": "cs0008",\n    "csarUUID": "None",\n    "csarVersion": "1.0",\n    "deploymentArtifacts": {},\n    "description": "VF",\n    "icon": "defaulticon",\n    "name": "ONAP-test-VF",\n    "properties": [],\n    "groups": [],\n    "requirements": {},\n    "resourceType": "VF",\n    "tags": ["ONAP-test-VF"],\n    "toscaArtifacts": {},\n    "vendorName": "Generic-Vendor",\n    "vendorRelease": "1.0"\n}'
    mock_exists.return_value = False
    mock_send.return_value = {}
    vf.create()
    mock_send.assert_called_once_with("POST", "create Vf", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources', data=expected_data)
    assert not vf.created()


@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
def test_create_OK(mock_send, mock_exists):
    """Create and update object."""
    vf = Vf()
    vsp = Vsp()
    vendor = Vendor()
    vsp._identifier = "1232"
    vf.vsp = vsp
    vsp.vendor = vendor
    vsp._csar_uuid = "1234"
    expected_data = '{\n    "artifacts": {},\n    "attributes": [],\n    "capabilities": {},\n    "categories":[\n        {\n            "name": "Generic",\n            "normalizedName": "generic",\n            "uniqueId": "resourceNewCategory.generic",\n            "icons": null,\n            "subcategories":[\n                {\n                    "name": "Abstract",\n                    "normalizedName": "abstract",\n                    "uniqueId": "resourceNewCategory.generic.abstract",\n                    "icons":[\n                        "objectStorage",\n                        "compute"\n                    ],\n                    "groupings": null,\n                    "ownerId": null,\n                    "empty": false\n                }\n            ],\n            "ownerId": null,\n            "empty": false\n        }\n    ],\n    "componentInstances": [],\n    "componentInstancesAttributes": {},\n    "componentInstancesProperties": {},\n    "componentType": "RESOURCE",\n    "contactId": "cs0008",\n    "csarUUID": "1234",\n    "csarVersion": "1.0",\n    "deploymentArtifacts": {},\n    "description": "VF",\n    "icon": "defaulticon",\n    "name": "ONAP-test-VF",\n    "properties": [],\n    "groups": [],\n    "requirements": {},\n    "resourceType": "VF",\n    "tags": ["ONAP-test-VF"],\n    "toscaArtifacts": {},\n    "vendorName": "Generic-Vendor",\n    "vendorRelease": "1.0"\n}'
    mock_exists.return_value = False
    mock_send.return_value = {'resourceType': 'VF', 'name': 'one', 'uuid': '1234', 'invariantUUID': '5678', 'version': '1.0', 'uniqueId': '91011', 'lifecycleState': 'NOT_CERTIFIED_CHECKOUT'}
    vf.create()
    mock_send.assert_called_once_with("POST", "create Vf", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources', data=expected_data)
    assert vf.created()
    assert vf._status == const.DRAFT
    assert vf.identifier == "1234"
    assert vf.unique_uuid == "5678"
    assert vf.version == "1.0"

@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'load')
def test_version_no_load_no_created(mock_load, mock_exists):
    """Test versions when not created."""
    mock_exists.return_value = False
    vf = Vf()
    assert vf.version is None
    mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
def test_version_no_load_created(mock_load):
    """Test versions when created."""
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "64"
    assert vf.version == "64"
    mock_load.assert_not_called()


@mock.patch.object(Vf, 'load')
def test_version_with_load(mock_load):
    """Test versions when not created but with identifier."""
    vf = Vf()
    vf.identifier = "1234"
    assert vf.version is None
    mock_load.assert_called_once()

@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'load')
def test_status_no_load_no_created(mock_load, mock_exists):
    """Test status when not created."""
    mock_exists.return_value = False
    vf = Vf()
    assert vf.status is None


@pytest.mark.parametrize("status", [const.COMMITED, const.CERTIFIED, const.UPLOADED, const.VALIDATED])
@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message')
def test_submit_not_Commited(mock_send, mock_load, mock_exists, status):
    """Do nothing if not created."""
    mock_exists.return_value = False
    vf = Vf()
    vf._status = status
    vf.submit()
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message')
def test_submit_OK(mock_send, mock_load, mock_exists):
    """Don't update status if submission NOK."""
    mock_exists.return_value = True
    vf = Vf()
    vf._status = const.COMMITED
    expected_data = '{\n  "userRemarks": "certify"\n}'
    vf._version = "1234"
    vf._unique_identifier = "12345"
    vf.submit()
    mock_send.assert_called_once_with(
        "POST", "Certify Vf",
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources/12345/lifecycleState/Certify',
        data=expected_data)

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
def test_onboard_new_vf_no_vsp(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Vf.status.fget)
    mock_status = Vf.status.getter(getter_mock)
    with mock.patch.object(Vf, 'status', mock_status):
        getter_mock.side_effect = [None, const.APPROVED, const.APPROVED]
        vf = Vf()
        with pytest.raises(ValueError):
            vf.onboard()
            mock_create.assert_not_called()
            mock_submit.assert_not_called()
            mock_load.assert_not_called()


@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
def test_onboard_new_vf(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Vf.status.fget)
    mock_status = Vf.status.getter(getter_mock)
    with mock.patch.object(Vf, 'status', mock_status):
        getter_mock.side_effect = [None, const.APPROVED, const.APPROVED,
                               const.APPROVED]
        vsp = Vsp()
        vf = Vf(vsp=vsp)
        vf._time_wait = 0
        vf.onboard()
        mock_create.assert_called_once()
        mock_submit.assert_not_called()
        mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
def test_onboard_vf_submit(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Vf.status.fget)
    mock_status = Vf.status.getter(getter_mock)
    with mock.patch.object(Vf, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, const.APPROVED,
                               const.APPROVED, const.APPROVED]
        vf = Vf()
        vf._time_wait = 0
        vf.onboard()
        mock_create.assert_not_called()
        mock_submit.assert_called_once()
        mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
def test_onboard_vf_load(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Vf.status.fget)
    mock_status = Vf.status.getter(getter_mock)
    with mock.patch.object(Vf, 'status', mock_status):
        getter_mock.side_effect = [const.CERTIFIED, const.CERTIFIED,
                               const.CERTIFIED, const.APPROVED, const.APPROVED,
                               const.APPROVED]
        vf = Vf()
        vf._time_wait = 0
        vf.onboard()
        mock_create.assert_not_called()
        mock_submit.assert_not_called()
        mock_load.assert_called_once()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
def test_onboard_whole_vf(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Vf.status.fget)
    mock_status = Vf.status.getter(getter_mock)
    with mock.patch.object(Vf, 'status', mock_status):
        getter_mock.side_effect = [None, const.DRAFT, const.DRAFT, const.CERTIFIED,
                               const.CERTIFIED, const.CERTIFIED, const.APPROVED,
                               const.APPROVED, const.APPROVED]
        vsp = Vsp()
        vf = Vf(vsp=vsp)
        vf._time_wait = 0
        vf.onboard()
        mock_create.assert_called_once()
        mock_submit.assert_called_once()
        mock_load.assert_called_once()


@mock.patch.object(Vf, "send_message_json")
def test_add_properties(mock_send_message_json):
    vf = Vf(name="test")
    vf._identifier = "toto"
    vf._unique_identifier = "toto"
    vf._status = const.CERTIFIED
    with pytest.raises(AttributeError):
        vf.add_property(Property(name="test", property_type="string"))
    vf._status = const.DRAFT
    vf.add_property(Property(name="test", property_type="string"))
    mock_send_message_json.assert_called_once()
