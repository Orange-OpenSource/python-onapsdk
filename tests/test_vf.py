#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test vf module."""

import json
import time
from unittest import mock
from unittest.mock import MagicMock
from pathlib import Path

import pytest

import onapsdk.constants as const
from onapsdk.exceptions import ParameterError, StatusError, RequestError, ValidationError
from onapsdk.sdc.category_management import ResourceCategory
from onapsdk.sdc.properties import ComponentProperty, NestedInput, Property
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
        {'resourceType': 'VF', 'name': 'one', 'uuid': '1234', 'invariantUUID': '5678', 'version': '1.0', 'lifecycleState': 'CERTIFIED', 'category': 'Generic', "subCategory": "Abstract"},
        {'resourceType': 'VF', 'name': 'two', 'uuid': '1235', 'invariantUUID': '5679', 'version': '1.0', 'lifecycleState': 'NOT_CERTIFIED_CHECKOUT', 'category': 'Generic', "subCategory": "Abstract"}]
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
    with pytest.raises(ParameterError) as err:
        vf.create()
    assert err.type == ParameterError
    assert str(err.value) == "At least vsp or vendor needs to be given"


@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
@mock.patch.object(Vf, "category", new_callable=mock.PropertyMock)
def test_create_already_exists(mock_category, mock_send, mock_exists):
    """Do nothing if already created in SDC."""
    vf = Vf(vendor=MagicMock())
    vsp = Vsp()
    vsp._identifier = "1232"
    vf.vsp = vsp
    mock_exists.return_value = True
    vf.create()
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
@mock.patch.object(Vf, "category", new_callable=mock.PropertyMock)
def test_create_issue_in_creation(mock_category, mock_send, mock_exists):
    """Do nothing if not created but issue during creation."""
    vf = Vf()
    vsp = Vsp()
    vendor = Vendor()
    vsp._identifier = "1232"
    vsp.create_csar = MagicMock(return_value=True)
    vsp.vendor = vendor
    vf.vsp = vsp
    expected_data = '{\n    "artifacts": {},\n    "attributes": [],\n    "capabilities": {},\n      "categories": [\n    {\n      "normalizedName": "generic",\n      "name": "Generic",\n      "uniqueId": "resourceNewCategory.generic",\n      "subcategories": [{"empty": false, "groupings": null, "icons": ["objectStorage", "compute"], "name": "Abstract", "normalizedName": "abstract", "ownerId": null, "type": null, "uniqueId": "resourceNewCategory.generic.abstract", "version": null}],\n      "version": null,\n      "ownerId": null,\n      "empty": false,\n      "type": null,\n      "icons": null\n    }\n  ],\n    "componentInstances": [],\n    "componentInstancesAttributes": {},\n    "componentInstancesProperties": {},\n    "componentType": "RESOURCE",\n    "contactId": "cs0008",\n    \n        "csarUUID": "None",\n        "csarVersion": "1.0",\n    \n    "deploymentArtifacts": {},\n    "description": "VF",\n    "icon": "defaulticon",\n    "name": "ONAP-test-VF",\n    "properties": [],\n    "groups": [],\n    "requirements": {},\n    "resourceType": "VF",\n    "tags": ["ONAP-test-VF"],\n    "toscaArtifacts": {},\n    "vendorName": "Generic-Vendor",\n    "vendorRelease": "1.0"\n}'
    mock_exists.return_value = False
    mock_send.side_effect = RequestError
    rc = ResourceCategory(
        name="Generic"
    )
    rc.normalized_name="generic"
    rc.unique_id="resourceNewCategory.generic"
    rc.subcategories=[{"empty": False, "groupings": None, "icons": ["objectStorage", "compute"], "name": "Abstract", "normalizedName": "abstract", "ownerId": None, "type": None, "uniqueId": "resourceNewCategory.generic.abstract", "version": None}]
    rc.version=None
    rc.owner_id=None
    rc.empty=False
    rc.type=None
    rc.icons=None
    mock_category.return_value = rc
    with pytest.raises(RequestError) as exc:
        vf.create()
    mock_send.assert_called_once_with("POST", "create Vf", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources', data=expected_data)
    assert not vf.created()


@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message_json')
@mock.patch.object(Vf, "category", new_callable=mock.PropertyMock)
def test_create_OK(mock_category, mock_send, mock_exists):
    """Create and update object."""
    vf = Vf()
    vsp = Vsp()
    vendor = Vendor()
    vsp._identifier = "1232"
    vf.vsp = vsp
    vsp.vendor = vendor
    vsp._csar_uuid = "1234"
    expected_data = '{\n    "artifacts": {},\n    "attributes": [],\n    "capabilities": {},\n      "categories": [\n    {\n      "normalizedName": "generic",\n      "name": "Generic",\n      "uniqueId": "resourceNewCategory.generic",\n      "subcategories": [{"empty": false, "groupings": null, "icons": ["objectStorage", "compute"], "name": "Abstract", "normalizedName": "abstract", "ownerId": null, "type": null, "uniqueId": "resourceNewCategory.generic.abstract", "version": null}],\n      "version": null,\n      "ownerId": null,\n      "empty": false,\n      "type": null,\n      "icons": null\n    }\n  ],\n    "componentInstances": [],\n    "componentInstancesAttributes": {},\n    "componentInstancesProperties": {},\n    "componentType": "RESOURCE",\n    "contactId": "cs0008",\n    \n        "csarUUID": "1234",\n        "csarVersion": "1.0",\n    \n    "deploymentArtifacts": {},\n    "description": "VF",\n    "icon": "defaulticon",\n    "name": "ONAP-test-VF",\n    "properties": [],\n    "groups": [],\n    "requirements": {},\n    "resourceType": "VF",\n    "tags": ["ONAP-test-VF"],\n    "toscaArtifacts": {},\n    "vendorName": "Generic-Vendor",\n    "vendorRelease": "1.0"\n}'
    mock_exists.return_value = False
    mock_send.return_value = {'resourceType': 'VF', 'name': 'one', 'uuid': '1234', 'invariantUUID': '5678', 'version': '1.0', 'uniqueId': '91011', 'lifecycleState': 'NOT_CERTIFIED_CHECKOUT'}
    rc = ResourceCategory(
        name="Generic"
    )
    rc.normalized_name="generic"
    rc.unique_id="resourceNewCategory.generic"
    rc.subcategories=[{"empty": False, "groupings": None, "icons": ["objectStorage", "compute"], "name": "Abstract", "normalizedName": "abstract", "ownerId": None, "type": None, "uniqueId": "resourceNewCategory.generic.abstract", "version": None}]
    rc.version=None
    rc.owner_id=None
    rc.empty=False
    rc.type=None
    rc.icons=None
    mock_category.return_value = rc
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
@mock.patch.object(Vf, 'add_resource')
def test_onboard_new_vf(mock_add_resource, mock_create, mock_submit, mock_load):
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
        mock_add_resource.assert_not_called()
        mock_submit.assert_not_called()
        mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
@mock.patch.object(Vf, 'add_resource')
def test_onboard_vf_submit(mock_add_resource, mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Vf.status.fget)
    mock_status = Vf.status.getter(getter_mock)
    with mock.patch.object(Vf, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, const.APPROVED,
                               const.APPROVED, const.APPROVED]
        vf = Vf()
        vf._time_wait = 0
        vf.onboard()
        mock_create.assert_not_called()
        mock_add_resource.assert_not_called()
        mock_submit.assert_called_once()
        mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
@mock.patch.object(Vf, 'add_resource')
def test_onboard_vf_load(mock_add_resource, mock_create, mock_submit, mock_load):
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
        mock_add_resource.assert_not_called()
        mock_submit.assert_not_called()
        mock_load.assert_called_once()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'submit')
