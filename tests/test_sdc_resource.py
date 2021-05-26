#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcResource module."""
from unittest import mock
import logging

import pytest

import onapsdk.constants as const
from onapsdk.exceptions import ParameterError, RequestError, ResourceNotFound
from onapsdk.onap_service import OnapService
from onapsdk.sdc.component import Component
from onapsdk.sdc.properties import ComponentProperty, Input, NestedInput, Property
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.service import Service
from onapsdk.sdc.vf import Vf
from onapsdk.utils.headers_creator import headers_sdc_tester
from onapsdk.utils.headers_creator import headers_sdc_creator


COMPONENT_PROPERTIES = [
    {
        "uniqueId":"3d9a184f-4268-4a0e-9ddd-252e49670013.vf_module_id",
        "type":"string",
        "required":False,
        "definition":False,
        "description":"The vFirewall Module ID is provided by ECOMP",
        "password":False,
        "name":"vf_module_id",
        "label":"vFirewall module ID",
        "hidden":False,
        "immutable":False,
        "isDeclaredListInput":False,
        "getInputProperty":False,
        "empty":False
    },{
        "uniqueId":"74f79006-ae56-4d58-947e-6a5089000774.skip_post_instantiation_configuration",
        "type":"boolean",
        "required":False,
        "definition":False,
        "password":False,
        "name":"skip_post_instantiation_configuration",
        "value":"true",
        "hidden":False,
        "immutable":False,
        "parentUniqueId":"74f79006-ae56-4d58-947e-6a5089000774",
        "isDeclaredListInput":False,
        "getInputProperty":False,
        "ownerId":"74f79006-ae56-4d58-947e-6a5089000774",
        "empty":False
    }
]



def test_init():
    """Test the initialization."""
    element = SdcResource()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert SdcResource.server == "SDC"
    assert SdcResource.base_front_url == "https://sdc.api.fe.simpledemo.onap.org:30207"
    assert SdcResource.base_back_url == "https://sdc.api.be.simpledemo.onap.org:30204"
    assert SdcResource.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=",
            "USER_ID": "cs0008",
            "X-ECOMP-InstanceID": "onapsdk"
        }

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

@mock.patch.object(Vf, 'deep_load')
def test__unique_identifier_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf.unique_identifier == None
    mock_load.assert_called_once()

@mock.patch.object(Vf, 'deep_load')
def test__unique_identifier_no_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    vf._unique_identifier= "toto"
    assert vf.unique_identifier == "toto"
    mock_load.assert_not_called()

