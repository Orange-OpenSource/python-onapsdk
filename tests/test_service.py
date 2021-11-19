#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test Service module."""

from os import path
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, PropertyMock
import shutil

import oyaml as yaml
import pytest

import onapsdk.constants as const
from onapsdk.exceptions import ParameterError, RequestError, ResourceNotFound, StatusError, ValidationError
from onapsdk.sdc.category_management import ServiceCategory
from onapsdk.sdc.component import Component
from onapsdk.sdc.properties import ComponentProperty, Property
from onapsdk.sdc.service import Service, ServiceInstantiationType
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.utils.headers_creator import headers_sdc_operator
from onapsdk.utils.headers_creator import headers_sdc_creator


ARTIFACTS = {
    "componentInstances" : [
        {
            "uniqueId" : "test_unique_id",
            "componentName" : "ubuntu16test_VF 0"
        }
    ]
}


COMPONENTS = {
    "componentInstances":[
        {
            "actualComponentUid":"374f0a98-a280-43f1-9e6c-00b436782ce7",
            "createdFromCsar":True,
            "uniqueId":"bcfa7544-6e3d-4666-93b1-c5973356d069.374f0a98-a280-43f1-9e6c-00b436782ce7.abstract_vsn",
            "normalizedName":"abstract_vsn",
            "name":"abstract_vsn",
            "originType":"CVFC",
            "customizationUUID":"971043e1-495b-4b75-901e-3d09baed7521",
            "componentUid":"374f0a98-a280-43f1-9e6c-00b436782ce7",
            "componentVersion":"1.0",
            "toscaComponentName":"org.openecomp.resource.vfc.11111cvfc.abstract.abstract.nodes.vsn",
            "componentName":"11111-nodes.vsnCvfc",
            "groupInstances":None
        }
    ]
}


COMPONENT = {
    "metadata":{
        "uniqueId":"374f0a98-a280-43f1-9e6c-00b436782ce7",
        "name":"11111-nodes.vsnCvfc",
        "version":"1.0",
        "isHighestVersion":True,
        "creationDate":1594898496259,
        "lastUpdateDate":1594898496325,
        "description":"Complex node type that is used as nested type in VF",
        "lifecycleState":"CERTIFIED",
        "tags":[
            "11111-nodes.vsnCvfc"
        ],
        "icon":"defaulticon",
        "normalizedName":"11111nodesvsncvfc",
        "systemName":"11111NodesVsncvfc",
        "contactId":"cs0008",
        "allVersions":{
            "1.0":"374f0a98-a280-43f1-9e6c-00b436782ce7"
        },
        "isDeleted":None,
        "projectCode":None,
        "csarUUID":None,
        "csarVersion":None,
        "importedToscaChecksum":None,
        "invariantUUID":"3c027ba1-8d3a-4b59-9394-d748fec5e42c",
        "componentType":"RESOURCE",
        "name":"Generic",
        "normalizedName":"generic",
        "uniqueId":"resourceNewCategory.generic",
        "icons":None,
        "creatorUserId":"cs0008",
        "creatorFullName":"Carlos Santana",
        "lastUpdaterUserId":"cs0008",
        "lastUpdaterFullName":"Carlos Santana",
        "archiveTime":0,
        "vendorName":"mj",
        "vendorRelease":"1.0",
        "resourceVendorModelNumber":"",
        "resourceType":"CVFC",
        "isAbstract":None,
        "cost":None,
        "licenseType":None,
        "toscaResourceName":"org.openecomp.resource.vfc.11111cvfc.abstract.abstract.nodes.vsn",
        "derivedFrom":None,
        "uuid":"59f05bfb-ccea-4857-8799-6acff59e6344",
        "archived":False,
        "vspArchived":False,
        "groupInstances":None
    }
}


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


def test_init_no_name():
    """Check init with no names."""
    svc = Service()
    assert isinstance(svc, SdcResource)
    assert svc._identifier is None
    assert svc._version is None
    assert svc.name == "ONAP-test-Service"
    assert svc.headers["USER_ID"] == "cs0008"
    assert svc.distribution_status is None
    assert svc._distribution_id is None
    assert isinstance(svc._base_url(), str)

@mock.patch.object(Service, 'exists')
def test_init_with_name(mock_exists):
    """Check init with no names."""
    mock_exists.return_value = False
    svc = Service(name="YOLO")
    assert svc._identifier == None
    assert svc._version == None
    assert svc.name == "YOLO"
    assert svc.created() == False
    assert svc.headers["USER_ID"] == "cs0008"
    assert svc.distribution_status is None
    assert svc._distribution_id is None
    assert isinstance(svc._base_url(), str)

@mock.patch.object(Service, 'exists')
def test_init_with_sdc_values(mock_exists):
    """Check init with no names."""
    sdc_values = {'uuid': '12', 'version': '14', 'invariantUUID': '56',
                  'distributionStatus': 'yes', 'lifecycleState': 'state',
                  'category': 'Network Service'}
    svc = Service(sdc_values=sdc_values)
    mock_exists.return_value = True
    assert svc._identifier == "12"
    assert svc._version == "14"
    assert svc.name == "ONAP-test-Service"
    assert svc.created()
    assert svc.headers["USER_ID"] == "cs0008"
    assert svc.distribution_status == "yes"
    assert svc._distribution_id is None
    assert svc.category_name == "Network Service"
    assert isinstance(svc._base_url(), str)