@mock.patch.object(Vf, 'create')
@mock.patch.object(Vf, 'add_resource')
def test_onboard_whole_vf(mock_add_resource, mock_create, mock_submit, mock_load):
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
        mock_add_resource.assert_not_called()
        mock_submit.assert_called_once()
        mock_load.assert_called_once()


@mock.patch.object(Vf, "send_message_json")
def test_add_properties(mock_send_message_json):
    vf = Vf(name="test")
    vf._identifier = "toto"
    vf._unique_identifier = "toto"
    vf._status = const.CERTIFIED
    with pytest.raises(StatusError):
        vf.add_property(Property(name="test", property_type="string"))
    vf._status = const.DRAFT
    vf.add_property(Property(name="test", property_type="string"))
    mock_send_message_json.assert_called_once()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message')
def test_add_artifact_to_vf(mock_send_message, mock_load):
    """Test VF add artifact"""
    vf = Vf(name="test")
    vf.status = const.DRAFT
    mycbapath = Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip")

    result = vf.add_deployment_artifact(artifact_label="cba",
                                        artifact_type="CONTROLLER_BLUEPRINT_ARCHIVE",
                                        artifact_name="vLB_CBA_Python.zip",
                                        artifact=mycbapath)
    mock_send_message.assert_called()
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "Add deployment artifact for test sdc resource"
    assert url == ("https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources/"
                    f"{vf.unique_identifier}/artifacts")


@mock.patch.object(Vf, "created")
@mock.patch.object(ResourceCategory, "get")
def test_vf_category(mock_resource_category, mock_created):
    mock_created.return_value = False
    vf = Vf(name="test")
    _ = vf.category
    mock_resource_category.assert_called_once_with(name="Generic", subcategory="Abstract")
    mock_resource_category.reset_mock()

    vf = Vf(name="test", category="Allotted Resource", subcategory="Allotted Resource")
    _ = vf.category
    mock_resource_category.assert_called_once_with(name="Allotted Resource", subcategory="Allotted Resource")
    mock_resource_category.reset_mock()

    vf = Vf(name="test", category="test", subcategory="test")
    _ = vf.category
    mock_resource_category.assert_called_once_with(name="test", subcategory="test")
    mock_resource_category.reset_mock()

    mock_created.return_value = True
    _ = vf.category
    mock_resource_category.assert_called_once_with(name="test", subcategory="test")

