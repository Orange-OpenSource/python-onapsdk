from unittest import mock

import pytest

from onapsdk.aai.aai_element import AaiElement
from onapsdk.aai.business import ServiceInstance
from onapsdk.so.deletion import ServiceDeletionRequest
from onapsdk.so.instantiation import NetworkInstantiation, VnfInstantiation
from onapsdk.exceptions import StatusError


RELATIONSHIPS_VNF = {
    "relationship": [
        {
            "related-to": "generic-vnf",
            "relationship_label": "anything",
            "related_link": "test_relationship_related_link",
            "relationship_data": []
        }
    ]
}


RELATIONSHIPS_NETWORK = {
    "relationship": [
        {
            "related-to": "l3-network",
            "relationship-label": "anything",
            "related-link": "related_link",
            "relationship-data": []
        }
    ]
}


NETWORK_INSTANCE = {
    'network-id': '49dab38b-3a5b-47e5-9cd6-b8d069d6109d',
    'network-name': 'Python_ONAP_SDK_network_instance_0b4308ca-3fe0-4af1-9c4e-ed2c816b9496',
    'is-bound-to-vpn': False,
    'resource-version': '1593162237842',
    'orchestration-status': 'Inventoried',
    'model-invariant-id': 'cdbb2169-e638-4aab-a4e9-b9d2d6d62b04',
    'model-version-id': '51789f7b-5ffc-4c12-ac87-02363fdb40b1',
    'model-customization-id': 'db9c9a6c-2a1c-4cdd-8fbc-e10448d0e4cc',
    'is-provider-network': False,
    'is-shared-network': False,
    'is-external-network': False,
    'relationship-list': {
        'relationship': [
            {
                'related-to': 'service-instance',
                'relationship-label': 'org.onap.relationships.inventory.ComposedOf',
                'related-link': '/aai/v19/business/customers/customer/TestCustomer/service-subscriptions/service-subscription/vFW_with_net/service-instances/service-instance/72fd9ee9-077f-4d3d-8e86-08ed24514802',
                'relationship-data': [
                    {
                        'relationship-key': 'customer.global-customer-id',
                        'relationship-value': 'TestCustomer'
                    },
                    {
                        'relationship-key': 'service-subscription.service-type',
                        'relationship-value': 'vFW_with_net'
                    },
                    {
                        'relationship-key': 'service-instance.service-instance-id',
                        'relationship-value': '72fd9ee9-077f-4d3d-8e86-08ed24514802'
                    }
                ],
                'related-to-property': [
                    {
                        'property-key': 'service-instance.service-instance-name',
                        'property-value': 'Python_ONAP_SDK_service_instance_7be66d06-c466-46cf-b84a-cd7af2d633ed'
                    }
                ]
            },
            {
                'related-to': 'cloud-region',
                'relationship-label': 'org.onap.relationships.inventory.Uses',
                'related-link': '/aai/v19/cloud-infrastructure/cloud-regions/cloud-region/TestCloudOwner/RegionOne',
                'relationship-data': [
                    {
                        'relationship-key': 'cloud-region.cloud-owner',
                        'relationship-value': 'TestCloudOwner'
                    },
                    {
                        'relationship-key': 'cloud-region.cloud-region-id',
                        'relationship-value': 'RegionOne'
                    }
                ],
                'related-to-property': [
                    {
                        'property-key': 'cloud-region.owner-defined-type',
                        'property-value': ''
                    }
                ]
            },
            {
                'related-to': 'line-of-business',
                'relationship-label': 'org.onap.relationships.inventory.Uses',
                'related-link': '/aai/v19/business/lines-of-business/line-of-business/Test-BusinessLine',
                'relationship-data': [
                    {
                        'relationship-key': 'line-of-business.line-of-business-name',
                        'relationship-value': 'Test-BusinessLine'
                    }
                ]
            },
            {
                'related-to': 'tenant',
                'relationship-label': 'org.onap.relationships.inventory.Uses',
                'related-link': '/aai/v19/cloud-infrastructure/cloud-regions/cloud-region/TestCloudOwner/RegionOne/tenants/tenant/89788fdf49514f94963b12a6c0cfdc71',
                'relationship-data': [
                    {
                        'relationship-key': 'cloud-region.cloud-owner',
                        'relationship-value': 'TestCloudOwner'
                    },
                    {
                        'relationship-key': 'cloud-region.cloud-region-id',
                        'relationship-value': 'RegionOne'
                    },
                    {
                        'relationship-key': 'tenant.tenant-id',
                        'relationship-value': '89788fdf49514f94963b12a6c0cfdc71'
                    }
                ],
                'related-to-property': [
                    {
                        'property-key': 'tenant.tenant-name',
                        'property-value': 'test-tenant'
                    }
                ]
            },
            {
                'related-to': 'platform',
                'relationship-label': 'org.onap.relationships.inventory.Uses',
                'related-link': '/aai/v19/business/platforms/platform/Test-Platform',
                'relationship-data': [
                    {
                        'relationship-key': 'platform.platform-name',
                        'relationship-value': 'Test-Platform'
                    }
                ]
            }
        ]
    }
}


def test_service_instance():
    service_subscription = mock.MagicMock()
    service_subscription.url = "test_url"
    service_instance = ServiceInstance(service_subscription=service_subscription,
                                       instance_id="test_service_instance_id")
    assert service_instance.url == (f"{service_instance.service_subscription.url}/service-instances/"
                                    f"service-instance/{service_instance.instance_id}")


@mock.patch.object(ServiceInstance, "send_message_json")
def test_service_instance_vnf_instances(mock_relationships_send_message_json):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    mock_relationships_send_message_json.return_value = {"relationship": []}
    assert len(list(service_instance.vnf_instances)) == 0
    mock_relationships_send_message_json.return_value = RELATIONSHIPS_VNF
    assert len(list(service_instance.vnf_instances)) == 1


@mock.patch.object(AaiElement, "send_message_json")
def test_service_instance_network_instances(mock_aai_element_send_message_json):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    mock_aai_element_send_message_json.side_effect = [RELATIONSHIPS_NETWORK, NETWORK_INSTANCE]
    assert len(list(service_instance.network_instances)) == 1


@mock.patch.object(VnfInstantiation, "instantiate_ala_carte")
def test_service_instance_add_vnf(mock_vnf_instantiation):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    service_instance.orchestration_status = "Inactive"
    with pytest.raises(StatusError) as exc:
        service_instance.add_vnf(mock.MagicMock(),
                                 mock.MagicMock(),
                                 mock.MagicMock())
    assert exc.type == StatusError
    service_instance.orchestration_status = "Active"
    service_instance.add_vnf(mock.MagicMock(),
                             mock.MagicMock(),
                             mock.MagicMock())
    mock_vnf_instantiation.assert_called_once()


@mock.patch.object(NetworkInstantiation, "instantiate_ala_carte")
def test_service_instance_add_network(mock_network_instantiation):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    service_instance.orchestration_status = "Inactive"
    with pytest.raises(StatusError) as exc:
        service_instance.add_network(mock.MagicMock(),
                                     mock.MagicMock(),
                                     mock.MagicMock())
    assert exc.type == StatusError
    service_instance.orchestration_status = "Active"
    service_instance.add_network(mock.MagicMock(),
                                 mock.MagicMock(),
                                 mock.MagicMock())
    mock_network_instantiation.assert_called_once()


@mock.patch.object(ServiceDeletionRequest, "send_request")
def test_service_instance_deletion(mock_service_deletion_request):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    service_instance.delete()
    mock_service_deletion_request.assert_called_once_with(service_instance)
