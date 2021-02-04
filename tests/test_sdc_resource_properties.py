from unittest import mock

import pytest

from onapsdk.exceptions import ParameterError
from onapsdk.sdc.properties import Input, Property
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.service import Service
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vl import Vl

INPUTS = {
    'inputs': [
        {
            'uniqueId': '9ee5fb23-4c4a-46bd-8682-68698559ee9c.skip_post_instantiation_configuration',
            'type': 'boolean',
            'required': False,
            'definition': False,
            'defaultValue': 'true',
            'description': None,
            'schema': None,
            'password': False,
            'name': 'skip_post_instantiation_configuration',
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': None,
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': '9ee5fb23-4c4a-46bd-8682-68698559ee9c',
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'constraints': None,
            'inputs': None,
            'properties': None,
            'schemaType': None,
            'schemaProperty': None,
            'getInputProperty': False,
            'version': None,
            'ownerId': '9ee5fb23-4c4a-46bd-8682-68698559ee9c',
            'empty': False
        },
        {
            'uniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079.test',
            'type': 'string',
            'required': False,
            'definition': False,
            'defaultValue': None,
            'description': None,
            'schema': {
                'derivedFrom': None,
                'constraints': None,
                'properties': None,
                'property': {
                    'uniqueId': None,
                    'type': '',
                    'required': False,
                    'definition': False,
                    'defaultValue': None,
                    'description': None,
                    'schema': None,
                    'password': False,
                    'name': None,
                    'value': None,
                    'label': None,
                    'hidden': False,
                    'immutable': False,
                    'inputPath': None,
                    'status': None,
                    'inputId': None,
                    'instanceUniqueId': None,
                    'propertyId': None,
                    'parentPropertyType': None,
                    'subPropertyInputPath': None,
                    'annotations': None,
                    'parentUniqueId': None,
                    'getInputValues': None,
                    'isDeclaredListInput': False,
                    'getPolicyValues': None,
                    'propertyConstraints': None,
                    'schemaType': None,
                    'schemaProperty': None,
                    'getInputProperty': False,
                    'version': None,
                    'ownerId': None,
                    'empty': False
                },
                'version': None,
                'ownerId': None,
                'empty': False,
                'type': None
            },
            'password': False,
            'name': 'test',
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
            'propertyId': '4a84415b-4580-4a78-aa33-501f0cd3d079.sraka',
            'parentPropertyType': 'string',
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': 'cs0008',
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'constraints': None,
            'inputs': None,
            'properties': None,
            'schemaType': '',
            'schemaProperty': {
                'uniqueId': None,
                'type': '',
                'required': False,
                'definition': False,
                'defaultValue': None,
                'description': None,
                'schema': None,
                'password': False,
                'name': None,
                'value': None,
                'label': None,
                'hidden': False,
                'immutable': False,
                'inputPath': None,
                'status': None,
                'inputId': None,
                'instanceUniqueId': None,
                'propertyId': None,
                'parentPropertyType': None,
                'subPropertyInputPath': None,
                'annotations': None,
                'parentUniqueId': None,
                'getInputValues': None,
                'isDeclaredListInput': False,
                'getPolicyValues': None,
                'propertyConstraints': None,
                'schemaType': None,
                'schemaProperty': None,
                'getInputProperty': False,
                'version': None,
                'ownerId': None,
                'empty': False
            },
            'getInputProperty': False,
            'version': None,
            'ownerId': 'cs0008',
            'empty': False
        },
        {
            'uniqueId': '9ee5fb23-4c4a-46bd-8682-68698559ee9c.controller_actor',
            'type': 'string',
            'required': False,
            'definition': False,
            'defaultValue': 'SO-REF-DATA',
            'description': None,
            'schema': None,
            'password': False,
            'name': 'controller_actor',
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': None,
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': '9ee5fb23-4c4a-46bd-8682-68698559ee9c',
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'constraints': None,
            'inputs': None,
            'properties': None,
            'schemaType': None,
            'schemaProperty': None,
            'getInputProperty': False,
            'version': None,
            'ownerId': '9ee5fb23-4c4a-46bd-8682-68698559ee9c',
            'empty': False
        },
        {
            'uniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079.lililili',
            'type': 'list',
            'required': False,
            'definition': False,
            'defaultValue': None,
            'description': None,
            'schema': {
                'derivedFrom': None,
                'constraints': None,
                'properties': None,
                'property': {
                    'uniqueId': None,
                    'type': 'abc',
                    'required': False,
                    'definition': False,
                    'defaultValue': None,
                    'description': None,
                    'schema': None,
                    'password': False,
                    'name': None,
                    'value': None,
                    'label': None,
                    'hidden': False,
                    'immutable': False,
                    'inputPath': None,
                    'status': None,
                    'inputId': None,
                    'instanceUniqueId': None,
                    'propertyId': None,
                    'parentPropertyType': None,
                    'subPropertyInputPath': None,
                    'annotations': None,
                    'parentUniqueId': None,
                    'getInputValues': None,
                    'isDeclaredListInput': False,
                    'getPolicyValues': None,
                    'propertyConstraints': None,
                    'schemaType': None,
                    'schemaProperty': None,
                    'getInputProperty': False,
                    'version': None,
                    'ownerId': None,
                    'empty': False
                },
                'version': None,
                'ownerId': None,
                'empty': False,
                'type': None
            },
            'password': False,
            'name': 'lililili',
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': None,
            'getInputValues': None,
            'isDeclaredListInput': True,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'constraints': None,
            'inputs': None,
            'properties': None,
            'schemaType': 'abc',
            'schemaProperty': {
                'uniqueId': None,
                'type': 'abc',
                'required': False,
                'definition': False,
                'defaultValue': None,
                'description': None,
                'schema': None,
                'password': False,
                'name': None,
                'value': None,
                'label': None,
                'hidden': False,
                'immutable': False,
                'inputPath': None,
                'status': None,
                'inputId': None,
                'instanceUniqueId': None,
                'propertyId': None,
                'parentPropertyType': None,
                'subPropertyInputPath': None,
                'annotations': None,
                'parentUniqueId': None,
                'getInputValues': None,
                'isDeclaredListInput': False,
                'getPolicyValues': None,
                'propertyConstraints': None,
                'schemaType': None,
                'schemaProperty': None,
                'getInputProperty': False,
                'version': None,
                'ownerId': None,
                'empty': False
            },
            'getInputProperty': False,
            'version': None,
            'ownerId': None,
            'empty': False
        }
    ]
}


