#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test pnf module."""

from unittest import mock
from unittest.mock import MagicMock
from pathlib import Path

import pytest

import onapsdk.constants as const
from onapsdk.exceptions import ParameterError, RequestError, StatusError
from onapsdk.sdc.category_management import ResourceCategory
from onapsdk.sdc.properties import Property
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.pnf import Pnf
from onapsdk.sdc.vsp import Vsp
from onapsdk.sdc.vsp import Vendor


@mock.patch.object(Pnf, 'send_message_json')
def test_get_all_no_pnf(mock_send):
    """Returns empty array if no pnfs."""
    mock_send.return_value = {}
    assert Pnf.get_all() == []
    mock_send.assert_called_once_with("GET", 'get Pnfs', 'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/resources?resourceType=PNF')


@mock.patch.object(Pnf, 'send_message_json')
def test_get_all_some_pnfs(mock_send):
    """Returns a list of pnfs."""
    mock_send.return_value = [
        {'resourceType': 'PNF', 'name': 'one', 'uuid': '1234', 'invariantUUID': '5678', 'version': '1.0', 'lifecycleState': 'CERTIFIED', 'category': 'Generic', "subCategory": "Abstract"},
        {'resourceType': 'PNF', 'name': 'two', 'uuid': '1235', 'invariantUUID': '5679', 'version': '1.0', 'lifecycleState': 'NOT_CERTIFIED_CHECKOUT', 'category': 'Generic', "subCategory": "Abstract"}]
    all_pnfs = Pnf.get_all()
    assert len(all_pnfs) == 2
    pnf_1 = all_pnfs[0]
    assert pnf_1.name == "one"
    assert pnf_1.identifier == "1234"
    assert pnf_1.unique_uuid == "5678"
    assert pnf_1.version == "1.0"
    assert pnf_1.status == const.CERTIFIED
    assert pnf_1.created()
    pnf_2 = all_pnfs[1]
    assert pnf_2.name == "two"
    assert pnf_2.identifier == "1235"
    assert pnf_2.unique_uuid == "5679"
    assert pnf_2.status == const.DRAFT
    assert pnf_2.version == "1.0"
    assert pnf_2.created()
    mock_send.assert_called_once_with("GET", 'get Pnfs', 'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/resources?resourceType=PNF')


def test_init_no_name():
    """Check init with no names."""
    pnf = Pnf()
    assert isinstance(pnf, SdcResource)
    assert pnf._identifier is None
    assert pnf._version is None
    assert pnf.name == "ONAP-test-PNF"
    assert pnf.headers["USER_ID"] == "cs0008"
    assert pnf.vsp is None
    assert pnf.vendor is None
    assert isinstance(pnf._base_url(), str)

@mock.patch.object(Pnf, 'exists')
def test_init_with_name(mock_exists):
    """Check init with names."""
    mock_exists.return_value = False
    pnf = Pnf(name="YOLO")
    assert pnf._identifier == None
    assert pnf._version == None
    assert pnf.name == "YOLO"
    assert pnf.created() == False
    assert pnf.headers["USER_ID"] == "cs0008"
    assert pnf.vsp == None
    assert isinstance(pnf._base_url(), str)


def test_equality_really_equals():
    """Check two pnfs are equals if name is the same."""
    pnf_1 = Pnf(name="equal")
    pnf_1.identifier = "1234"
    pnf_2 = Pnf(name="equal")
    pnf_2.identifier = "1235"
    assert pnf_1 == pnf_2


def test_equality_not_equals():
    """Check two pnfs are not equals if name is not the same."""
    pnf_1 = Pnf(name="equal")
    pnf_1.identifier = "1234"
    pnf_2 = Pnf(name="not_equal")
    pnf_2.identifier = "1234"
    assert pnf_1 != pnf_2


def test_equality_not_equals_not_same_object():
    """Check a pnf and something different are not equals."""
    pnf_1 = Pnf(name="equal")
    pnf_1.identifier = "1234"
    pnf_2 = SdcResource()
    pnf_2.name = "equal"
    assert pnf_1 != pnf_2


@mock.patch.object(Pnf, 'get_all')
def test_exists_not_exists(mock_get_all):
    """Return False if pnf doesn't exist in SDC."""
    pnf_1 = Pnf(name="one")
    pnf_1.identifier = "1234"
    mock_get_all.return_value = [pnf_1]
    pnf = Pnf(name="two")
    assert not pnf.exists()


