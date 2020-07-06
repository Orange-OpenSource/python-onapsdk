import json
from collections.abc import Iterable
from unittest import mock

import pytest

from onapsdk.sdnc.preload import NetworkPreload, PreloadInformation, VfModulePreload
from onapsdk.so.instantiation import Subnet


PRELOAD_INFORMATIONS = {
    'preload-information': {
        'preload-list': [
            {
                'preload-id': 'Python_ONAP_SDK_network_instance_338d5238-22fe-44d1-857a-223e2f6edd9b', 
                'preload-type': 'network', 
                'preload-data': {
                    'preload-network-topology-information': {
                        'physical-network-name': 'Not Aplicable', 
                        'is-provider-network': False, 
                        'is-external-network': False, 
                        'network-topology-identifier-structure': {
                            'network-technology': 'neutron', 
                            'network-type': 'Generic NeutronNet', 
                            'network-name': 'Python_ONAP_SDK_network_instance_338d5238-22fe-44d1-857a-223e2f6edd9b', 
                            'network-role': 'integration_test_net'
                        }, 
                        'is-shared-network': False
                    }, 
                    'preload-oper-status': {
                        'create-timestamp': '2020-06-26T09:12:03.708Z', 
                        'order-status': 'PendingAssignment'
                    }
                }
            }, 
            {
                'preload-id': 'Python_ONAP_SDK_network_instance_5d61bcf6-ec37-4cea-9d1b-744d0c2b75b9', 
                'preload-type': 'network', 
                'preload-data': {
                    'preload-network-topology-information': {
                        'is-provider-network': False, 
                        'is-external-network': False, 
                        'network-topology-identifier-structure': {
                            'network-technology': 'neutron', 
                            'network-type': 'Generic NeutronNet', 
                            'network-name': 'Python_ONAP_SDK_network_instance_5d61bcf6-ec37-4cea-9d1b-744d0c2b75b9', 
                            'network-id': '1234', 
                            'network-role': 'integration_test_net'
                        }, 
                        'is-shared-network': False
                    }, 
                    'preload-oper-status': {
                        'create-timestamp': '2020-06-25T12:22:35.939Z', 
                        'order-status': 'PendingAssignment'
                    }
                }
            }
        ]
    }
}


@mock.patch.object(VfModulePreload, "send_message_json")
def test_vf_module_preload_gr_api(mock_send_message_json):
    VfModulePreload.upload_vf_module_preload(vnf_instance=mock.MagicMock(),
                                             vf_module_instance_name="test",
                                             vf_module=mock.MagicMock())
    mock_send_message_json.assert_called_once()
    method, description, url = mock_send_message_json.call_args[0]
    assert method == "POST"
    assert description == "Upload VF module preload using GENERIC-RESOURCE-API"
    assert url == (f"{VfModulePreload.base_url}/restconf/operations/"
                   "GENERIC-RESOURCE-API:preload-vf-module-topology-operation")


@mock.patch.object(PreloadInformation, "send_message_json")
def test_preload_information(mock_send_message_json):
    mock_send_message_json.return_value = PRELOAD_INFORMATIONS
    preload_informations = PreloadInformation.get_all()
    assert isinstance(preload_informations, Iterable)
    preload_informations_list = list(preload_informations)
    assert len(preload_informations_list) == 2
    preload_information = preload_informations_list[0]
    assert isinstance(preload_information, PreloadInformation)
    assert preload_information.preload_id == "Python_ONAP_SDK_network_instance_338d5238-22fe-44d1-857a-223e2f6edd9b"
    assert preload_information.preload_type == "network"


@mock.patch.object(NetworkPreload, "send_message_json")
def test_network_preload(mock_send_message_json):
    NetworkPreload.upload_network_preload(
        mock.MagicMock(),
        network_instance_name="test_instance",
    )
    mock_send_message_json.assert_called_once()
    _, _, kwargs = mock_send_message_json.mock_calls[0]
    assert "data" in kwargs
    data = json.loads(kwargs["data"])
    assert not len(data["input"]["preload-network-topology-information"]["subnets"])

    mock_send_message_json.reset_mock()
    NetworkPreload.upload_network_preload(
        mock.MagicMock(),
        network_instance_name="test_instance",
        subnets=[Subnet(
            name="test_subnet",
            start_address="127.0.0.0",
            gateway_address="127.0.0.1"
        )]
    )
    mock_send_message_json.assert_called_once()
    _, _, kwargs = mock_send_message_json.mock_calls[0]
    assert "data" in kwargs
    data = json.loads(kwargs["data"])
    assert len(data["input"]["preload-network-topology-information"]["subnets"])
    assert data["input"]["preload-network-topology-information"]["subnets"][0]["subnet-name"] == "test_subnet"
    assert data["input"]["preload-network-topology-information"]["subnets"][0]["dhcp-enabled"] == "N"

    mock_send_message_json.reset_mock()
    NetworkPreload.upload_network_preload(
        mock.MagicMock(),
        network_instance_name="test_instance",
        subnets=[Subnet(
            name="test_subnet",
            start_address="127.0.0.0",
            gateway_address="127.0.0.1",
            dhcp_enabled=True,
            dhcp_start_address="192.168.0.0",
            dhcp_end_address="192.168.0.1"
        )]
    )
    mock_send_message_json.assert_called_once()
    _, _, kwargs = mock_send_message_json.mock_calls[0]
    assert "data" in kwargs
    data = json.loads(kwargs["data"])
    assert len(data["input"]["preload-network-topology-information"]["subnets"])
    assert data["input"]["preload-network-topology-information"]["subnets"][0]["subnet-name"] == "test_subnet"
    assert data["input"]["preload-network-topology-information"]["subnets"][0]["dhcp-start-address"] == "192.168.0.0"
    assert data["input"]["preload-network-topology-information"]["subnets"][0]["dhcp-end-address"] == "192.168.0.1"
