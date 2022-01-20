import json
import oyaml as yaml
from collections import namedtuple
from pathlib import Path
from unittest import mock

import pytest

from onapsdk.exceptions import APIError, InvalidResponse, ResourceNotFound, StatusError
from onapsdk.sdc.service import Service
from onapsdk.sdnc import NetworkPreload, VfModulePreload
from onapsdk.so.instantiation import (
    NetworkInstantiation,
    ServiceInstantiation,
    SoService,
    SoServicePnf,
    SoServiceVfModule,
    SoServiceVnf,
    VfModuleInstantiation,
    VnfInstantiation
)
from onapsdk.vid import Vid
from onapsdk.aai.business.owning_entity import OwningEntity

@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_ala_carte_instantiation(mock_service_instantiation_send_message):
    mock_sdc_service = mock.MagicMock()
    mock_sdc_service.distributed = False
    with pytest.raises(StatusError):
        ServiceInstantiation.\
            instantiate_ala_carte(sdc_service=mock_sdc_service,
                                  cloud_region=mock.MagicMock(),
                                  tenant=mock.MagicMock(),
                                  customer=mock.MagicMock(),
                                  owning_entity=mock.MagicMock(),
                                  project=mock.MagicMock(),
                                  service_instance_name="test",
                                  service_subscription=mock.MagicMock())
    mock_sdc_service.distributed = True
    service_instance = ServiceInstantiation.\
            instantiate_ala_carte(sdc_service=mock_sdc_service,
                                  cloud_region=mock.MagicMock(),
                                  tenant=mock.MagicMock(),
                                  customer=mock.MagicMock(),
                                  owning_entity=mock.MagicMock(),
                                  project=mock.MagicMock(),
                                  service_instance_name="test",
                                  service_subscription=mock.MagicMock())
    assert service_instance.name == "test"

    service_instance = ServiceInstantiation.\
            instantiate_ala_carte(sdc_service=mock_sdc_service,
                                  cloud_region=mock.MagicMock(),
                                  tenant=mock.MagicMock(),
                                  customer=mock.MagicMock(),
                                  owning_entity=mock.MagicMock(),
                                  project=mock.MagicMock(),
                                  service_subscription=mock.MagicMock())
    assert service_instance.name.startswith("Python_ONAP_SDK_service_instance_")
    mock_service_instantiation_send_message.assert_called()
    method, _, url = mock_service_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{ServiceInstantiation.base_url}/onap/so/infra/"
                   f"serviceInstantiation/{ServiceInstantiation.api_version}/serviceInstances")


@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_macro_instantiation(mock_service_instantiation_send_message):
    mock_sdc_service = mock.MagicMock()
    mock_sdc_service.distributed = False
    with pytest.raises(StatusError):
        ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              project=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              service_instance_name="test",
                              service_subscription=mock.MagicMock())
    mock_sdc_service.distributed = True
    service_instance = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              project=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              service_instance_name="test",
                              service_subscription=mock.MagicMock())
    assert service_instance.name == "test"

    service_instance = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              project=mock.MagicMock(),
                              so_service=mock.MagicMock())
    assert service_instance.name.startswith("Python_ONAP_SDK_service_instance_")
    mock_service_instantiation_send_message.assert_called()
    method, _, url = mock_service_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{ServiceInstantiation.base_url}/onap/so/infra/"
                   f"serviceInstantiation/{ServiceInstantiation.api_version}/serviceInstances")

    so_service_mock = mock.MagicMock()
    so_service_mock.instance_name = "SoServiceInstanceName"
    service_instance = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              project=mock.MagicMock(),
                              so_service=so_service_mock)
    assert service_instance.name == "SoServiceInstanceName"
    mock_service_instantiation_send_message.assert_called()
    method, _, url = mock_service_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{ServiceInstantiation.base_url}/onap/so/infra/"
                   f"serviceInstantiation/{ServiceInstantiation.api_version}/serviceInstances")