@mock.patch.object(Pnf, 'get_all')
def test_exists(mock_get_all):
    """Return True if pnf exists in SDC."""
    pnf_1 = Pnf(name="one")
    pnf_1.identifier = "1234"
    pnf_1.unique_uuid = "5689"
    pnf_1.unique_identifier = "71011"
    pnf_1.status = const.DRAFT
    pnf_1.version = "1.1"
    mock_get_all.return_value = [pnf_1]
    pnf = Pnf(name="one")
    assert pnf.exists()
    assert pnf.identifier == "1234"
    assert pnf.unique_uuid == "5689"
    assert pnf.unique_identifier == "71011"
    assert pnf.status == const.DRAFT
    assert pnf.version == "1.1"


@mock.patch.object(Pnf, 'exists')
def test_load_created(mock_exists):
    """Load is a wrapper around exists()."""
    pnf = Pnf(name="one")
    pnf.load()
    mock_exists.assert_called_once()


@mock.patch.object(Pnf, 'exists')
def test_create_no_vsp_no_vendor(mock_exists):
    """Do nothing if no vsp and no vendor"""
    pnf = Pnf()
    mock_exists.return_value = False
    with pytest.raises(ParameterError) as err:
        pnf.create()
    assert err.type == ParameterError
    assert str(err.value) == "Neither Vsp nor Vendor provided."


@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'send_message_json')
@mock.patch.object(Pnf, "category")
def test_create_already_exists(mock_category, mock_send, mock_exists):
    """Do nothing if already created in SDC."""
    pnf = Pnf()
    vsp = Vsp()
    vsp._identifier = "1232"
    pnf.vsp = vsp
    mock_exists.return_value = True
    pnf.create()
    mock_send.assert_not_called()


@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'send_message_json')
@mock.patch.object(Pnf, "category", new_callable=mock.PropertyMock)
def test_create_issue_in_creation(mock_category, mock_send, mock_exists):
# def test_create_issue_in_creation(mock_send, mock_exists):
    """Do nothing if not created but issue during creation."""
    pnf = Pnf()
    vsp = Vsp()
    vendor = Vendor()
    vsp._identifier = "1232"
    vsp.create_csar = MagicMock(return_value=True)
    vsp.vendor = vendor
    pnf.vsp = vsp
    expected_data = '{\n    "artifacts": {},\n    "attributes": [],\n    "capabilities": {},\n      "categories": [\n    {\n      "normalizedName": "generic",\n      "name": "Generic",\n      "uniqueId": "resourceNewCategory.generic",\n      "subcategories": [{"empty": false, "groupings": null, "icons": ["objectStorage", "compute"], "name": "Abstract", "normalizedName": "abstract", "ownerId": null, "type": null, "uniqueId": "resourceNewCategory.generic.abstract", "version": null}],\n      "version": null,\n      "ownerId": null,\n      "empty": false,\n      "type": null,\n      "icons": null\n    }\n  ],\n    "componentInstances": [],\n    "componentInstancesAttributes": {},\n    "componentInstancesProperties": {},\n    "componentType": "RESOURCE",\n    "contactId": "cs0008",\n    \n    "csarUUID": "None",\n    "csarVersion": "1.0",\n    "vendorName": "Generic-Vendor",\n    \n    "deploymentArtifacts": {},\n    "description": "PNF",\n    "icon": "defaulticon",\n    "name": "ONAP-test-PNF",\n    "properties": [],\n    "groups": [],\n    "requirements": {},\n    "resourceType": "PNF",\n    "tags": ["ONAP-test-PNF"],\n    "toscaArtifacts": {},\n    "vendorRelease": "1.0"\n}'
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
    pnf.create()
    mock_send.assert_called_once_with("POST", "create Pnf", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources', data=expected_data)
    assert not pnf.created()


@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'send_message_json')
@mock.patch.object(Pnf, "category", new_callable=mock.PropertyMock)
def test_create_OK(mock_category, mock_send, mock_exists):
    """Create and update object."""
    pnf = Pnf()
    vsp = Vsp()
    vendor = Vendor()
    vsp._identifier = "1232"
    pnf.vsp = vsp
    vsp.vendor = vendor
    vsp._csar_uuid = "1234"
    expected_data = '{\n    "artifacts": {},\n    "attributes": [],\n    "capabilities": {},\n      "categories": [\n    {\n      "normalizedName": "generic",\n      "name": "Generic",\n      "uniqueId": "resourceNewCategory.generic",\n      "subcategories": [{"empty": false, "groupings": null, "icons": ["objectStorage", "compute"], "name": "Abstract", "normalizedName": "abstract", "ownerId": null, "type": null, "uniqueId": "resourceNewCategory.generic.abstract", "version": null}],\n      "version": null,\n      "ownerId": null,\n      "empty": false,\n      "type": null,\n      "icons": null\n    }\n  ],\n    "componentInstances": [],\n    "componentInstancesAttributes": {},\n    "componentInstancesProperties": {},\n    "componentType": "RESOURCE",\n    "contactId": "cs0008",\n    \n    "csarUUID": "1234",\n    "csarVersion": "1.0",\n    "vendorName": "Generic-Vendor",\n    \n    "deploymentArtifacts": {},\n    "description": "PNF",\n    "icon": "defaulticon",\n    "name": "ONAP-test-PNF",\n    "properties": [],\n    "groups": [],\n    "requirements": {},\n    "resourceType": "PNF",\n    "tags": ["ONAP-test-PNF"],\n    "toscaArtifacts": {},\n    "vendorRelease": "1.0"\n}'
    mock_exists.return_value = False
    mock_send.return_value = {'resourceType': 'PNF', 'name': 'one', 'uuid': '1234', 'invariantUUID': '5678', 'version': '1.0', 'uniqueId': '91011', 'lifecycleState': 'NOT_CERTIFIED_CHECKOUT'}
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
    pnf.create()
    mock_send.assert_called_once_with("POST", "create Pnf", 'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources', data=expected_data)
    assert pnf.created()
    assert pnf._status == const.DRAFT
    assert pnf.identifier == "1234"
    assert pnf.unique_uuid == "5678"
    assert pnf.version == "1.0"