PROPERTIES = {
    "properties": [{
        'uniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079.llllll',
        'type': 'integer',
        'required': False,
        'definition': False,
        'defaultValue': None,
        'description': None,
        'schema': {
            'derivedFrom': None,
            'constraints': None,
            'properties': None,
            'property': {
                'uniqueId': None,
                'type': '',
                'required': False,
                'definition': False,
                'defaultValue': None,
                'description': None,
                'schema': None,
                'password': False,
                'name': None,
                'value': None,
                'label': None,
                'hidden': False,
                'immutable': False,
                'inputPath': None,
                'status': None,
                'inputId': None,
                'instanceUniqueId': None,
                'propertyId': None,
                'parentPropertyType': None,
                'subPropertyInputPath': None,
                'annotations': None,
                'parentUniqueId': None,
                'getInputValues': None,
                'isDeclaredListInput': False,
                'getPolicyValues': None,
                'propertyConstraints': None,
                'schemaType': None,
                'schemaProperty': None,
                'getInputProperty': False,
                'version': None,
                'ownerId': None,
                'empty': False
            },
            'version': None,
            'ownerId': None,
            'empty': False,
            'type': None
        },
        'password': False,
        'name': 'llllll',
        'value': '{"get_input":["lililili","INDEX","llllll"]}',
        'label': None,
        'hidden': False,
        'immutable': False,
        'inputPath': None,
        'status': None,
        'inputId': None,
        'instanceUniqueId': None,
        'propertyId': None,
        'parentPropertyType': None,
        'subPropertyInputPath': None,
        'annotations': None,
        'parentUniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'getInputValues': [
            {
                'propName': None,
                'inputName': 'lililili',
                'inputId': '4a84415b-4580-4a78-aa33-501f0cd3d079.lililili',
                'indexValue': None,
                'getInputIndex': None,
                'list': False,
                'version': None,
                'ownerId': None,
                'empty': False,
                'type': None
            }
        ],
        'isDeclaredListInput': False,
        'getPolicyValues': None,
        'propertyConstraints': None,
        'constraints': None,
        'schemaType': '',
        'schemaProperty': {
            'uniqueId': None,
            'type': '',
            'required': False,
            'definition': False,
            'defaultValue': None,
            'description': None,
            'schema': None,
            'password': False,
            'name': None,
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': None,
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': None,
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'schemaType': None,
            'schemaProperty': None,
            'getInputProperty': False,
            'version': None,
            'ownerId': None,
            'empty': False
        },
        'getInputProperty': True,
        'version': None,
        'ownerId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'empty': False
    },
    {
        'uniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079.test',
        'type': 'string',
        'required': False,
        'definition': False,
        'defaultValue': None,
        'description': None,
        'schema': {
            'derivedFrom': None,
            'constraints': None,
            'properties': None,
            'property': {
                'uniqueId': None,
                'type': '',
                'required': False,
                'definition': False,
                'defaultValue': None,
                'description': None,
                'schema': None,
                'password': False,
                'name': None,
                'value': None,
                'label': None,
                'hidden': False,
                'immutable': False,
                'inputPath': None,
                'status': None,
                'inputId': None,
                'instanceUniqueId': None,
                'propertyId': None,
                'parentPropertyType': None,
                'subPropertyInputPath': None,
                'annotations': None,
                'parentUniqueId': None,
                'getInputValues': None,
                'isDeclaredListInput': False,
                'getPolicyValues': None,
                'propertyConstraints': None,
                'schemaType': None,
                'schemaProperty': None,
                'getInputProperty': False,
                'version': None,
                'ownerId': None,
                'empty': False
            },
            'version': None,
            'ownerId': None,
            'empty': False,
            'type': None
        },
        'password': False,
        'name': 'test',
        'value': None,
        'label': None,
        'hidden': False,
        'immutable': False,
        'inputPath': None,
        'status': None,
        'inputId': None,
        'instanceUniqueId': None,
        'propertyId': None,
        'parentPropertyType': None,
        'subPropertyInputPath': None,
        'annotations': None,
        'parentUniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'getInputValues': [],
        'isDeclaredListInput': False,
        'getPolicyValues': None,
        'propertyConstraints': None,
        'constraints': None,
        'schemaType': '',
        'schemaProperty': {
            'uniqueId': None,
            'type': '',
            'required': False,
            'definition': False,
            'defaultValue': None,
            'description': None,
            'schema': None,
            'password': False,
            'name': None,
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': None,
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': None,
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'schemaType': None,
            'schemaProperty': None,
            'getInputProperty': False,
            'version': None,
            'ownerId': None,
            'empty': False
        },
        'getInputProperty': True,
        'version': None,
        'ownerId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'empty': False
    },
    {
        'uniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079.yyy',
        'type': 'string',
        'required': False,
        'definition': False,
        'defaultValue': None,
        'description': None,
        'schema': {
            'derivedFrom': None,
            'constraints': None,
            'properties': None,
            'property': {
                'uniqueId': None,
                'type': '',
                'required': False,
                'definition': False,
                'defaultValue': None,
                'description': None,
                'schema': None,
                'password': False,
                'name': None,
                'value': None,
                'label': None,
                'hidden': False,
                'immutable': False,
                'inputPath': None,
                'status': None,
                'inputId': None,
                'instanceUniqueId': None,
                'propertyId': None,
                'parentPropertyType': None,
                'subPropertyInputPath': None,
                'annotations': None,
                'parentUniqueId': None,
                'getInputValues': None,
                'isDeclaredListInput': False,
                'getPolicyValues': None,
                'propertyConstraints': None,
                'schemaType': None,
                'schemaProperty': None,
                'getInputProperty': False,
                'version': None,
                'ownerId': None,
                'empty': False
            },
            'version': None,
            'ownerId': None,
            'empty': False,
            'type': None
        },
        'password': False,
        'name': 'yyy',
        'value': 'lalala',
        'label': None,
        'hidden': False,
        'immutable': False,
        'inputPath': None,
        'status': None,
        'inputId': None,
        'instanceUniqueId': None,
        'propertyId': None,
        'parentPropertyType': None,
        'subPropertyInputPath': None,
        'annotations': None,
        'parentUniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'getInputValues': None,
        'isDeclaredListInput': False,
        'getPolicyValues': None,
        'propertyConstraints': None,
        'constraints': None,
        'schemaType': '',
        'schemaProperty': {
            'uniqueId': None,
            'type': '',
            'required': False,
            'definition': False,
            'defaultValue': None,
            'description': None,
            'schema': None,
            'password': False,
            'name': None,
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': None,
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': None,
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'schemaType': None,
            'schemaProperty': None,
            'getInputProperty': False,
            'version': None,
            'ownerId': None,
            'empty': False
        },
        'getInputProperty': False,
        'version': None,
        'ownerId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'empty': False
    },
    {
        'uniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079.test2',
        'type': 'boolean',
        'required': False,
        'definition': False,
        'defaultValue': None,
        'description': 'test2',
        'schema': {
            'derivedFrom': None,
            'constraints': None,
            'properties': None,
            'property': {
                'uniqueId': None,
                'type': '',
                'required': False,
                'definition': False,
                'defaultValue': None,
                'description': None,
                'schema': None,
                'password': False,
                'name': None,
                'value': None,
                'label': None,
                'hidden': False,
                'immutable': False,
                'inputPath': None,
                'status': None,
                'inputId': None,
                'instanceUniqueId': None,
                'propertyId': None,
                'parentPropertyType': None,
                'subPropertyInputPath': None,
                'annotations': None,
                'parentUniqueId': None,
                'getInputValues': None,
                'isDeclaredListInput': False,
                'getPolicyValues': None,
                'propertyConstraints': None,
                'schemaType': None,
                'schemaProperty': None,
                'getInputProperty': False,
                'version': None,
                'ownerId': None,
                'empty': False
            },
            'version': None,
            'ownerId': None,
            'empty': False,
            'type': None
        },
        'password': False,
        'name': 'test2',
        'value': '{"get_input":"test2"}',
        'label': None,
        'hidden': False,
        'immutable': False,
        'inputPath': None,
        'status': None,
        'inputId': None,
        'instanceUniqueId': None,
        'propertyId': None,
        'parentPropertyType': None,
        'subPropertyInputPath': None,
        'annotations': None,
        'parentUniqueId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'getInputValues': [
            {
                'propName': None,
                'inputName': 'test2',
                'inputId': '4a84415b-4580-4a78-aa33-501f0cd3d079.test2',
                'indexValue': None,
                'getInputIndex': None,
                'list': False,
                'version': None,
                'ownerId': None,
                'empty': False,
                'type': None
            }
        ],
        'isDeclaredListInput': False,
        'getPolicyValues': None,
        'propertyConstraints': None,
        'constraints': None,
        'schemaType': '',
        'schemaProperty': {
            'uniqueId': None,
            'type': '',
            'required': False,
            'definition': False,
            'defaultValue': None,
            'description': None,
            'schema': None,
            'password': False,
            'name': None,
            'value': None,
            'label': None,
            'hidden': False,
            'immutable': False,
            'inputPath': None,
            'status': None,
            'inputId': None,
            'instanceUniqueId': None,
            'propertyId': None,
            'parentPropertyType': None,
            'subPropertyInputPath': None,
            'annotations': None,
            'parentUniqueId': None,
            'getInputValues': None,
            'isDeclaredListInput': False,
            'getPolicyValues': None,
            'propertyConstraints': None,
            'schemaType': None,
            'schemaProperty': None,
            'getInputProperty': False,
            'version': None,
            'ownerId': None,
            'empty': False
        },
        'getInputProperty': True,
        'version': None,
        'ownerId': '4a84415b-4580-4a78-aa33-501f0cd3d079',
        'empty': False
    }]
}