def test_service_instance_aai_service_instance():
    customer_mock = mock.MagicMock()
    service_instantiation = ServiceInstantiation(name="test",
                                                request_id="test_request_id",
                                                instance_id="test_instance_id",
                                                sdc_service=mock.MagicMock(),
                                                cloud_region=mock.MagicMock(),
                                                tenant=mock.MagicMock(),
                                                customer=customer_mock,
                                                owning_entity=mock.MagicMock(),
                                                project=mock.MagicMock())
    status_mock = mock.PropertyMock(return_value=ServiceInstantiation.StatusEnum.IN_PROGRESS)
    type(service_instantiation).status = status_mock
    with pytest.raises(StatusError):
        service_instantiation.aai_service_instance

    status_mock.return_value = return_value=ServiceInstantiation.StatusEnum.COMPLETED
    assert service_instantiation.aai_service_instance is not None

    customer_mock.get_service_subscription_by_service_type.side_effect = APIError
    with pytest.raises(APIError) as err:
        service_instantiation.aai_service_instance
    assert err.type == APIError


@mock.patch.object(VnfInstantiation, "send_message_json")
def test_vnf_instantiation(mock_vnf_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = VnfInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              vnf_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              sdc_service=mock.MagicMock())
    assert vnf_instantiation.name.startswith("Python_ONAP_SDK_vnf_instance_")
    mock_vnf_instantiation_send_message.assert_called_once()
    method, _, url = mock_vnf_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{VnfInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{VnfInstantiation.api_version}/serviceInstances/"
                   f"{aai_service_instance_mock.instance_id}/vnfs")

    vnf_instantiation = VnfInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              vnf_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              vnf_instance_name="test",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              sdc_service=mock.MagicMock())
    assert vnf_instantiation.name == "test"


@mock.patch.object(VnfInstantiation, "send_message_json")
def test_vnf_instantiation_with_cr_and_tenant(mock_vnf_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = VnfInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              vnf_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              sdc_service=mock.MagicMock())
    assert vnf_instantiation.name.startswith("Python_ONAP_SDK_vnf_instance_")
    mock_vnf_instantiation_send_message.assert_called_once()
    method, _, url = mock_vnf_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{VnfInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{VnfInstantiation.api_version}/serviceInstances/"
                   f"{aai_service_instance_mock.instance_id}/vnfs")

    vnf_instantiation = VnfInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              vnf_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              vnf_instance_name="test",
                              sdc_service=mock.MagicMock())
    assert vnf_instantiation.name == "test"