@mock.patch.object(Service, 'get_all')
def test_version_filter(mock_get_all):
    """Check version filter"""
    svc_1 = Service(name="test_version_filter")
    svc_1.identifier = "1111"
    svc_1.unique_uuid = "2222"
    svc_1.unique_identifier = "3333"
    svc_1.status = const.CERTIFIED
    svc_1.version = "1.0"

    svc_2 = Service(name="test_version_filter")
    svc_2.identifier = "1111"
    svc_2.unique_uuid = "2222"
    svc_2.unique_identifier = "3333"
    svc_2.status = const.DRAFT
    svc_2.version = "1.1"

    mock_get_all.return_value = [svc_1, svc_2]

    svc = Service(name='test_version_filter')
    assert svc.exists()
    assert svc.version == "1.1"

    svc = Service(name='test_version_filter', version='1.0')
    assert svc.exists()
    assert svc.version == "1.0"

    svc = Service(name='test_version_filter', version='-111')
    assert not svc.exists()
    assert not svc.version

def test_equality_really_equals():
    """Check two vfs are equals if name is the same."""
    svc_1 = Service(name="equal")
    svc_1.identifier = "1234"
    svc_2 = Service(name="equal")
    svc_2.identifier = "1235"
    assert svc_1 == svc_2


def test_equality_not_equals():
    """Check two vfs are not equals if name is not the same."""
    svc_1 = Service(name="equal")
    svc_1.identifier = "1234"
    svc_2 = Service(name="not_equal")
    svc_2.identifier = "1234"
    assert svc_1 != svc_2


def test_equality_not_equals_not_same_object():
    """Check a vf and something different are not equals."""
    svc_1 = Service(name="equal")
    svc_1.identifier = "1234"
    svc_2 = SdcResource()
    svc_2.name = "equal"
    assert svc_1 != svc_2

@mock.patch.object(Service, 'load_metadata')
def test_distribution_id_no_load(mock_load):
    svc = Service()
    svc.identifier = "1234"
    svc._distribution_id = "4567"
    assert svc.distribution_id == "4567"
    mock_load.assert_not_called()

@mock.patch.object(Service, 'load_metadata')
def test_distribution_id_load(mock_load):
    svc = Service()
    svc.identifier = "1234"
    assert svc.distribution_id is None
    mock_load.assert_called_once()

@mock.patch.object(Service, '_check_distributed')
def test_distributed_no_load(mock_check_distributed):
    svc = Service()
    svc.identifier = "1234"
    svc._distributed = True
    assert svc.distributed
    mock_check_distributed.assert_not_called()

@mock.patch.object(Service, '_check_distributed')
def test_distributed_load(mock_check_distributed):
    svc = Service()
    svc.identifier = "1234"
    assert not svc.distributed
    mock_check_distributed.assert_called_once()

def test_distribution_id_setter():
    svc = Service()
    svc.identifier = "1234"
    svc.distribution_id = "4567"
    assert svc._distribution_id == "4567"

@mock.patch.object(Service, '_create')
@mock.patch.object(Service, "category", new_callable=mock.PropertyMock)
@mock.patch.object(Service, "exists")
def test_create(mock_exists, mock_category, mock_create):
    mock_exists.return_value = False

    svc = Service()
    svc.create()
    mock_create.assert_called_once_with("service_create.json.j2",
                                        name="ONAP-test-Service",
                                        instantiation_type="A-la-carte",
                                        category=svc.category)
    mock_create.reset_mock()
    svc = Service(instantiation_type=ServiceInstantiationType.MACRO)
    svc.create()
    mock_create.assert_called_once_with("service_create.json.j2",
                                        name="ONAP-test-Service",
                                        instantiation_type="Macro",
                                        category=svc.category)

@mock.patch.object(Service, 'exists')
@mock.patch.object(Service, 'send_message')
def test_add_resource_not_draft(mock_send, mock_exists):
    mock_exists.return_value = False
    svc = Service()
    resource = SdcResource()
    with pytest.raises(StatusError):
        svc.add_resource(resource)
    mock_send.assert_not_called()

@mock.patch.object(Service, 'load')
@mock.patch.object(Service, 'send_message')
def test_add_resource_bad_result(mock_send, mock_load):
    svc = Service()
    svc.unique_identifier = "45"
    svc.identifier = "93"
    svc.status = const.DRAFT
    mock_send.return_value = {}
    resource = SdcResource()
    resource.unique_identifier = "12"
    resource.created = MagicMock(return_value=True)
    resource.version = "40"
    resource.name = "test"
    assert svc.add_resource(resource) is None
    mock_send.assert_called_once_with(
        'POST', 'Add SDCRESOURCE to ServiceProxy',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/45/resourceInstance',
        data='{\n  "name": "test",\n  "componentVersion": "40",\n  "posY": 100,\n  "posX": 200,\n  "uniqueId": "12",\n  "originType": "SDCRESOURCE",\n  "componentUid": "12",\n  "icon": "defaulticon"\n}')