def test__status_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.status = "4567"
    assert vf._status == "4567"

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_request_error(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.side_effect = RequestError
    with pytest.raises(RequestError) as err:
        vf.deep_load()
    assert err.type == RequestError
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/screen?excludeTypes=VFCMT&excludeTypes=Configuration".format(vf.base_front_url),
                                      headers=headers_sdc_creator(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_OK(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5689"
    vf.unique_uuid = "1234"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011', 'invariantUUID': '1234', 'categories': [{'name': 'test', 'subcategories': [{'name': 'test_subcategory'}]}]}]}
    vf.deep_load()
    assert vf.unique_identifier == "71011"
    assert vf._category_name == "test"
    assert vf._subcategory_name == "test_subcategory"
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/screen?excludeTypes=VFCMT&excludeTypes=Configuration".format(vf.base_front_url),
                                      headers=headers_sdc_creator(vf.headers))

@mock.patch.object(Service, 'created')
@mock.patch.object(Service, 'send_message_json')
def test__deep_load_response_OK_dependency(mock_send, mock_created):
    mock_created.return_value = True
    vf = Service()
    vf.identifier = "4321"
    vf.unique_uuid = "1234"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.side_effect = [{'services': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011', 'invariantUUID': '1234', 'categories': [{'name': 'test', 'subcategories': [{'name': 'test_subcategory'}]}]}]}, [{'version': '4567', 'uniqueId': '71011'}]]
    vf.deep_load()
    assert vf.unique_identifier == "71011"

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_NOK(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5678"
    vf.unique_uuid = "1234"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011', 'invariantUUID': '1234', }]}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/screen?excludeTypes=VFCMT&excludeTypes=Configuration".format(vf.base_front_url),
                                      headers=headers_sdc_creator(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_OK_under_cert(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5689"
    vf.unique_uuid = "1234"
    vf._version = "4567"
    vf._status = const.UNDER_CERTIFICATION
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011', 'invariantUUID': '1234', 'categories': [{'name': 'test', 'subcategories': [{'name': 'test_subcategory'}]}]}]}
    vf.deep_load()
    assert vf.unique_identifier == "71011"
    assert vf._category_name == "test"
    assert vf._subcategory_name == "test_subcategory"
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/screen?excludeTypes=VFCMT&excludeTypes=Configuration".format(vf.base_front_url),
                                      headers=headers_sdc_tester(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_NOK_under_cert(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5678"
    vf.unique_uuid = "1234"
    vf._version = "4567"
    vf._status = const.UNDER_CERTIFICATION
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'invariantUUID': '1234', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/screen?excludeTypes=VFCMT&excludeTypes=Configuration".format(vf.base_front_url),
                                      headers=headers_sdc_tester(vf.headers))

def test__parse_sdc_status_certified():
    assert SdcResource._parse_sdc_status("CERTIFIED", None, logging.getLogger()) == const.CERTIFIED

def test__parse_sdc_status_certified_not_approved():
    assert SdcResource._parse_sdc_status("CERTIFIED",
                                         const.DISTRIBUTION_NOT_APPROVED,
                                         logging.getLogger()) == const.CERTIFIED

def test__parse_sdc_status_certified_approved():
    assert SdcResource._parse_sdc_status("CERTIFIED",
                                         const.DISTRIBUTION_APPROVED,
                                         logging.getLogger()) == const.CERTIFIED

def test__parse_sdc_status_distributed():
    assert SdcResource._parse_sdc_status("CERTIFIED", const.SDC_DISTRIBUTED,
                                         logging.getLogger()) == const.DISTRIBUTED

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status(const.NOT_CERTIFIED_CHECKOUT, None,
                                         logging.getLogger() ) == const.DRAFT

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status(const.NOT_CERTIFIED_CHECKIN, None,
                                         logging.getLogger() ) == const.CHECKED_IN

def test__parse_sdc_status_submitted():
    assert SdcResource._parse_sdc_status(const.READY_FOR_CERTIFICATION, None,
                                         logging.getLogger() ) == const.SUBMITTED

def test__parse_sdc_status_under_certification():
    assert SdcResource._parse_sdc_status(const.CERTIFICATION_IN_PROGRESS, None,
                                         logging.getLogger() ) == const.UNDER_CERTIFICATION

def test__parse_sdc_status_unknown():
    assert SdcResource._parse_sdc_status("UNKNOWN", None, logging.getLogger() ) == 'UNKNOWN'

def test__parse_sdc_status_empty():
    assert SdcResource._parse_sdc_status("", None, logging.getLogger() ) is None

def test__really_submit():
    sdcResource = SdcResource()
    with pytest.raises(NotImplementedError):
        sdcResource._really_submit()

def test__action_url_no_action_type():
    sdcResource = SdcResource()
    url = sdcResource._action_url("base", "subpath", "version_path")
    assert url == "base/resources/version_path/lifecycleState/subpath"

def test__action_url_action_type():
    sdcResource = SdcResource()
    url = sdcResource._action_url("base", "subpath", "version_path",
                                  action_type="distribution")
    assert url == "base/resources/version_path/distribution/subpath"

@mock.patch.object(SdcResource, '_parse_sdc_status')
def test_update_informations_from_sdc_creation_no_distribitution_state(mock_parse):
    mock_parse.return_value = "12"
    sdcResource = SdcResource()
    details = {'invariantUUID': '1234',
               'lifecycleState': 'state',
               'version': 'v12',
               'uniqueId': '5678'}

    sdcResource.update_informations_from_sdc_creation(details)
    assert sdcResource.unique_uuid == "1234"
    assert sdcResource.status == "12"
    assert sdcResource.version == "v12"
    assert sdcResource.unique_identifier == "5678"
    mock_parse.assert_called_once_with("state", None, mock.ANY)

@mock.patch.object(SdcResource, '_parse_sdc_status')
def test_update_informations_from_sdc_creation_distribitution_state(mock_parse):
    mock_parse.return_value = "bgt"
    sdcResource = SdcResource()
    details = {'invariantUUID': '1234',
               'lifecycleState': 'state',
               'distributionStatus': 'trez',
               'version': 'v12',
               'uniqueId': '5678'}

    sdcResource.update_informations_from_sdc_creation(details)
    assert sdcResource.unique_uuid == "1234"
    assert sdcResource.status == "bgt"
    assert sdcResource.version == "v12"
    assert sdcResource.unique_identifier == "5678"
    mock_parse.assert_called_once_with("state", 'trez', mock.ANY)

@mock.patch.object(SdcResource, "is_own_property")
@mock.patch.object(SdcResource, "declare_input_for_own_property")
@mock.patch.object(SdcResource, "declare_nested_input")
def test_declare_input(mock_nested, mock_own, mock_is_own):
    sdc_resource = SdcResource()
    prop = Property(name="test", property_type="test")
    mock_is_own.return_value = False
    with pytest.raises(ParameterError):
        sdc_resource.declare_input(prop)
    mock_is_own.return_value = True
    sdc_resource.declare_input(prop)
    mock_own.assert_called_once()
    mock_nested.assert_not_called()

    mock_nested.reset_mock()
    mock_own.reset_mock()
    sdc_resource.declare_input(NestedInput(sdc_resource=mock.MagicMock(), input_obj=mock.MagicMock()))
    mock_own.assert_not_called()
    mock_nested.assert_called_once()

@mock.patch.object(SdcResource, "send_message_json")
@mock.patch.object(SdcResource, "get_component")
@mock.patch.object(SdcResource, "resource_inputs_url", new_callable=mock.PropertyMock)
def test_declare_nested_input(mock_resource_inputs, mock_get_component, mock_send_json):
    sdc_resource = SdcResource()
    sdc_resource.unique_identifier = "toto"
    mock_resource_inputs.return_value = "test"
    sdc_resource.declare_input(NestedInput(sdc_resource=mock.MagicMock(), input_obj=mock.MagicMock()))
    mock_get_component.assert_called_once()
    mock_send_json.assert_called_once()

@mock.patch.object(SdcResource, "inputs", new_callable=mock.PropertyMock)
def test_get_input(mock_inputs):
    sdc_resource = SdcResource()

    mock_inputs.return_value = [
        Input(unique_id="123",
              input_type="integer",
              name="test",
              sdc_resource=sdc_resource),
        Input(unique_id="321",
              input_type="string",
              name="test2",
              sdc_resource=sdc_resource)
    ]
    assert sdc_resource.get_input("test")
    assert sdc_resource.get_input("test2")
    with pytest.raises(ResourceNotFound):
        sdc_resource.get_input("test3")

@mock.patch.object(SdcResource, "components", new_callable=mock.PropertyMock)
def test_get_component(mock_components):
    sdc_resource = SdcResource()

    mock_components.return_value = [
        Component(
            created_from_csar=False,
            actual_component_uid="123",
            unique_id="123",
            normalized_name="123",
            name="123",
            origin_type="123",
            customization_uuid="123",
            tosca_component_name="123",
            component_name="123",
            component_uid="123",
            component_version="123",
            sdc_resource=SdcResource(name="test"),
            parent_sdc_resource=sdc_resource
        )
    ]
    assert sdc_resource.get_component(SdcResource(name="test"))
    with pytest.raises(ResourceNotFound):
        sdc_resource.get_component(SdcResource(name="test2"))

def test_component_properties():
    sdc_resource = mock.MagicMock()
    parent_sdc_resource = SdcResource()

    component = Component(
            created_from_csar=False,
            actual_component_uid="123",
            unique_id="123",
            normalized_name="123",
            name="123",
            origin_type="123",
            customization_uuid="123",
            tosca_component_name="123",
            component_name="123",
            component_uid="123",
            component_version="123",
            sdc_resource=sdc_resource,
            parent_sdc_resource=mock.MagicMock()
    )
    sdc_resource.send_message_json.return_value = {}
    assert not len(list(component.properties))

    sdc_resource.send_message_json.return_value = COMPONENT_PROPERTIES
    properties = list(component.properties)
    assert len(properties) == 2
    prop1, prop2 = properties

    assert prop1.unique_id == "3d9a184f-4268-4a0e-9ddd-252e49670013.vf_module_id"
    assert prop1.property_type == "string"
    assert prop1.name == "vf_module_id"
    assert prop1.value is None

    assert prop2.unique_id == "74f79006-ae56-4d58-947e-6a5089000774.skip_post_instantiation_configuration"
    assert prop2.property_type == "boolean"
    assert prop2.name == "skip_post_instantiation_configuration"
    assert prop2.value == "true"

@mock.patch.object(Component, "properties", new_callable=mock.PropertyMock)
def test_component_property_set_value(mock_component_properties):
    mock_sdc_resource = mock.MagicMock()
    component = Component(
            created_from_csar=False,
            actual_component_uid="123",
            unique_id="123",
            normalized_name="123",
            name="123",
            origin_type="123",
            customization_uuid="123",
            tosca_component_name="123",
            component_name="123",
            component_uid="123",
            component_version="123",
            sdc_resource=mock_sdc_resource,
            parent_sdc_resource=mock.MagicMock()
    )
    mock_component_properties.return_value = [
        ComponentProperty(
            unique_id="123",
            property_type="string",
            name="test_property",
            component=component
        )
    ]
    with pytest.raises(ParameterError):
        component.get_property(property_name="non_exists")
    prop1 = component.get_property(property_name="test_property")
    assert prop1.name == "test_property"
    assert prop1.unique_id == "123"
    assert prop1.property_type == "string"
    assert not prop1.value

    prop1.value = "123"
    mock_sdc_resource.send_message_json.assert_called_once()

@mock.patch.object(SdcResource, "_action_to_sdc")
def test_sdc_resource_checkout(mock_action_to_sdc):
    mock_action_to_sdc.return_value = None
    sdc_resource = SdcResource()
    sdc_resource.checkout()
    mock_action_to_sdc.assert_called_once_with(const.CHECKOUT, "lifecycleState")