VL_PROPERTIES = {
    "properties": [{
        'uniqueId': 'd37cd65e-9842-4490-9343-a1a874e6b52a.network_role',
        'type': 'string',
        'required': False,
        'definition': False,
        'defaultValue': None,
        'description': 'Unique label that defines the role that this network performs. example: vce oam network, vnat sr-iov1 network\n',
        'schema': None,
        'password': False,
        'name': 'network_role',
        'value': None,
        'label': None,
        'hidden': False,
        'immutable': False,
        'inputPath': None,
        'status': None,
        'inputId': None,
        'instanceUniqueId': None,
        'propertyId': None,
        'parentPropertyType': None,
        'subPropertyInputPath': None,
        'annotations': None,
        'parentUniqueId': '1af9771b-0f79-4e98-8747-30fd06da85cb',
        'getInputValues': None,
        'isDeclaredListInput': False,
        'getPolicyValues': None,
        'propertyConstraints': None,
        'constraints': None,
        'schemaType': None,
        'schemaProperty': None,
        'getInputProperty': False,
        'version': None,
        'ownerId': '1af9771b-0f79-4e98-8747-30fd06da85cb',
        'empty': False
    }]
}


@mock.patch.object(Service, "send_message_json")
@mock.patch.object(Service, "send_message")
def test_service_properties(mock_send, mock_send_json):

    service = Service(name="test")
    service.unique_identifier = "toto"

    mock_send_json.return_value = {}
    assert len(list(service.properties)) == 0

    mock_send_json.return_value = PROPERTIES
    properties_list = list(service.properties)
    assert len(properties_list) == 4
    prop1, prop2, prop3, prop4 = properties_list

    mock_send_json.return_value = INPUTS

    assert prop1.sdc_resource == service
    assert prop1.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.llllll"
    assert prop1.name == "llllll"
    assert prop1.property_type == "integer"
    assert prop1.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop1.value == '{"get_input":["lililili","INDEX","llllll"]}'
    assert prop1.description is None
    assert prop1.get_input_values
    prop1_input = prop1.input
    assert prop1_input.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.lililili"
    assert prop1_input.input_type == "list"
    assert prop1_input.name == "lililili"
    assert prop1_input.default_value is None

    assert prop2.sdc_resource == service
    assert prop2.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.test"
    assert prop2.name == "test"
    assert prop2.property_type == "string"
    assert prop2.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop2.value is None
    assert prop2.description is None
    assert prop2.get_input_values == []
    assert prop2.input is None

    assert prop3.sdc_resource == service
    assert prop3.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.yyy"
    assert prop3.name == "yyy"
    assert prop3.property_type == "string"
    assert prop3.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop3.value == "lalala"
    assert prop3.description is None
    assert prop3.get_input_values is None
    assert prop3.input is None

    assert prop4.sdc_resource == service
    assert prop4.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.test2"
    assert prop4.name == "test2"
    assert prop4.property_type == "boolean"
    assert prop4.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop4.value == '{"get_input":"test2"}'
    assert prop4.description == "test2"
    assert prop4.get_input_values
    with pytest.raises(ParameterError):
        prop4.input