@mock.patch.object(Service, 'load')
@mock.patch.object(Service, 'send_message')
def test_add_resource_OK(mock_send, mock_load):
    svc = Service()
    svc.unique_identifier = "45"
    svc.identifier = "93"
    svc.status = const.DRAFT
    mock_send.return_value = {'yes': 'indeed'}
    resource = SdcResource()
    resource.unique_identifier = "12"
    resource.created = MagicMock(return_value=True)
    resource.version = "40"
    resource.name = "test"
    result = svc.add_resource(resource)
    assert result['yes'] == "indeed"
    mock_send.assert_called_once_with(
        'POST', 'Add SDCRESOURCE to ServiceProxy',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/45/resourceInstance',
        data='{\n  "name": "test",\n  "componentVersion": "40",\n  "posY": 100,\n  "posX": 200,\n  "uniqueId": "12",\n  "originType": "SDCRESOURCE",\n  "componentUid": "12",\n  "icon": "defaulticon"\n}')

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_checkin(mock_verify):
    svc = Service()
    svc.checkin()
    mock_verify.assert_called_once_with(const.DRAFT, const.CHECKIN, 'lifecycleState')

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_submit(mock_verify):
    svc = Service()
    svc.submit()
    mock_verify.assert_called_once_with(const.CHECKED_IN, const.SUBMIT_FOR_TESTING, 'lifecycleState')

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_certify(mock_verify):
    svc = Service()
    svc.certify()
    mock_verify.assert_called_once_with(
        const.CHECKED_IN, const.CERTIFY, 'lifecycleState',
        headers=headers_sdc_creator(svc.headers))

@mock.patch.object(Service, '_verify_action_to_sdc')
def test_distribute(mock_verify):
    svc = Service()
    svc.distribute()
    mock_verify.assert_called_once_with(
        const.CERTIFIED, const.DISTRIBUTE, 'distribution',
        headers=headers_sdc_creator(svc.headers))

@mock.patch.object(Service, 'send_message')
def test_get_tosca_no_result(mock_send):
    if path.exists('/tmp/tosca_files'):
        shutil.rmtree('/tmp/tosca_files')
    mock_send.return_value = {}
    svc = Service()
    svc.identifier = "12"
    svc.get_tosca()
    headers = headers_sdc_creator(svc.headers)
    headers['Accept'] = 'application/octet-stream'
    mock_send.assert_called_once_with(
        'GET', 'Download Tosca Model for ONAP-test-Service',
        'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/services/12/toscaModel',
        headers=headers)
    assert not path.exists('/tmp/tosca_files')


def test_get_tosca_bad_csart(requests_mock):
    if path.exists('/tmp/tosca_files'):
        shutil.rmtree('/tmp/tosca_files')
    svc = Service()
    svc.identifier = "12"
    with open('tests/data/bad.csar', mode='rb') as file:
        file_content = file.read()
        requests_mock.get(
            'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/services/12/toscaModel',
            content=file_content)
    svc.get_tosca()


def test_get_tosca_result(requests_mock):
    if path.exists('/tmp/tosca_files'):
        shutil.rmtree('/tmp/tosca_files')
    with open('tests/data/test.csar', mode='rb') as file:
        file_content = file.read()
        requests_mock.get(
            'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/services/12/toscaModel',
            content=file_content)
    svc = Service()
    svc.identifier = "12"
    svc.get_tosca()

def test_get_tosca_result_no_service_in_csar(requests_mock):
    if path.exists('/tmp/tosca_files'):
        shutil.rmtree('/tmp/tosca_files')
    with open('tests/data/bad_no_service.csar', mode='rb') as file:
        file_content = file.read()
        requests_mock.get(
            'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/services/12/toscaModel',
            content=file_content)
    svc = Service()
    svc.identifier = "12"
    with pytest.raises(ValidationError):
        svc.get_tosca()

@mock.patch.object(Service, 'send_message_json')
def test_distributed_api_error(mock_send):
    mock_send.side_effect = ResourceNotFound
    svc = Service()
    svc.distribution_id = "12"
    assert not svc.distributed

@mock.patch.object(Service, 'send_message_json')
def test_distributed_not_distributed(mock_send):
    mock_send.return_value = {
        'distributionStatusList':[
            {'omfComponentID': "SO", 'status': "DOWNLOAD_OK"},
            {'omfComponentID': "sdnc", 'status': "DOWNLOAD_NOK"},
            {'omfComponentID': "aai", 'status': "DOWNLOAD_OK"}]}
    svc = Service()
    svc.distribution_id = "12"
    assert not svc.distributed
    mock_send.assert_called_once_with(
        'GET', 'Check distribution for ONAP-test-Service',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/distribution/12',
        headers=headers_sdc_operator(svc.headers))

@mock.patch.object(Service, 'send_message_json')
def test_distributed_not_distributed(mock_send):
    mock_send.return_value = {
        'distributionStatusList':[
            {'omfComponentID': "SO", 'status': "DOWNLOAD_OK"},
            {'omfComponentID': "aai", 'status': "DOWNLOAD_OK"}]}
    svc = Service()
    svc.distribution_id = "12"
    assert not svc.distributed
    mock_send.assert_called_once_with(
        'GET', 'Check distribution for ONAP-test-Service',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/distribution/12',
        headers=headers_sdc_creator(svc.headers))

@mock.patch.object(Service, 'send_message_json')
def test_distributed_distributed(mock_send):
    mock_send.return_value = {
        'distributionStatusList':[
            {'omfComponentID': "SO", 'status': "DOWNLOAD_OK"},
            {'omfComponentID': "sdnc", 'status': "DOWNLOAD_OK"},
            {'omfComponentID': "aai", 'status': "DOWNLOAD_OK"}]}
    svc = Service()
    svc.distribution_id = "12"
    assert svc.distributed
    mock_send.assert_called_once_with(
        'GET', 'Check distribution for ONAP-test-Service',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/distribution/12',
        headers=headers_sdc_creator(svc.headers))