@mock.patch.object(Vf, "send_message_json")
def test_update_vsp(mock_send):

    vf = Vf(name="test")
    vf._unique_identifier = "123"
    vsp = MagicMock()
    vsp.csar_uuid = "122333"
    vsp.human_readable_version = "1.0"
    mock_send.return_value = {
        "csarUUID": "322111",
        "csarVersion": "0.1",
        "tags": [],
        "categories": [],
        "allVersions": [],
        "archived": False,
        "creationDate": int(time.time()),
        "lastUpdateDate": int(time.time()),
    }
    vf.update_vsp(vsp)
    assert mock_send.call_count == 2
    mock_call_kwargs_data = json.loads(mock_send.mock_calls[-1][2]["data"])  # Get kward from `unittest.mock.call` tuple
    assert mock_call_kwargs_data["csarUUID"] == "122333"
    assert mock_call_kwargs_data["csarVersion"] == "1.0"

@mock.patch.object(Vf, 'exists')
@mock.patch.object(Vf, 'send_message')
def test_add_resource_not_draft(mock_send, mock_exists):
    mock_exists.return_value = False
    vf = Vf()
    resource = SdcResource()
    with pytest.raises(StatusError):
        vf.add_resource(resource)
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message')
def test_add_resource_bad_result(mock_send, mock_load):
    vf = Vf()
    vf.unique_identifier = "45"
    vf.identifier = "93"
    vf.status = const.DRAFT
    mock_send.return_value = {}
    resource = SdcResource()
    resource.unique_identifier = "12"
    resource.created = MagicMock(return_value=True)
    resource.version = "40"
    resource.name = "test"
    assert vf.add_resource(resource) is None
    mock_send.assert_called_once_with(
        'POST', 'Add SDCRESOURCE to VF',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources/45/resourceInstance',
        data='{\n  "name": "test",\n  "componentVersion": "40",\n  "posY": 100,\n  "posX": 200,\n  "uniqueId": "12",\n  "originType": "SDCRESOURCE",\n  "componentUid": "12",\n  "icon": "defaulticon"\n}')

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message')
def test_add_resource_OK(mock_send, mock_load):
    vf = Vf()
    vf.unique_identifier = "45"
    vf.identifier = "93"
    vf.status = const.DRAFT
    mock_send.return_value = {'yes': 'indeed'}
    resource = SdcResource()
    resource.unique_identifier = "12"
    resource.created = MagicMock(return_value=True)
    resource.version = "40"
    resource.name = "test"
    result = vf.add_resource(resource)
    assert result['yes'] == "indeed"
    mock_send.assert_called_once_with(
        'POST', 'Add SDCRESOURCE to VF',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources/45/resourceInstance',
        data='{\n  "name": "test",\n  "componentVersion": "40",\n  "posY": 100,\n  "posX": 200,\n  "uniqueId": "12",\n  "originType": "SDCRESOURCE",\n  "componentUid": "12",\n  "icon": "defaulticon"\n}')

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, "send_message_json")
@mock.patch.object(Vf, "resource_inputs_url")
def test_vf_vendor_property(mock_resource_inputs_url, mock_send_message_json, mock_created):
    mock_created.return_value = False
    vf = Vf()
    assert vf.vendor is None

    vsp_mock = MagicMock()
    vsp_mock.vendor = MagicMock()
    vf.vsp = vsp_mock
    assert vf.vendor == vsp_mock.vendor

    vf._vendor = None
    mock_created.return_value = True
    mock_send_message_json.return_value = {"vendorName": "123"}
    assert vf.vendor.name == "123"

@mock.patch.object(SdcResource, "declare_input")
@mock.patch.object(Vf, "send_message")
def test_vf_declare_input(mock_send_message, mock_sdc_resource_declare_input):
    vf = Vf()
    prop = Property(name="test_prop", property_type="string")
    nested_input = NestedInput(MagicMock(), MagicMock())
    vf.declare_input(prop)
    mock_sdc_resource_declare_input.assert_called_once()
    mock_send_message.assert_not_called()
    mock_sdc_resource_declare_input.reset_mock()
    vf.declare_input(nested_input)
    mock_sdc_resource_declare_input.assert_called_once()
    mock_send_message.assert_not_called()
    mock_sdc_resource_declare_input.reset_mock()
    vf.declare_input(ComponentProperty("test_unique_id", "test_property_type", "test_name", MagicMock()))
    mock_send_message.assert_called()
    mock_sdc_resource_declare_input.assert_not_called()
