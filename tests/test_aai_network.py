
from unittest import mock

from onapsdk.aai.business import NetworkInstance, ServiceInstance
from onapsdk.so.deletion import NetworkDeletionRequest


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


def test_create_network_instance_from_api_response():
    service_instance = mock.MagicMock()
    network_instance = NetworkInstance.create_from_api_response(
        NETWORK_INSTANCE,
        service_instance
    )
    assert network_instance.network_name == "Python_ONAP_SDK_network_instance_0b4308ca-3fe0-4af1-9c4e-ed2c816b9496"
    assert network_instance.network_id == "49dab38b-3a5b-47e5-9cd6-b8d069d6109d"
    assert network_instance.is_bound_to_vpn is False
    assert network_instance.is_provider_network is False
    assert network_instance.is_shared_network is False
    assert network_instance.is_external_network is False
    assert network_instance.resource_version == "1593162237842"
    assert network_instance.model_invariant_id == "cdbb2169-e638-4aab-a4e9-b9d2d6d62b04"
    assert network_instance.model_version_id == "51789f7b-5ffc-4c12-ac87-02363fdb40b1"
    assert network_instance.model_customization_id == "db9c9a6c-2a1c-4cdd-8fbc-e10448d0e4cc"


@mock.patch.object(NetworkDeletionRequest, "send_message_json")
def test_network_instance_delete(mock_send_message_json):
    network_instance = NetworkInstance(mock.MagicMock(),
                                       network_id="test_network_id",
                                       is_bound_to_vpn=True,
                                       is_provider_network=False,
                                       is_shared_network=True,
                                       is_external_network=False)
    network_instance.delete()
    mock_send_message_json.assert_called_once()