@mock.patch.object(Service, 'send_message_json')
def test_load_metadata_no_result(mock_send):
    mock_send.return_value = {}
    svc = Service()
    svc.identifier = "1"
    svc.load_metadata()
    assert svc._distribution_id is None
    mock_send.assert_called_once_with(
        'GET', 'Get Metadata for ONAP-test-Service',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/1/distribution',
        headers=headers_sdc_creator(svc.headers))

@mock.patch.object(Service, 'send_message_json')
def test_load_metadata_bad_json(mock_send):
    mock_send.return_value = {'yolo': 'in the wood'}
    svc = Service()
    svc.identifier = "1"
    svc.load_metadata()
    assert svc._distribution_id is None
    mock_send.assert_called_once_with(
        'GET', 'Get Metadata for ONAP-test-Service',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/1/distribution',
        headers=headers_sdc_creator(svc.headers))

@mock.patch.object(Service, 'send_message_json')
def test_load_metadata_OK(mock_send):
    mock_send.return_value = {'distributionStatusOfServiceList': [
        {'distributionID': "11"}, {'distributionID': "12"}]}
    svc = Service()
    svc.identifier = "1"
    svc.load_metadata()
    assert svc._distribution_id == "11"
    mock_send.assert_called_once_with(
        'GET', 'Get Metadata for ONAP-test-Service',
        'https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/1/distribution',
        headers=headers_sdc_creator(svc.headers))

def test_get_all_url():
    assert Service._get_all_url() == "https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/services"

@mock.patch.object(Service, '_action_to_sdc')
@mock.patch.object(Service, 'load')
def test_really_submit_request_failed(mock_load, mock_action):
    mock_action.side_effect = RequestError
    svc = Service()
    with pytest.raises(RequestError) as err:
        svc._really_submit()
    assert err.type == RequestError
    mock_load.assert_not_called()
    mock_action.assert_called_once_with('Certify', action_type='lifecycleState')

@mock.patch.object(Service, '_action_to_sdc')
@mock.patch.object(Service, 'load')
def test_really_submit_OK(mock_load, mock_action):
    mock_action.return_value = "yes"
    svc = Service()
    svc._really_submit()
    mock_load.assert_called_once()
    mock_action.assert_called_once_with('Certify', action_type='lifecycleState')

@mock.patch.object(Service, 'load')
@mock.patch.object(Service, '_action_to_sdc')
@mock.patch.object(Service, 'created')
def test_verify_action_to_sdc_not_created(mock_created, mock_action, mock_load):
    mock_created.return_value = False
    svc = Service()
    svc._status = "no_yes"
    svc._verify_action_to_sdc("yes", "action", action_type='lifecycleState')
    mock_created.assert_called()
    mock_action.assert_not_called()
    mock_load.assert_not_called()

@mock.patch.object(Service, 'load')
@mock.patch.object(Service, '_action_to_sdc')
@mock.patch.object(Service, 'created')
def test_verify_action_to_sdc_bad_status(mock_created, mock_action, mock_load):
    mock_created.return_value = True
    svc = Service()
    svc._status = "no_yes"
    with pytest.raises(StatusError) as err:
        svc._verify_action_to_sdc("yes", "action", action_type='lifecycleState')
    assert err.type == StatusError
    mock_created.assert_called()
    mock_action.assert_not_called()
    mock_load.assert_not_called()