@mock.patch.object(Service, "send_message_json")
def test_service_inputs(mock_send_json):
    service = Service(name="test")
    service.unique_identifier = "toto"

    mock_send_json.return_value = {}
    assert len(list(service.inputs)) == 0

    mock_send_json.return_value = INPUTS
    inputs_list = list(service.inputs)
    assert len(inputs_list) == 4

    input1, input2, input3, input4 = inputs_list
    assert input1.unique_id == "9ee5fb23-4c4a-46bd-8682-68698559ee9c.skip_post_instantiation_configuration"
    assert input1.input_type == "boolean"
    assert input1.name == "skip_post_instantiation_configuration"
    assert input1.default_value == "true"

    assert input2.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.test"
    assert input2.input_type == "string"
    assert input2.name == "test"
    assert input2.default_value is None

    assert input3.unique_id == "9ee5fb23-4c4a-46bd-8682-68698559ee9c.controller_actor"
    assert input3.input_type == "string"
    assert input3.name == "controller_actor"
    assert input3.default_value == "SO-REF-DATA"

    assert input4.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.lililili"
    assert input4.input_type == "list"
    assert input4.name == "lililili"
    assert input4.default_value is None


@mock.patch.object(Vf, "send_message_json")
def test_vf_properties(mock_send_json):
    vf = Vf(name="test")
    vf.unique_identifier = "toto"

    mock_send_json.return_value = {}
    assert len(list(vf.properties)) == 0

    mock_send_json.return_value = PROPERTIES
    properties_list = list(vf.properties)
    assert len(properties_list) == 4
    prop1, prop2, prop3, prop4 = properties_list

    mock_send_json.return_value = INPUTS

    assert prop1.sdc_resource == vf
    assert prop1.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.llllll"
    assert prop1.name == "llllll"
    assert prop1.property_type == "integer"
    assert prop1.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop1.value == '{"get_input":["lililili","INDEX","llllll"]}'
    assert prop1.description is None
    assert prop1.get_input_values
    prop1_input = prop1.input
    assert prop1_input.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.lililili"
    assert prop1_input.input_type == "list"
    assert prop1_input.name == "lililili"
    assert prop1_input.default_value is None

    assert prop2.sdc_resource == vf
    assert prop2.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.test"
    assert prop2.name == "test"
    assert prop2.property_type == "string"
    assert prop2.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop2.value is None
    assert prop2.description is None
    assert prop2.get_input_values == []
    assert prop2.input is None

    assert prop3.sdc_resource == vf
    assert prop3.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.yyy"
    assert prop3.name == "yyy"
    assert prop3.property_type == "string"
    assert prop3.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop3.value == "lalala"
    assert prop3.description is None
    assert prop3.get_input_values is None
    assert prop3.input is None

    assert prop4.sdc_resource == vf
    assert prop4.unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079.test2"
    assert prop4.name == "test2"
    assert prop4.property_type == "boolean"
    assert prop4.parent_unique_id == "4a84415b-4580-4a78-aa33-501f0cd3d079"
    assert prop4.value == '{"get_input":"test2"}'
    assert prop4.description == "test2"
    assert prop4.get_input_values
    with pytest.raises(ParameterError):
        prop4.input