@mock.patch.object(VnfInstantiation, "send_message_json")
@mock.patch.object(OwningEntity, "get_by_owning_entity_id")
def test_vnf_instantiation_macro(mock_owning_entity_get, mock_vnf_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"

    relation_1 = mock.MagicMock()
    relation_1.related_to = "owning-entity"
    relation_1.relationship_data = [{"relationship-value": "test"}]
    relation_2 = mock.MagicMock()
    relation_2.related_to = "project"
    relation_2.relationship_data = [{"relationship-value": "test"}]

    aai_service_instance_mock.relationships = (item for item in [relation_1, relation_2])

    vnf_instantiation = VnfInstantiation.\
        instantiate_macro(aai_service_instance=aai_service_instance_mock,
                          vnf_object=mock.MagicMock(),
                          line_of_business="test_lob",
                          platform="test_platform",
                          cloud_region=mock.MagicMock(),
                          tenant=mock.MagicMock(),
                          sdc_service=mock.MagicMock())
    assert vnf_instantiation.name.startswith("Python_ONAP_SDK_vnf_instance_")
    mock_vnf_instantiation_send_message.assert_called_once()
    method, _, url = mock_vnf_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{VnfInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{VnfInstantiation.api_version}/serviceInstances/"
                   f"{aai_service_instance_mock.instance_id}/vnfs")

    vnf_instantiation = VnfInstantiation. \
        instantiate_macro(aai_service_instance=aai_service_instance_mock,
                          vnf_object=mock.MagicMock(),
                          line_of_business="test_lob",
                          platform="test_platform",
                          vnf_instance_name="test",
                          cloud_region=mock.MagicMock(),
                          tenant=mock.MagicMock(),
                          sdc_service=mock.MagicMock())
    assert vnf_instantiation.name == "test"

    vnf_instantiation = VnfInstantiation. \
        instantiate_macro(aai_service_instance=aai_service_instance_mock,
                          vnf_object=mock.MagicMock(),
                          line_of_business="test_lob",
                          platform="test_platform",
                          cloud_region=mock.MagicMock(),
                          tenant=mock.MagicMock(),
                          sdc_service=mock.MagicMock(),
                          so_vnf=mock.MagicMock())
    assert vnf_instantiation.name.startswith("Python_ONAP_SDK_service_instance_")

    so_vnf_mock = mock.MagicMock()
    so_vnf_mock.instance_name = "SoVnfInstanceName"
    vnf_instantiation = VnfInstantiation. \
        instantiate_macro(aai_service_instance=aai_service_instance_mock,
                          vnf_object=mock.MagicMock(),
                          line_of_business="test_lob",
                          platform="test_platform",
                          cloud_region=mock.MagicMock(),
                          tenant=mock.MagicMock(),
                          sdc_service=mock.MagicMock(),
                          so_vnf=so_vnf_mock)
    assert vnf_instantiation.name == "SoVnfInstanceName"


@mock.patch.object(NetworkInstantiation, "send_message_json")
@mock.patch.object(NetworkPreload, "send_message_json")
def test_network_instantiation(mock_network_preload, mock_network_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = NetworkInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              network_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
    mock_network_preload.assert_called_once()
    assert vnf_instantiation.name.startswith("Python_ONAP_SDK_network_instance_")
    mock_network_instantiation_send_message.assert_called_once()
    method, _, url = mock_network_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{NetworkInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{NetworkInstantiation.api_version}/serviceInstances/"
                   f"{aai_service_instance_mock.instance_id}/networks")

    network_instantiation = NetworkInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              network_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              network_instance_name="test",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
    assert mock_network_preload.call_count == 2
    assert network_instantiation.name == "test"


@mock.patch.object(NetworkInstantiation, "send_message_json")
@mock.patch.object(NetworkPreload, "send_message_json")
def test_network_instantiation_with_cr_and_tenant(mock_network_preload, mock_network_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = NetworkInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              network_object=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
    mock_network_preload.assert_called_once()
    assert vnf_instantiation.name.startswith("Python_ONAP_SDK_network_instance_")
    mock_network_instantiation_send_message.assert_called_once()
    method, _, url = mock_network_instantiation_send_message.call_args[0]
    assert method == "POST"
    assert url == (f"{NetworkInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{NetworkInstantiation.api_version}/serviceInstances/"
                   f"{aai_service_instance_mock.instance_id}/networks")

    network_instantiation = NetworkInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              network_object=mock.MagicMock(),
                              line_of_business="test_lob",
                              platform="test_platform",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              network_instance_name="test")
    assert mock_network_preload.call_count == 2
    assert network_instantiation.name == "test"

@mock.patch.object(Vid, "send_message")
@mock.patch.object(VnfInstantiation, "send_message_json")
@mock.patch("onapsdk.so.instantiation.SdcService")
def test_vnf_instantiation_get_by_vnf_instance_name(mock_sdc_service, mock_send_message_json, mock_send):
    mock_sdc_service.return_value.vnfs = []
    mock_send_message_json.return_value = {}
    with pytest.raises(InvalidResponse):
        VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name")
    mock_send_message_json.return_value = {
        "requestList": [
            {
                "request": {
                    "requestScope": "not_vnf"
                }
            }
        ]
    }
    with pytest.raises(InvalidResponse):
        VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name")
    mock_send_message_json.return_value = {
        "requestList": [
            {
                "request": {
                    "requestScope": "vnf",
                    "requestType": "updateInstance"
                }
            }
        ]
    }
    with pytest.raises(InvalidResponse):
        VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name")
    mock_send_message_json.return_value = {
        "requestList": [
            {
                "request": {
                    "requestScope": "vnf",
                    "requestType": "createInstance"
                }
            }
        ]
    }
    with pytest.raises(ResourceNotFound):
        VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name")
    mock_send_message_json.return_value = {
        "requestList": [
            {
                "request": {
                    "requestScope": "vnf",
                    "requestType": "createInstance",
                    "requestDetails": {
                        "relatedInstanceList": [
                            {
                                "relatedInstance": {
                                    "modelInfo": {
                                        "modelType": "service",
                                        "modelName": "test_service"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
    with pytest.raises(ResourceNotFound):
        VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name")
    mock_vnf = mock.MagicMock()
    mock_vnf.name = "test_vnf_name"
    mock_sdc_service.return_value.vnfs = [mock_vnf]
    mock_send_message_json.return_value = {
        "requestList": [
            {
                "request": {
                    "requestScope": "vnf",
                    "requestType": "createInstance",
                    "requestDetails": {
                        "modelInfo": {
                            "modelCustomizationName": "test_fail_vnf_name"
                        },
                        "relatedInstanceList": [
                            {
                                "relatedInstance": {
                                    "modelInfo": {
                                        "modelType": "service",
                                        "modelName": "test_service",
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
    with pytest.raises(ResourceNotFound):
        VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name")
    mock_sdc_service.return_value.vnfs = [mock_vnf]
    mock_send_message_json.return_value = {
        "requestList": [
            {
                "request": {
                    "requestScope": "vnf",
                    "requestType": "createInstance",
                    "requestDetails": {
                        "modelInfo": {
                            "modelCustomizationName": "test_vnf_name"
                        },
                        "relatedInstanceList": [
                            {
                                "relatedInstance": {
                                    "modelInfo": {
                                        "modelType": "service",
                                        "modelName": "test_service"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
    assert VnfInstantiation.get_by_vnf_instance_name("test_vnf_instance_name") is not None


@mock.patch.object(VfModuleInstantiation, "send_message_json")
@mock.patch.object(VfModulePreload, "upload_vf_module_preload")
def test_vf_module_instantiation(mock_vf_module_preload, mock_send_message_json):
    mock_service_instance = mock.MagicMock()
    mock_service_instance.instance_id = "1234"
    mock_vnf_instance = mock.MagicMock()
    mock_vnf_instance.service_instance = mock_service_instance
    mock_vnf_instance.vnf_id = "4321"
    instantiation = VfModuleInstantiation.\
        instantiate_ala_carte(vf_module=mock.MagicMock(),
                              vnf_instance=mock_vnf_instance,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
    assert instantiation.name.startswith("Python_ONAP_SDK_vf_module_instance_")
    mock_send_message_json.assert_called_once()
    method, _, url = mock_send_message_json.call_args[0]
    assert method == "POST"
    assert url == (f"{VfModuleInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{VfModuleInstantiation.api_version}/serviceInstances/1234/vnfs/"
                   f"4321/vfModules")

    instantiation = VfModuleInstantiation.\
        instantiate_ala_carte(vf_module=mock.MagicMock(),
                              vnf_instance=mock_vnf_instance,
                              vf_module_instance_name="test",
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
    assert instantiation.name == "test"


@mock.patch.object(VfModuleInstantiation, "send_message_json")
@mock.patch.object(VfModulePreload, "upload_vf_module_preload")
def test_vf_module_instantiation_with_cr_and_tenant(mock_vf_module_preload, mock_send_message_json):
    mock_service_instance = mock.MagicMock()
    mock_service_instance.instance_id = "1234"
    mock_vnf_instance = mock.MagicMock()
    mock_vnf_instance.service_instance = mock_service_instance
    mock_vnf_instance.vnf_id = "4321"
    instantiation = VfModuleInstantiation.\
        instantiate_ala_carte(vf_module=mock.MagicMock(),
                              vnf_instance=mock_vnf_instance,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
    assert instantiation.name.startswith("Python_ONAP_SDK_vf_module_instance_")
    mock_send_message_json.assert_called_once()
    method, _, url = mock_send_message_json.call_args[0]
    assert method == "POST"
    assert url == (f"{VfModuleInstantiation.base_url}/onap/so/infra/serviceInstantiation/"
                   f"{VfModuleInstantiation.api_version}/serviceInstances/1234/vnfs/"
                   f"4321/vfModules")

    instantiation = VfModuleInstantiation.\
        instantiate_ala_carte(vf_module=mock.MagicMock(),
                              vnf_instance=mock_vnf_instance,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              vf_module_instance_name="test")
    assert instantiation.name == "test"


def test_instantiation_wait_for_finish():
    with mock.patch.object(ServiceInstantiation, "finished", new_callable=mock.PropertyMock) as mock_finished:
        with mock.patch.object(ServiceInstantiation, "completed", new_callable=mock.PropertyMock) as mock_completed:
            instantiation = ServiceInstantiation(
                name="test",
                request_id="test",
                instance_id="test",
                sdc_service=mock.MagicMock(),
                cloud_region=mock.MagicMock(),
                tenant=mock.MagicMock(),
                customer=mock.MagicMock(),
                owning_entity=mock.MagicMock(),
                project=mock.MagicMock()
            )
            instantiation.WAIT_FOR_SLEEP_TIME = 0
            mock_finished.side_effect = [False, False, True]
            mock_completed.return_value = True
            rv = namedtuple("Value", ["return_value"])
            instantiation._wait_for_finish(rv)
            assert rv.return_value

@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_instantiation_multicloud(mock_send_message_json):

    mock_sdc_service = mock.MagicMock()
    mock_sdc_service.distributed = True
    _ = ServiceInstantiation.\
            instantiate_ala_carte(sdc_service=mock_sdc_service,
                                  cloud_region=mock.MagicMock(),
                                  tenant=mock.MagicMock(),
                                  customer=mock.MagicMock(),
                                  owning_entity=mock.MagicMock(),
                                  project=mock.MagicMock(),
                                  service_subscription=mock.MagicMock())
    _, kwargs = mock_send_message_json.call_args
    data = json.loads(kwargs["data"])
    assert data["requestDetails"]["requestParameters"]["userParams"] == []
    mock_send_message_json.reset_mock()

    _ = ServiceInstantiation.\
            instantiate_ala_carte(sdc_service=mock_sdc_service,
                                  cloud_region=mock.MagicMock(),
                                  tenant=mock.MagicMock(),
                                  customer=mock.MagicMock(),
                                  owning_entity=mock.MagicMock(),
                                  project=mock.MagicMock(),
                                  enable_multicloud=True,
                                  service_subscription=mock.MagicMock())
    _, kwargs = mock_send_message_json.call_args
    data = json.loads(kwargs["data"])
    assert data["requestDetails"]["requestParameters"]["userParams"] == [{"name": "orchestrator", "value": "multicloud"}]
    mock_send_message_json.reset_mock()

    _ = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              project=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              service_instance_name="test",
                              service_subscription=mock.MagicMock())
    _, kwargs = mock_send_message_json.call_args
    data = json.loads(kwargs["data"])
    assert not any(filter(lambda x: x == {"name": "orchestrator", "value": "multicloud"}, data["requestDetails"]["requestParameters"]["userParams"]))
    mock_send_message_json.reset_mock()

    _ = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              project=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              service_instance_name="test",
                              enable_multicloud=True,
                              service_subscription=mock.MagicMock())
    _, kwargs = mock_send_message_json.call_args
    data = json.loads(kwargs["data"])
    assert any(filter(lambda x: x == {"name": "orchestrator", "value": "multicloud"}, data["requestDetails"]["requestParameters"]["userParams"]))


@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_instantiation_so_service(mock_send_message_json):
    mock_sdc_service = mock.MagicMock()
    mock_sdc_service.distributed = True

    so_service = SoService(
        subscription_service_type="test_so_service",
        vnfs=[
            SoServiceVnf(
                model_name="test_so_service_vnf_model_name_1",
                instance_name="test_so_service_vnf_instance_name_1",
                parameters={
                    "param_1": "param_1_value",
                    "param_2": "param_2_value"
                }
            ),
            SoServiceVnf(
                model_name="test_so_service_vnf_model_name_2",
                instance_name="test_so_service_vnf_instance_name_2",
                vf_modules=[
                    SoServiceVfModule(
                        model_name="test_so_service_vf_module_model_name_1",
                        instance_name="test_so_service_vf_module_instance_name_1",
                        parameters={
                            "vf_module_param_1": "vf_module_param_1_value",
                            "vf_module_param_2": "vf_module_param_2_value"
                        }
                    ),
                    SoServiceVfModule(
                        model_name="test_so_service_vf_module_model_name_2",
                        instance_name="test_so_service_vf_module_instance_name_2",
                        parameters={
                            "vf_module_param_1": "vf_module_param_1_value",
                            "vf_module_param_2": "vf_module_param_2_value"
                        }
                    ),
                ]
            )
        ],
        pnfs=[
            SoServicePnf(
                model_name="test_so_service_pnf_model_name_1",
                instance_name="test_so_service_pnf_instance_name_1"
            ),
            SoServicePnf(
                model_name="test_so_service_pnf_model_name_2",
                instance_name="test_so_service_pnf_instance_name_2"
            )
        ]
    )

    _ = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              project=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              service_instance_name="test",
                              so_service=so_service)
    _, kwargs = mock_send_message_json.call_args
    data = json.loads(kwargs["data"])
    assert data["requestDetails"]["requestParameters"]["subscriptionServiceType"] == "test_so_service"
    assert len(data["requestDetails"]["requestParameters"]["userParams"][1]["service"]["resources"]["vnfs"]) == 2
    assert len(data["requestDetails"]["requestParameters"]["userParams"][1]["service"]["resources"]["pnfs"]) == 2
    vnf_1_data = data["requestDetails"]["requestParameters"]["userParams"][1]["service"]["resources"]["vnfs"][0]
    vnf_2_data = data["requestDetails"]["requestParameters"]["userParams"][1]["service"]["resources"]["vnfs"][1]
    pnf_1_data = data["requestDetails"]["requestParameters"]["userParams"][1]["service"]["resources"]["pnfs"][0]
    pnf_2_data = data["requestDetails"]["requestParameters"]["userParams"][1]["service"]["resources"]["pnfs"][1]

    assert vnf_1_data["instanceName"] == "test_so_service_vnf_instance_name_1"
    assert len(vnf_1_data["instanceParams"][0]) == 2
    assert vnf_1_data["instanceParams"][0]["param_1"] == "param_1_value"
    assert vnf_1_data["instanceParams"][0]["param_2"] == "param_2_value"
    assert len(vnf_1_data["vfModules"]) == 0

    assert vnf_2_data["instanceName"] == "test_so_service_vnf_instance_name_2"
    assert len(vnf_2_data["instanceParams"][0]) == 0
    assert len(vnf_2_data["vfModules"]) == 2
    vf_module_1_data = vnf_2_data["vfModules"][0]
    vf_module_2_data = vnf_2_data["vfModules"][1]

    assert vf_module_1_data["instanceName"] == "test_so_service_vf_module_instance_name_1"
    assert len(vf_module_1_data["instanceParams"][0]) == 2
    assert vf_module_1_data["instanceParams"][0]["vf_module_param_1"] == "vf_module_param_1_value"
    assert vf_module_1_data["instanceParams"][0]["vf_module_param_2"] == "vf_module_param_2_value"

    assert vf_module_2_data["instanceName"] == "test_so_service_vf_module_instance_name_2"
    assert len(vf_module_2_data["instanceParams"][0]) == 2
    assert vf_module_2_data["instanceParams"][0]["vf_module_param_1"] == "vf_module_param_1_value"
    assert vf_module_2_data["instanceParams"][0]["vf_module_param_2"] == "vf_module_param_2_value"

    assert pnf_1_data["instanceName"] == "test_so_service_pnf_instance_name_1"

    assert pnf_2_data["instanceName"] == "test_so_service_pnf_instance_name_2"


def test_so_service_load_from_yaml():

    so_service_yaml = """
    subscription_service_type: myservice
    vnfs:
        - model_name: myvfmodel
          instance_name: myfirstvnf
          parameters:
              param1: value1
          processing_priority: 1
          vf_modules:
              - instance_name: mysecondvfm
                model_name: base
                processing_priority: 2
                parameters:
                    param-vfm1: value-vfm1
              - instance_name: myfirstvfm
                model_name: base
                processing_priority: 1
                parameters:
                    param-vfm1: value-vfm1
        - model_name: myvfmodel
          instance_name: mysecondvnf
          parameters:
              param1: value1
          processing_priority: 2
          vf_modules:
              - instance_name: myfirstvfm
                model_name: base
                processing_priority: 1
                parameters:
                    param-vfm1: value-vfm1
              - instance_name: mysecondvfm
                model_name: base
                processing_priority: 2
                parameters:
                    param-vfm1: value-vfm1
    pnfs:
        - model_name: mypnfmodel
          instance_name: myfirstpnf
    """
    so_service = SoService.load(yaml.safe_load(so_service_yaml))
    assert so_service.subscription_service_type == "myservice"
    assert not so_service.instance_name
    assert len(so_service.vnfs) == 2
    assert len(so_service.pnfs) == 1

    so_service_vnf_1 = so_service.vnfs[0]
    so_service_vnf_2 = so_service.vnfs[1]
    so_service_pnf = so_service.pnfs[0]

    assert so_service_vnf_1.model_name == "myvfmodel"
    assert so_service_vnf_1.instance_name == "myfirstvnf"
    assert so_service_vnf_1.processing_priority == 1
    assert len(so_service_vnf_1.parameters) == 1
    assert so_service_vnf_1.parameters["param1"] == "value1"
    assert len(so_service_vnf_1.vf_modules) == 2

    so_service_vnf_1_vf_module_1 = so_service_vnf_1.vf_modules[0]
    so_service_vnf_1_vf_module_2 = so_service_vnf_1.vf_modules[1]

    assert so_service_vnf_1_vf_module_1.model_name == "base"
    assert so_service_vnf_1_vf_module_1.instance_name == "mysecondvfm"
    assert so_service_vnf_1_vf_module_1.processing_priority == 2
    assert len(so_service_vnf_1_vf_module_1.parameters) == 1
    assert so_service_vnf_1_vf_module_1.parameters["param-vfm1"] == "value-vfm1"
    assert so_service_vnf_1_vf_module_2.model_name == "base"
    assert so_service_vnf_1_vf_module_2.instance_name == "myfirstvfm"
    assert so_service_vnf_1_vf_module_2.processing_priority == 1
    assert len(so_service_vnf_1_vf_module_2.parameters) == 1
    assert so_service_vnf_1_vf_module_2.parameters["param-vfm1"] == "value-vfm1"

    assert so_service_vnf_2.model_name == "myvfmodel"
    assert so_service_vnf_2.instance_name == "mysecondvnf"
    assert so_service_vnf_2.processing_priority == 2
    assert len(so_service_vnf_2.parameters) == 1
    assert so_service_vnf_2.parameters["param1"] == "value1"
    assert len(so_service_vnf_2.vf_modules) == 2

    so_service_vnf_1_vf_module_1 = so_service_vnf_2.vf_modules[0]
    so_service_vnf_1_vf_module_2 = so_service_vnf_2.vf_modules[1]

    assert so_service_vnf_1_vf_module_1.model_name == "base"
    assert so_service_vnf_1_vf_module_1.instance_name == "myfirstvfm"
    assert so_service_vnf_1_vf_module_1.processing_priority == 1
    assert len(so_service_vnf_1_vf_module_1.parameters) == 1
    assert so_service_vnf_1_vf_module_1.parameters["param-vfm1"] == "value-vfm1"
    assert so_service_vnf_1_vf_module_2.model_name == "base"
    assert so_service_vnf_1_vf_module_2.instance_name == "mysecondvfm"
    assert so_service_vnf_1_vf_module_2.processing_priority == 2
    assert len(so_service_vnf_1_vf_module_2.parameters) == 1
    assert so_service_vnf_1_vf_module_2.parameters["param-vfm1"] == "value-vfm1"

    assert so_service_pnf.model_name == "mypnfmodel"
    assert so_service_pnf.instance_name == "myfirstpnf"


def test_so_service_load_from_file():
    with Path(Path(__file__).parent, "data/test_so_service_data.yaml").open() as yaml_template:
        so_service_data = yaml.safe_load(yaml_template)
    service = Service(next(iter(so_service_data.keys())))
    so_service = SoService.load(so_service_data[service.name])
    assert so_service.subscription_service_type == "myservice"
    assert not so_service.instance_name
    assert len(so_service.vnfs) == 2

    so_service_vnf_1 = so_service.vnfs[0]
    so_service_vnf_2 = so_service.vnfs[1]

    assert so_service_vnf_1.model_name == "myvfmodel"
    assert so_service_vnf_1.instance_name == "myfirstvnf"
    assert so_service_vnf_1.processing_priority == 1
    assert len(so_service_vnf_1.parameters) == 1
    assert so_service_vnf_1.parameters["param1"] == "value1"
    assert len(so_service_vnf_1.vf_modules) == 2

    so_service_vnf_1_vf_module_1 = so_service_vnf_1.vf_modules[0]
    so_service_vnf_1_vf_module_2 = so_service_vnf_1.vf_modules[1]

    assert so_service_vnf_1_vf_module_1.model_name == "base"
    assert so_service_vnf_1_vf_module_1.instance_name == "mysecondvfm"
    assert so_service_vnf_1_vf_module_1.processing_priority == 2
    assert len(so_service_vnf_1_vf_module_1.parameters) == 1
    assert so_service_vnf_1_vf_module_1.parameters["param-vfm1"] == "value-vfm1"
    assert so_service_vnf_1_vf_module_2.model_name == "base"
    assert so_service_vnf_1_vf_module_2.instance_name == "myfirstvfm"
    assert so_service_vnf_1_vf_module_2.processing_priority == 1
    assert len(so_service_vnf_1_vf_module_2.parameters) == 1
    assert so_service_vnf_1_vf_module_2.parameters["param-vfm1"] == "value-vfm1"

    assert so_service_vnf_2.model_name == "myvfmodel"
    assert so_service_vnf_2.instance_name == "mysecondvnf"
    assert so_service_vnf_2.processing_priority == 2
    assert len(so_service_vnf_2.parameters) == 1
    assert so_service_vnf_2.parameters["param1"] == "value1"
    assert len(so_service_vnf_2.vf_modules) == 2

    so_service_vnf_1_vf_module_1 = so_service_vnf_2.vf_modules[0]
    so_service_vnf_1_vf_module_2 = so_service_vnf_2.vf_modules[1]

    assert so_service_vnf_1_vf_module_1.model_name == "base"
    assert so_service_vnf_1_vf_module_1.instance_name == "myfirstvfm"
    assert so_service_vnf_1_vf_module_1.processing_priority == 1
    assert len(so_service_vnf_1_vf_module_1.parameters) == 1
    assert so_service_vnf_1_vf_module_1.parameters["param-vfm1"] == "value-vfm1"
    assert so_service_vnf_1_vf_module_2.model_name == "base"
    assert so_service_vnf_1_vf_module_2.instance_name == "mysecondvfm"
    assert so_service_vnf_1_vf_module_2.processing_priority == 2
    assert len(so_service_vnf_1_vf_module_2.parameters) == 1
    assert so_service_vnf_1_vf_module_2.parameters["param-vfm1"] == "value-vfm1"


def test_so_service_vnf_load_from_yaml():

    so_vnf_yaml = """
    model_name: myvnfmodel
    instance_name: mynewvnf
    parameters:
        param1: value1
    vf_modules:
        - instance_name: myfirstvfm 
          model_name: base
          processing_priority: 1
          parameters:
              param-vfm1: value-vfm1
        - instance_name: mysecondvfm
          model_name: second_base
          processing_priority: 2
          parameters:
              param-vfm2: value-vfm2
              param-vfm3: value-vfm3
    """

    so_vnf = SoServiceVnf.load(yaml.safe_load(so_vnf_yaml))
    assert so_vnf.model_name == "myvnfmodel"
    assert so_vnf.instance_name == "mynewvnf"

    assert len(so_vnf.parameters) == 1
    assert so_vnf.parameters["param1"] == "value1"

    assert len(so_vnf.vf_modules) == 2
    so_vnf_vf_module_1 = so_vnf.vf_modules[0]
    so_vnf_vf_module_2 = so_vnf.vf_modules[1]

    assert so_vnf_vf_module_1.model_name == "base"
    assert so_vnf_vf_module_1.instance_name == "myfirstvfm"
    assert so_vnf_vf_module_1.processing_priority == 1
    assert len(so_vnf_vf_module_1.parameters) == 1
    assert so_vnf_vf_module_1.parameters["param-vfm1"] == "value-vfm1"

    assert so_vnf_vf_module_2.model_name == "second_base"
    assert so_vnf_vf_module_2.instance_name == "mysecondvfm"
    assert so_vnf_vf_module_2.processing_priority == 2
    assert len(so_vnf_vf_module_2.parameters) == 2
    assert so_vnf_vf_module_2.parameters["param-vfm2"] == "value-vfm2"
    assert so_vnf_vf_module_2.parameters["param-vfm3"] == "value-vfm3"
