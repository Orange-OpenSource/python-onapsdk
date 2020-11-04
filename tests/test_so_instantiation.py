import json
from unittest import mock

import pytest

from onapsdk.sdnc import NetworkPreload, VfModulePreload
from onapsdk.sdc.service import Service as SdcService
from onapsdk.so.so_element import OrchestrationRequest
from onapsdk.so.instantiation import (
    NetworkInstantiation,
    ServiceInstantiation,
    VfModuleInstantiation,
    VnfInstantiation
)
from onapsdk.vid import Vid


@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_ala_carte_instantiation(mock_service_instantiation_send_message):
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


@mock.patch.object(ServiceInstantiation, "send_message_json")
def test_service_macro_instantiation(mock_service_instantiation_send_message):
    mock_sdc_service = mock.MagicMock()
    mock_sdc_service.distributed = False
    with pytest.raises(ValueError):
        ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              project=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
                              service_instance_name="test")
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
                              service_instance_name="test")
    assert service_instance.name == "test"

    service_instance = ServiceInstantiation.\
            instantiate_macro(sdc_service=mock_sdc_service,
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              customer=mock.MagicMock(),
                              owning_entity=mock.MagicMock(),
                              line_of_business=mock.MagicMock(),
                              platform=mock.MagicMock(),
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
def test_vnf_instantiation_with_cr_and_tenant(mock_vnf_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = VnfInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              vnf_object=mock.MagicMock(),
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock(),
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock())
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
                              cloud_region=mock.MagicMock(),
                              tenant=mock.MagicMock(),
                              vnf_instance_name="test")
    assert vnf_instantiation.name == "test"


@mock.patch.object(NetworkInstantiation, "send_message_json")
@mock.patch.object(NetworkPreload, "send_message_json")
def test_network_instantiation(mock_network_preload, mock_network_instantiation_send_message):
    aai_service_instance_mock = mock.MagicMock()
    aai_service_instance_mock.instance_id = "test_instance_id"
    vnf_instantiation = NetworkInstantiation.\
        instantiate_ala_carte(aai_service_instance=aai_service_instance_mock,
                              network_object=mock.MagicMock(),
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock())
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
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock(),
                              network_instance_name="test")
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
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock(),
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
                              line_of_business_object=mock.MagicMock(),
                              platform_object=mock.MagicMock(),
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
            assert instantiation.wait_for_finish()

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
                                  project=mock.MagicMock())
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
                                  enable_multicloud=True)
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
                              service_instance_name="test")
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
                              enable_multicloud=True)
    _, kwargs = mock_send_message_json.call_args
    data = json.loads(kwargs["data"])
    assert any(filter(lambda x: x == {"name": "orchestrator", "value": "multicloud"}, data["requestDetails"]["requestParameters"]["userParams"]))