@mock.patch.object(Vl, "send_message_json")
@mock.patch.object(Vl, "exists")
def test_vl_properties(mock_exists, mock_send_json):
    mock_exists.return_value = True
    vl = Vl(name="test")
    vl.unique_identifier = "toto"

    mock_send_json.return_value = {}
    assert len(list(vl.properties)) == 0

    mock_send_json.return_value = VL_PROPERTIES
    properties_list = list(vl.properties)
    assert len(properties_list) == 1
    prop = properties_list[0]

    assert prop.sdc_resource == vl
    assert prop.unique_id == "d37cd65e-9842-4490-9343-a1a874e6b52a.network_role"
    assert prop.name == "network_role"
    assert prop.property_type == "string"
    assert prop.parent_unique_id == "1af9771b-0f79-4e98-8747-30fd06da85cb"
    assert prop.value is None
    assert prop.description == "Unique label that defines the role that this network performs. example: vce oam network, vnat sr-iov1 network\n"
    assert prop.get_input_values is None
    assert prop.input is None


@mock.patch.object(SdcResource, "send_message_json")
def test_sdc_resource_is_own_property(mock_send_json):
    sdc_resource = SdcResource(name="test")
    sdc_resource.unique_identifier = "toto"
    mock_send_json.return_value = PROPERTIES
    prop1 = Property(
        name="llllll",
        property_type="integer"
    )
    prop2 = Property(
        name="test2",
        property_type="string"
    )
    assert sdc_resource.is_own_property(prop1)
    assert not sdc_resource.is_own_property(prop2)