@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'load')
def test_version_no_load_no_created(mock_load, mock_exists):
    """Test versions when not created."""
    mock_exists.return_value = False
    pnf = Pnf()
    assert pnf.version is None
    mock_load.assert_not_called()

@mock.patch.object(Pnf, 'load')
def test_version_no_load_created(mock_load):
    """Test versions when created."""
    pnf = Pnf()
    pnf.identifier = "1234"
    pnf._version = "64"
    assert pnf.version == "64"
    mock_load.assert_not_called()


@mock.patch.object(Pnf, 'load')
def test_version_with_load(mock_load):
    """Test versions when not created but with identifier."""
    pnf = Pnf()
    pnf.identifier = "1234"
    assert pnf.version is None
    mock_load.assert_called_once()

@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'load')
def test_status_no_load_no_created(mock_load, mock_exists):
    """Test status when not created."""
    mock_exists.return_value = False
    pnf = Pnf()
    assert pnf.status is None


@pytest.mark.parametrize("status", [const.COMMITED, const.CERTIFIED, const.UPLOADED, const.VALIDATED])
@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'send_message')
def test_submit_not_Commited(mock_send, mock_load, mock_exists, status):
    """Do nothing if not created."""
    mock_exists.return_value = False
    pnf = Pnf()
    pnf._status = status
    pnf.submit()
    mock_send.assert_not_called()

@mock.patch.object(Pnf, 'exists')
@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'send_message')
def test_submit_OK(mock_send, mock_load, mock_exists):
    """Don't update status if submission NOK."""
    mock_exists.return_value = True
    pnf = Pnf()
    pnf._status = const.COMMITED
    expected_data = '{\n  "userRemarks": "certify"\n}'
    pnf._version = "1234"
    pnf._unique_identifier = "12345"
    pnf.submit()
    mock_send.assert_called_once_with(
        "POST", "Certify Pnf",
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources/12345/lifecycleState/Certify',
        data=expected_data)


@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'submit')
@mock.patch.object(Pnf, 'create')
def test_onboard_new_pnf(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Pnf.status.fget)
    mock_status = Pnf.status.getter(getter_mock)
    with mock.patch.object(Pnf, 'status', mock_status):
        getter_mock.side_effect = [None, const.APPROVED, const.APPROVED,
                               const.APPROVED]
        vsp = Vsp()
        pnf = Pnf(vsp=vsp)
        pnf._time_wait = 0
        pnf.onboard()
        mock_create.assert_called_once()
        mock_submit.assert_not_called()
        mock_load.assert_not_called()

@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'submit')
@mock.patch.object(Pnf, 'create')
def test_onboard_pnf_submit(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Pnf.status.fget)
    mock_status = Pnf.status.getter(getter_mock)
    with mock.patch.object(Pnf, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, const.APPROVED,
                               const.APPROVED, const.APPROVED]
        pnf = Pnf()
        pnf._time_wait = 0
        pnf.onboard()
        mock_create.assert_not_called()
        mock_submit.assert_called_once()
        mock_load.assert_not_called()