@mock.patch.object(Service, 'load')
@mock.patch.object(Service, '_action_to_sdc')
@mock.patch.object(Service, 'created')
def test_verify_action_to_sdc_OK(mock_created, mock_action, mock_load):
    mock_created.return_value = True
    mock_action.return_value = "good"
    svc = Service()
    svc._status = "yes"
    svc._verify_action_to_sdc("yes", "action", action_type='lifecycleState')
    mock_created.assert_called()
    mock_action.assert_called_once()
    mock_load.assert_called_once()

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'approve')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'start_certification')
@mock.patch.object(Service, 'submit')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_new_service(mock_create, mock_add_resource,
                             mock_checkin, mock_submit,
                             mock_start_certification, mock_certify,
                             mock_approve, mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [None, const.DISTRIBUTED, const.DISTRIBUTED,
                                const.DISTRIBUTED, const.DISTRIBUTED,
                                const.DISTRIBUTED, const.DISTRIBUTED,
                                const.DISTRIBUTED, None]
        service = Service()
        service._time_wait = 0
        service.onboard()
        mock_create.assert_called_once()
        mock_add_resource.assert_not_called()
        mock_checkin.assert_not_called()
        mock_submit.assert_not_called()
        mock_start_certification.assert_not_called()
        mock_certify.assert_not_called()
        mock_approve.assert_not_called()
        mock_distribute.assert_not_called()

@mock.patch.object(Service, 'status')
def test_onboard_invalid_status(mock_status):
    mock_status.return_value = False
    service = Service()
    service._time_wait = 0
    with pytest.raises(StatusError) as err:
        service.onboard()
    assert err.type == StatusError

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'approve')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'start_certification')
@mock.patch.object(Service, 'submit')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_service_no_resources(mock_create,
                                      mock_add_resource, mock_checkin,
                                      mock_submit, mock_start_certification,
                                      mock_certify, mock_approve,
                                      mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, const.DISTRIBUTED,
                                const.DISTRIBUTED, const.DISTRIBUTED,
                                const.DISTRIBUTED, const.DISTRIBUTED,
                                const.DISTRIBUTED, const.DISTRIBUTED, None]
        service = Service()
        service._time_wait = 0
        with pytest.raises(ParameterError):
            service.onboard()
            mock_create.assert_not_called()
            mock_add_resource.assert_not_called()
            mock_checkin.assert_not_called()
            mock_submit.assert_not_called()
            mock_start_certification.assert_not_called()
            mock_certify.assert_not_called()
            mock_approve.assert_not_called()
            mock_distribute.assert_not_called()

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'approve')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'start_certification')
@mock.patch.object(Service, 'submit')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_service_resources(mock_create, mock_add_resource,
                                   mock_checkin, mock_submit,
                                   mock_start_certification, mock_certify,
                                   mock_approve, mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED, None]
        resource = SdcResource()
        service = Service(resources=[resource])
        service._time_wait = 0
        service.onboard()
        mock_create.assert_not_called()
        mock_add_resource.assert_called_once_with(resource)
        mock_checkin.assert_called_once()
        mock_submit.assert_not_called()
        mock_start_certification.assert_not_called()
        mock_certify.assert_not_called()
        mock_approve.assert_not_called()
        mock_distribute.assert_not_called()

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'approve')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'start_certification')
@mock.patch.object(Service, 'submit')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_service_several_resources(mock_create,
                                           mock_add_resource, mock_checkin,
                                           mock_submit,
                                           mock_start_certification,
                                           mock_certify, mock_approve,
                                           mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [const.DRAFT, const.DRAFT, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED, None]
        resource1 = SdcResource()
        resource2 = SdcResource()
        service = Service(resources=[resource1, resource2])
        service._time_wait = 0
        service.onboard()
        mock_create.assert_not_called()
        calls = [mock.call(resource1), mock.call(resource2)]
        mock_add_resource.assert_has_calls(calls, any_order=True)
        assert  mock_add_resource.call_count == 2
        mock_checkin.assert_called_once()
        mock_submit.assert_not_called()
        mock_start_certification.assert_not_called()
        mock_certify.assert_not_called()
        mock_approve.assert_not_called()
        mock_distribute.assert_not_called()

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'approve')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'start_certification')
@mock.patch.object(Service, 'submit')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_service_certifi(mock_create,
                                       mock_add_resource, mock_checkin,
                                       mock_submit, mock_start_certification,
                                       mock_certify, mock_approve,
                                       mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [const.CHECKED_IN,
                               const.CHECKED_IN,
                               const.CHECKED_IN,
                               const.CHECKED_IN,
                               const.CHECKED_IN,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, None]
        service = Service()
        service._time_wait = 0
        service.onboard()
        mock_create.assert_not_called()
        mock_add_resource.assert_not_called()
        mock_checkin.assert_not_called()
        mock_submit.assert_not_called()
        mock_start_certification.assert_not_called()
        mock_certify.assert_called_once()
        mock_approve.assert_not_called()
        mock_distribute.assert_not_called()

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_service_distribute(mock_create,
                                    mock_add_resource,
                                    mock_checkin,
                                    mock_certify,
                                    mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [const.CERTIFIED, const.CERTIFIED, const.CERTIFIED,
                               const.CERTIFIED, const.CERTIFIED, const.CERTIFIED,
                               const.CERTIFIED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED, None]
        service = Service()
        service._time_wait = 0
        service.onboard()
        mock_create.assert_not_called()
        mock_add_resource.assert_not_called()
        mock_checkin.assert_not_called()
        mock_certify.assert_not_called()
        mock_distribute.assert_called_once()

@mock.patch.object(Service, 'distribute')
@mock.patch.object(Service, 'certify')
@mock.patch.object(Service, 'checkin')
@mock.patch.object(Service, 'add_resource')
@mock.patch.object(Service, 'create')
def test_onboard_whole_service(mock_create,
                               mock_add_resource,
                               mock_checkin,
                               mock_certify,
                               mock_distribute):
    getter_mock = mock.Mock(wraps=Service.status.fget)
    mock_status = Service.status.getter(getter_mock)
    with mock.patch.object(Service, 'status', mock_status):
        getter_mock.side_effect = [None, const.DRAFT, const.DRAFT,const.CHECKED_IN,
                               const.CHECKED_IN, const.CHECKED_IN,
                               const.CERTIFIED, const.CERTIFIED,
                               const.CERTIFIED, const.CERTIFIED,
                               const.CERTIFIED, const.CERTIFIED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, const.DISTRIBUTED,
                               const.DISTRIBUTED, None]
        resource = SdcResource()
        service = Service(resources=[resource])
        service._time_wait = 0
        service.onboard()
        mock_create.assert_called_once()
        mock_add_resource.assert_called_once_with(resource)
        mock_checkin.assert_called_once()
        mock_certify.assert_called_once()
        mock_distribute.assert_called_once()

@mock.patch("onapsdk.sdc.service.Service.send_message_json")
@mock.patch("onapsdk.sdc.service.SdcResource.import_from_sdc")
@mock.patch("onapsdk.sdc.service.Service.resource_inputs_url", new_callable=mock.PropertyMock)
def test_vnf_vf_modules_one(mock_service_resource_inputs_url, mock_import_from_sdc, mock_send_message_json):
    """Test parsing TOSCA file with one VNF which has associated one VFmodule"""
    service = Service(name="test")
    mock_send_message_json.side_effect = [{
        "componentInstances": [{
            "actualComponentUid": "123",
            "originType": "VF",
            "name": "ubuntu16_VF 0",
            "toscaComponentName": "org.openecomp.resource.vf.Ubuntu16Vf",
            "createdFromCsar": False,
            "uniqueId": "123",
            "normalizedName": "123",
            "customizationUUID": "123",
            "componentUid": "123",
            "componentVersion": "123",
            "componentName": "123",
            "groupInstances": [
                {
                    "name": "ubuntu16_vf0..Ubuntu16Vf..base_ubuntu16..module-0",
                    "type": "org.openecomp.groups.VfModule",
                    "groupName": "Ubuntu16Vf..base_ubuntu16..module-0",
                    "groupUUID": "ed041b38-63fc-486d-9d4d-4e2531bc7e54",
                    "invariantUUID": "f47c3a9b-6a5f-4d1a-8a0b-b7f56ebb9a90",
                    "version": "1",
                    "customizationUUID": "d946ea06-ec4b-4ed2-921a-117e1379b913"
                }
            ]
        }]
    }, MagicMock()
    ]
    vnfs = list(service.vnfs)
    assert len(vnfs) == 1
    vnf = vnfs[0]
    assert vnf.name == "ubuntu16_VF 0"
    assert vnf.node_template_type == "org.openecomp.resource.vf.Ubuntu16Vf"
    assert vnf.vf_modules
    assert vnf.vf_modules[0].name == "ubuntu16_vf0..Ubuntu16Vf..base_ubuntu16..module-0"

@mock.patch("onapsdk.sdc.service.Service.send_message_json")
@mock.patch("onapsdk.sdc.service.SdcResource.import_from_sdc")
@mock.patch("onapsdk.sdc.service.Service.resource_inputs_url", new_callable=mock.PropertyMock)
def test_pnf_modules_one(mock_service_resource_inputs_url, mock_import_from_sdc, mock_send_message_json):
    """Test parsing TOSCA file with one PNF which has associated one PNFmodule"""
    service = Service(name="test")
    mock_send_message_json.side_effect = [{
        "componentInstances": [{
            "actualComponentUid": "123",
            "originType": "PNF",
            "name": "test_pnf_vsp 0",
            "toscaComponentName": "org.openecomp.resource.pnf.TestPnfVsp",
            "createdFromCsar": False,
            "uniqueId": "123",
            "normalizedName": "123",
            "customizationUUID": "123",
            "componentUid": "123",
            "componentVersion": "123",
            "componentName": "123",
            "groupInstances": None
        }]
    }, MagicMock()
    ]
    pnfs = list(service.pnfs)
    assert len(pnfs) == 1
    pnf = pnfs[0]
    assert pnf.name == "test_pnf_vsp 0"
    assert pnf.node_template_type == "org.openecomp.resource.pnf.TestPnfVsp"

@mock.patch("onapsdk.sdc.service.Service.send_message_json")
@mock.patch("onapsdk.sdc.service.SdcResource.import_from_sdc")
@mock.patch("onapsdk.sdc.service.Service.resource_inputs_url", new_callable=mock.PropertyMock)
def test_vnf_vf_modules_two(mock_service_resource_inputs_url, mock_import_from_sdc, mock_send_message_json):
    """Test parsing TOSCA file with two VNF which has associated one VFmodule"""
    service = Service(name="test")
    mock_send_message_json.side_effect = [{
        "componentInstances": [{
            "actualComponentUid": "123",
            "originType": "VF",
            "name": "vFWCL_vPKG-vf 0",
            "toscaComponentName": "org.openecomp.resource.vf.VfwclVpkgVf",
            "createdFromCsar": False,
            "uniqueId": "123",
            "normalizedName": "123",
            "customizationUUID": "123",
            "componentUid": "123",
            "componentVersion": "123",
            "componentName": "123",
            "groupInstances": [
                {
                    "name": "vfwcl_vpkgvf0..VfwclVpkgVf..base_vpkg..module-0",
                    "type": "org.openecomp.groups.VfModule",
                    "groupName": "Ubuntu16Vf..base_ubuntu16..module-0",
                    "groupUUID": "ed041b38-63fc-486d-9d4d-4e2531bc7e54",
                    "invariantUUID": "f47c3a9b-6a5f-4d1a-8a0b-b7f56ebb9a90",
                    "version": "1",
                    "customizationUUID": "d946ea06-ec4b-4ed2-921a-117e1379b913"
                }
            ]
        },
        {
            "actualComponentUid": "123",
            "originType": "VF",
            "name": "vFWCL_vFWSNK-vf 0",
            "toscaComponentName": "org.openecomp.resource.vf.VfwclVfwsnkVf",
            "createdFromCsar": False,
            "uniqueId": "123",
            "normalizedName": "123",
            "customizationUUID": "123",
            "componentUid": "123",
            "componentVersion": "123",
            "componentName": "123",
            "groupInstances": [
                {
                    "name": "vfwcl_vfwsnkvf0..VfwclVfwsnkVf..base_vfw..module-0",
                    "type": "org.openecomp.groups.VfModule",
                    "groupName": "Ubuntu16Vf..base_ubuntu16..module-0",
                    "groupUUID": "ed041b38-63fc-486d-9d4d-4e2531bc7e54",
                    "invariantUUID": "f47c3a9b-6a5f-4d1a-8a0b-b7f56ebb9a90",
                    "version": "1",
                    "customizationUUID": "d946ea06-ec4b-4ed2-921a-117e1379b913"
                }
            ]
        }]
    }, MagicMock(), MagicMock()
    ]
    vnfs = list(service.vnfs)
    assert len(vnfs) == 2
    vnf = vnfs[0]
    assert vnf.name == "vFWCL_vPKG-vf 0"
    assert vnf.node_template_type == "org.openecomp.resource.vf.VfwclVpkgVf"
    assert vnf.vf_modules
    assert vnf.vf_modules[0].name == "vfwcl_vpkgvf0..VfwclVpkgVf..base_vpkg..module-0"

    vnf = vnfs[1]
    assert vnf.name == "vFWCL_vFWSNK-vf 0"
    assert vnf.node_template_type == "org.openecomp.resource.vf.VfwclVfwsnkVf"
    assert vnf.vf_modules
    assert vnf.vf_modules[0].name == "vfwcl_vfwsnkvf0..VfwclVfwsnkVf..base_vfw..module-0"


@mock.patch.object(Service, 'send_message_json')
def test_get_vnf_unique_id(mock_send):
    """Test Service get nf uid with One Vf"""
    svc = Service()
    svc.unique_identifier = "service_unique_identifier"
    mock_send.return_value = ARTIFACTS
    unique_id = svc.get_nf_unique_id(nf_name="ubuntu16test_VF 0")
    mock_send.assert_called_once_with(
        'GET', 'Get nf unique ID',
        f"https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/{svc.unique_identifier}")
    assert unique_id == 'test_unique_id'

@mock.patch.object(Service, 'send_message_json')
def test_get_vnf_unique_id_not_found(mock_send):
    """Test Service get nf uid with One Vf"""
    svc = Service()
    svc.unique_identifier = "service_unique_identifier"
    artifacts = {"componentInstances": []}
    mock_send.return_value = artifacts
    with pytest.raises(ResourceNotFound) as err:
        svc.get_nf_unique_id(nf_name="ubuntu16test_VF 0")
    assert err.type == ResourceNotFound
    mock_send.assert_called_once_with(
        'GET', 'Get nf unique ID',
        f"https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/{svc.unique_identifier}")

@mock.patch.object(Service, 'get_nf_unique_id')
@mock.patch.object(Service, 'load')
@mock.patch.object(Service, 'send_message')
def test_add_artifact_to_vf(mock_send_message, mock_load, mock_add):
    """Test Service add artifact"""
    svc = Service()
    mock_add.return_value = "54321"
    result = svc.add_artifact_to_vf(vnf_name="ubuntu16test_VF 0",
                                    artifact_type="DCAE_INVENTORY_BLUEPRINT",
                                    artifact_name="clampnode.yaml",
                                    artifact="data".encode('utf-8'))
    mock_send_message.assert_called()
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "Add artifact to vf"
    assert url == ("https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/"
                    f"{svc.unique_identifier}/resourceInstance/54321/artifacts")

@mock.patch.object(Service, 'load')
@mock.patch.object(Service, 'send_message')
def test_add_artifact_to_service(mock_send_message, mock_load):
    """Test Service add artifact"""
    svc = Service()
    svc.status = const.DRAFT
    mycbapath = Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip")

    result = svc.add_deployment_artifact(artifact_label="cba",
                                         artifact_type="CONTROLLER_BLUEPRINT_ARCHIVE",
                                         artifact_name="vLB_CBA_Python.zip",
                                         artifact=mycbapath)
    mock_send_message.assert_called()
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "Add deployment artifact for ONAP-test-Service sdc resource"
    assert url == ("https://sdc.api.fe.simpledemo.onap.org:30207/sdc1/feProxy/rest/v1/catalog/services/"
                    f"{svc.unique_identifier}/artifacts")

@mock.patch("onapsdk.sdc.service.Service.send_message_json")
@mock.patch("onapsdk.sdc.service.SdcResource.import_from_sdc")
@mock.patch("onapsdk.sdc.service.Service.resource_inputs_url", new_callable=mock.PropertyMock)
def test_service_networks(mock_service_resource_inputs_url, mock_import_from_sdc, mock_send_message_json):
    mock_send_message_json.side_effect = [{
        "componentInstances": [{
            "actualComponentUid": "123",
            "originType": "VL",
            "name": "NeutronNet 0",
            "toscaComponentName": "org.openecomp.resource.vl.nodes.heat.network.neutron.Net",
            "createdFromCsar": False,
            "uniqueId": "123",
            "normalizedName": "123",
            "customizationUUID": "123",
            "componentUid": "123",
            "componentVersion": "123",
            "componentName": "123",
            "groupInstances": None
        }]
    }, MagicMock()
    ]

    service = Service(name="test")
    networks = list(service.networks)
    assert len(networks) == 1
    network = networks[0]
    assert network.name == "NeutronNet 0"
    assert network.node_template_type == "org.openecomp.resource.vl.nodes.heat.network.neutron.Net"

@mock.patch.object(Service, '_unzip_csar_file')
def test_tosca_template_no_tosca_model(mock_unzip):
    service = Service(name="test")
    getter_mock = mock.Mock(wraps=Service.tosca_model.fget)
    getter_mock.return_value = False
    mock_tosca_model = Service.tosca_model.getter(getter_mock)
    with mock.patch.object(Service, 'tosca_model', mock_tosca_model):
        service.tosca_template
        mock_unzip.assert_not_called()

@mock.patch.object(Service, '_unzip_csar_file')
def test_tosca_template_tosca_model(mock_unzip):
    service = Service(name="test")
    service._tosca_model = str.encode("test")
    service.tosca_template
    mock_unzip.assert_called_once_with(mock.ANY, mock.ANY)

@mock.patch.object(Service, '_unzip_csar_file')
def test_tosca_template_present(mock_unzip):
    service = Service(name="test")
    service._tosca_template = "test"
    assert service.tosca_template == "test"
    mock_unzip.assert_not_called()

@mock.patch.object(Service, 'send_message')
def test_tosca_model(mock_send):
    service = Service(name="test")
    service.identifier = "toto"
    service.tosca_model
    mock_send.assert_called_once_with("GET", "Download Tosca Model for test",
                                      "https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/services/toto/toscaModel",
                                      headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream', 'USER_ID': 'cs0008', 'Authorization': 'Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=', 'X-ECOMP-InstanceID': 'onapsdk'})

@mock.patch.object(Service, "send_message_json")
def test_add_properties(mock_send_message_json):
    service = Service(name="test")
    service._identifier = "toto"
    service._unique_identifier = "toto"
    service._status = const.CERTIFIED
    with pytest.raises(StatusError):
        service.add_property(Property(name="test", property_type="string"))
    service._status = const.DRAFT
    service.add_property(Property(name="test", property_type="string"))
    mock_send_message_json.assert_called_once()

@mock.patch.object(Service, "send_message_json")
def test_service_components(mock_send_message_json):
    service = Service(name="test")
    service.unique_identifier = "toto"

    mock_send_message_json.return_value = {}
    assert len(list(service.components)) == 0

    mock_send_message_json.reset_mock()
    mock_send_message_json.side_effect = [COMPONENTS, COMPONENT]
    components = list(service.components)
    assert len(components) == 1
    assert mock_send_message_json.call_count == 2
    component = components[0]
    assert component.actual_component_uid == "374f0a98-a280-43f1-9e6c-00b436782ce7"
    assert component.sdc_resource.unique_uuid == "3c027ba1-8d3a-4b59-9394-d748fec5e42c"

def test_component_properties():
    sdc_resource = mock.MagicMock()
    service = Service(name="test")
    service.unique_identifier = "toto"

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
            parent_sdc_resource=service,
            group_instances=None
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
    service = Service(name="test")
    service.unique_identifier = "toto"
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
            parent_sdc_resource=service,
            group_instances=None
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

@mock.patch.object(Service, "add_resource")
@mock.patch.object(Service, "add_property")
@mock.patch.object(Service, "declare_input")
def test_declare_resources_and_properties(mock_declare_input, mock_add_property, mock_add_resource):

    service = Service(name="test",
                      resources=[SdcResource()],
                      properties=[Property(name="test", property_type="string")],
                      inputs=[Property(name="test", property_type="string")])
    service.declare_resources_and_properties()
    mock_add_resource.assert_called_once()
    mock_add_property.assert_called_once()
    mock_declare_input.assert_called_once()

@mock.patch.object(Service, "created")
@mock.patch.object(ServiceCategory, "get")
def test_service_category(mock_resource_category, mock_created):
    mock_created.return_value = False
    service = Service(name="test")
    _ = service.category
    mock_resource_category.assert_called_once_with(name="Network Service")
    mock_resource_category.reset_mock()

    service = Service(name="test", category="test")
    _ = service.category
    mock_resource_category.assert_called_once_with(name="test")
    mock_resource_category.reset_mock()

    mock_created.return_value = True
    _ = service.category
    mock_resource_category.assert_called_once_with(name="test")

def test_service_origin_type():
    service = Service(name="test")
    assert service.origin_type == "ServiceProxy"

@mock.patch.object(Service, "unique_identifier", new_callable=PropertyMock)
def test_service_metadata_url(mock_uniquie_identifier):
    mock_uniquie_identifier.return_value = "1233"
    service = Service(name="test")
    assert service.metadata_url == f"{service._base_create_url()}/services/1233/filteredDataByParams?include=metadata"


@mock.patch.object(Service, "created")
@mock.patch.object(Service, "send_message_json")
@mock.patch.object(Service, "metadata_url", new_callable=PropertyMock)
def test_service_instantiation_type(mock_metadata_url, mock_send_message_json, mock_created):
    mock_created.return_value = False
    service = Service(name="test")
    assert service.instantiation_type == ServiceInstantiationType.A_LA_CARTE

    service = Service(name="test", instantiation_type=ServiceInstantiationType.MACRO)
    assert service.instantiation_type == ServiceInstantiationType.MACRO

    mock_created.return_value = True
    mock_send_message_json.return_value = {"metadata": {"instantiationType": "A-la-carte"}}
    service = Service(name="test")
    assert service.instantiation_type == ServiceInstantiationType.A_LA_CARTE

    mock_send_message_json.return_value = {"metadata": {"instantiationType": "Macro"}}
    service = Service(name="test")
    assert service.instantiation_type == ServiceInstantiationType.MACRO


@mock.patch.object(Service, "get_all")
def test_service_get_by_unique_uuid(mock_get_all):
    mock_get_all.return_value = []
    with pytest.raises(ResourceNotFound):
        Service.get_by_unique_uuid("test")
    mock_service = MagicMock()
    mock_service.unique_uuid = "test"
    mock_get_all.return_value = [mock_service]
    Service.get_by_unique_uuid("test")