@mock.patch.object(SdcResource, "properties", new_callable=mock.PropertyMock)
@mock.patch.object(SdcResource, "send_message_json")
def test_sdc_resource_set_property_value(mock_send_message_json, mock_sdc_resource_properties):
    sdc_resource = SdcResource(name="test")
    sdc_resource.unique_identifier = "toto"

    mock_sdc_resource_properties.return_value = [
        Property(name="test",
                 property_type="string",
                 sdc_resource=sdc_resource)
    ]
    with pytest.raises(ParameterError):
        sdc_resource.set_property_value(Property(name="test2",
                                                 property_type="integer",
                                                 sdc_resource=sdc_resource),
                                        value="lalala")
    prop = sdc_resource.get_property(property_name="test")
    assert prop.name == "test"
    assert prop.property_type == "string"
    assert not prop.value

    prop.value = "test"
    mock_send_message_json.assert_called_once()
    assert prop.value == "test"

@mock.patch.object(SdcResource, "inputs", new_callable=mock.PropertyMock)
@mock.patch.object(SdcResource, "send_message_json")
def test_sdc_resource_input_default_value(mock_send_message_json, mock_inputs):
    sdc_resource = SdcResource(name="test")
    sdc_resource.unique_identifier = "toto"

    mock_inputs.return_value = [
        Input(unique_id="123",
              input_type="integer",
              name="test",
              sdc_resource=sdc_resource)
    ]
    assert sdc_resource.get_input("test")
    input_obj = sdc_resource.get_input("test")
    assert not input_obj.default_value
    input_obj.default_value = "123"
    mock_send_message_json.assert_called_once()
    assert input_obj.default_value == "123"