@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'submit')
@mock.patch.object(Pnf, 'create')
def test_onboard_pnf_load(mock_create, mock_submit, mock_load):
    getter_mock = mock.Mock(wraps=Pnf.status.fget)
    mock_status = Pnf.status.getter(getter_mock)
    with mock.patch.object(Pnf, 'status', mock_status):
        getter_mock.side_effect = [const.CERTIFIED, const.CERTIFIED,
                               const.CERTIFIED, const.APPROVED, const.APPROVED,
                               const.APPROVED]
        pnf = Pnf()
        pnf._time_wait = 0
        pnf.onboard()
        mock_create.assert_not_called()
        mock_submit.assert_not_called()
        mock_load.assert_called_once()

@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'submit')
@mock.patch.object(Pnf, 'create')
def test_onboard_whole_pnf_vsp(mock_create, mock_submit, mock_load):
    """Test onboarding with vsp"""
    getter_mock = mock.Mock(wraps=Pnf.status.fget)
    mock_status = Pnf.status.getter(getter_mock)
    with mock.patch.object(Pnf, 'status', mock_status):
        getter_mock.side_effect = [None, const.DRAFT, const.DRAFT, const.CERTIFIED,
                               const.CERTIFIED, const.CERTIFIED, const.APPROVED,
                               const.APPROVED, const.APPROVED]
        vsp = Vsp()
        pnf = Pnf(vsp=vsp)
        pnf._time_wait = 0
        pnf.onboard()
        mock_create.assert_called_once()
        mock_submit.assert_called_once()
        mock_load.assert_called_once()

@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'submit')
@mock.patch.object(Pnf, 'create')
def test_onboard_whole_pnf_vendor(mock_create, mock_submit, mock_load):
    """Test onboarding with vendor"""
    getter_mock = mock.Mock(wraps=Pnf.status.fget)
    mock_status = Pnf.status.getter(getter_mock)
    with mock.patch.object(Pnf, 'status', mock_status):
        getter_mock.side_effect = [None, const.DRAFT, const.DRAFT, const.CERTIFIED,
                               const.CERTIFIED, const.CERTIFIED, const.APPROVED,
                               const.APPROVED, const.APPROVED]
        vendor = Vendor()
        pnf = Pnf(vendor=vendor)
        pnf._time_wait = 0
        pnf.onboard()
        mock_create.assert_called_once()
        mock_submit.assert_called_once()
        mock_load.assert_called_once()

@mock.patch.object(Pnf, "send_message_json")
def test_add_properties(mock_send_message_json):
    pnf = Pnf(name="test")
    pnf._identifier = "toto"
    pnf._unique_identifier = "toto"
    pnf._status = const.CERTIFIED
    with pytest.raises(StatusError) as err:
        pnf.add_property(Property(name="test", property_type="string"))
    pnf._status = const.DRAFT
    pnf.add_property(Property(name="test", property_type="string"))
    mock_send_message_json.assert_called_once()

@mock.patch.object(Pnf, 'load')
@mock.patch.object(Pnf, 'send_message')
def test_add_artifact_to_pnf(mock_send_message, mock_load):
    """Test Pnf add artifact"""
    pnf = Pnf(name="test")
    pnf.status = const.DRAFT
    mycbapath = Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip")

    result = pnf.add_deployment_artifact(artifact_label="cba",
                                        artifact_type="CONTROLLER_BLUEPRINT_ARCHIVE",
                                        artifact_name="vLB_CBA_Python.zip",
                                        artifact=mycbapath)
    mock_send_message.assert_called()
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "Add deployment artifact for test sdc resource"
    assert url == ("https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/resources/"
                    f"{pnf.unique_identifier}/artifacts")


@mock.patch.object(Pnf, "created")
@mock.patch.object(ResourceCategory, "get")
def test_pnf_category(mock_resource_category, mock_created):
    mock_created.return_value = False
    pnf = Pnf(name="test")
    _ = pnf.category
    mock_resource_category.assert_called_once_with(name="Generic", subcategory="Abstract")
    mock_resource_category.reset_mock()

    pnf = Pnf(name="test", category="test", subcategory="test")
    _ = pnf.category
    mock_resource_category.assert_called_once_with(name="test", subcategory="test")
    mock_resource_category.reset_mock()

    mock_created.return_value = True
    _ = pnf.category
    mock_resource_category.assert_called_once_with(name="test", subcategory="test")
