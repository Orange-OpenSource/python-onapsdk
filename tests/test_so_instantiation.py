from unittest import mock

import pytest

from onapsdk.sdnc import VfModulePreload
from onapsdk.service import Service as SdcService
from onapsdk.so.so_element import OrchestrationRequest
from onapsdk.so.instantiation import (
    ServiceInstantiation,
    VfModuleInstantiation,
    VnfInstantiation
)


@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_instantiation(mock_service_instantiation_send_message):
    mock_sdc_service = mock.MagicMock()
    mock_sdc_service.distributed = False
    with pytest.raises(ValueError):
        ServiceInstantiation.\
            instantiate_so_ala_carte(sdc_service=mock_sdc_service,
                                    cloud_region=mock.MagicMock(),
                                    tenant=mock.MagicMock(),
                                    customer=mock.MagicMock(),
                                    owning_entity=mock.MagicMock(),
                                    project=mock.MagicMock(),
                                    service_instance_name="test")
    mock_sdc_service.distributed = True
    service_instance = ServiceInstantiation.\
            instantiate_so_ala_carte(sdc_service=mock_sdc_service,
                                    cloud_region=mock.MagicMock(),
                                    tenant=mock.MagicMock(),
                                    customer=mock.MagicMock(),
                                    owning_entity=mock.MagicMock(),
                                    project=mock.MagicMock(),
                                    service_instance_name="test")
    assert service_instance.name == "test"

    service_instance = ServiceInstantiation.\
            instantiate_so_ala_carte(sdc_service=mock_sdc_service,
                                    cloud_region=mock.MagicMock(),
                                    tenant=mock.MagicMock(),
                                    customer=mock.MagicMock(),
                                    owning_entity=mock.MagicMock(),
                                    project=mock.MagicMock())
    assert service_instance.name.startswith("Python_ONAP_SDK_service_instance_")
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
    with pytest.raises(AttributeError):
        service_instantiation.aai_service_instance

    status_mock.return_value = return_value=ServiceInstantiation.StatusEnum.COMPLETED
    assert service_instantiation.aai_service_instance is not None

    customer_mock.get_service_subscription_by_service_type.side_effect = ValueError
    with pytest.raises(AttributeError):
        service_instantiation.aai_service_instance


@mock.patch.object(VnfInstantiation, "send_message_json")
def test_vnf_instantiation(mock_vnf_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = VnfInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              vnf_object=mock.MagicMock(),
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock())
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
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock(),
                              vnf_instance_name="test")
    assert vnf_instantiation.name == "test"


@mock.patch.object(VnfInstantiation, "send_message_json")
@mock.patch("onapsdk.so.instantiation.SdcService")
def test_vnf_instantiation_get_by_vnf_instance_name(mock_sdc_service, mock_send_message_json):
    mock_sdc_service.return_value.vnfs = []
    mock_send_message_json.return_value = {}
    with pytest.raises(ValueError):
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
    with pytest.raises(ValueError):
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
    with pytest.raises(ValueError):
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
    with pytest.raises(ValueError):
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
    with pytest.raises(ValueError):
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
    with pytest.raises(ValueError):
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
                              vnf_instance=mock_vnf_instance)
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
                              vf_module_instance_name="test")
    assert instantiation.name == "test"
