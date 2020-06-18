#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI Customer module."""
from unittest import mock

import pytest

from onapsdk.aai.business import Customer, ServiceSubscription
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.service import Service as SdcService


SIMPLE_CUSTOMER = {
    "customer": [
        {
            "global-customer-id": "generic",
            "subscriber-name": "generic",
            "subscriber-type": "INFRA",
            "resource-version": "1561218640404",
        }
    ]
}


SERVICE_SUBSCRIPTION = {
    "service-subscription": [
        {
            "service-type": "freeradius",
            "resource-version": "1562591478146",
            "relationship-list": {
                "relationship": [
                    {
                        "related-to": "tenant",
                        "relationship-label": "org.onap.relationships.inventory.Uses",
                        "related-link": "/aai/v16/cloud-infrastructure/cloud-regions/cloud-region/OPNFV/RegionOne/tenants/tenant/4bdc6f0f2539430f9428c852ba606808",
                        "relationship-data": [
                            {
                                "relationship-key": "cloud-region.cloud-owner",
                                "relationship-value": "OPNFV",
                            },
                            {
                                "relationship-key": "cloud-region.cloud-region-id",
                                "relationship-value": "RegionOne",
                            },
                            {
                                "relationship-key": "tenant.tenant-id",
                                "relationship-value": "4bdc6f0f2539430f9428c852ba606808",
                            },
                        ],
                        "related-to-property": [
                            {
                                "property-key": "tenant.tenant-name",
                                "property-value": "onap-dublin-daily-vnfs",
                            }
                        ],
                    }
                ]
            },
        },
        {"service-type": "ims"},
    ]
}


CUSTOMERS = {
    "customer": [
        {
            "subscriber-name": "generic",
            "subscriber-type": "INFRA",
            "global-customer-id": "generic",
            "resource-version": "1581510772967",
        }
    ]
}


SIMPLE_CUSTOMER_2 = {
    "global-customer-id": "generic",
    "subscriber-name": "generic",
    "subscriber-type": "INFRA",
    "resource-version": "1561218640404",
}


SERVICE_INSTANCES = {
    "service-instance":[
        {
            "service-instance-id":"5410bf79-2aa3-450e-a324-ec5630dc18cf",
            "service-instance-name":"test",
            "environment-context":"General_Revenue-Bearing",
            "workload-context":"Production",
            "model-invariant-id":"2a51a89b-6f94-4417-8831-c468fb30ed02",
            "model-version-id":"92a82807-b483-4579-86b1-c79b1286aab4",
            "resource-version":"1589457727708",
            "orchestration-status":"Active",
            "relationship-list":{
                "relationship":[
                    {
                        "related-to":"owning-entity",
                        "relationship-label":"org.onap.relationships.inventory.BelongsTo",
                        "related-link":"/aai/v16/business/owning-entities/owning-entity/ff6c945f-89ab-4f14-bafd-0cdd6eac791a",
                        "relationship-data":[
                            {
                                "relationship-key":"owning-entity.owning-entity-id",
                                "relationship-value":"ff6c945f-89ab-4f14-bafd-0cdd6eac791a"
                            }
                        ]
                    },
                    {
                        "related-to":"project",
                        "relationship-label":"org.onap.relationships.inventory.Uses",
                        "related-link":"/aai/v16/business/projects/project/python_onap_sdk_project",
                        "relationship-data":[
                            {
                                "relationship-key":"project.project-name",
                                "relationship-value":"python_onap_sdk_project"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}


SERVICE_SUBSCRIPTION_RELATIONSHIPS = {
    "relationship": [
        {
            "related-to": "tenant",
            "relationship-label": "org.onap.relationships.inventory.Uses",
            "related-link": "/aai/v16/cloud-infrastructure/cloud-regions/cloud-region/OPNFV/RegionOne/tenants/tenant/4bdc6f0f2539430f9428c852ba606808",
            "relationship-data": [
                {
                    "relationship-key": "cloud-region.cloud-owner",
                    "relationship-value": "OPNFV",
                },
                {
                    "relationship-key": "cloud-region.cloud-region-id",
                    "relationship-value": "RegionOne",
                },
                {
                    "relationship-key": "tenant.tenant-id",
                    "relationship-value": "4bdc6f0f2539430f9428c852ba606808",
                },
            ],
            "related-to-property": [
                {
                    "property-key": "tenant.tenant-name",
                    "property-value": "onap-dublin-daily-vnfs",
                }
            ],
        }
    ]
}


CLOUD_REGION = {
    "cloud-region": [
        {
            "cloud-owner": "OPNFV",
            "cloud-region-id": "RegionOne",
            "cloud-type": "openstack",
            "owner-defined-type": "N/A",
            "cloud-region-version": "pike",
            "identity-url": "http://msb-iag.onap:80/api/multicloud-pike/v0/OPNFV_RegionOne/identity/v2.0",
            "cloud-zone": "OPNFV LaaS",
            "complex-name": "Cruguil",
            "resource-version": "1561217827955",
            "orchestration-disabled": True,
            "in-maint": False,
            "relationship-list": {
                "relationship": [
                    {
                        "related-to": "complex",
                        "relationship-label": "org.onap.relationships.inventory.LocatedIn",
                        "related-link": "/aai/v13/cloud-infrastructure/complexes/complex/cruguil",
                        "relationship-data": [
                            {
                                "relationship-key": "complex.physical-location-id",
                                "relationship-value": "cruguil",
                            }
                        ],
                    }
                ]
            },
        }
    ]
}


TENANT = {
    "tenant-id": "4bdc6f0f2539430f9428c852ba606808",
    "tenant-name": "onap-dublin-daily-vnfs",
    "resource-version": "1562591004273",
    "relationship-list": {
        "relationship": [
            {
                "related-to": "service-subscription",
                "relationship-label": "org.onap.relationships.inventory.Uses",
                "related-link": "/aai/v16/business/customers/customer/generic/service-subscriptions/service-subscription/freeradius",
                "relationship-data": [
                    {
                        "relationship-key": "customer.global-customer-id",
                        "relationship-value": "generic",
                    },
                    {
                        "relationship-key": "service-subscription.service-type",
                        "relationship-value": "freeradius",
                    },
                ],
            },
            {
                "related-to": "service-subscription",
                "relationship-label": "org.onap.relationships.inventory.Uses",
                "related-link": "/aai/v16/business/customers/customer/generic/service-subscriptions/service-subscription/ims",
                "relationship-data": [
                    {
                        "relationship-key": "customer.global-customer-id",
                        "relationship-value": "generic",
                    },
                    {
                        "relationship-key": "service-subscription.service-type",
                        "relationship-value": "ims",
                    },
                ],
            },
            {
                "related-to": "service-subscription",
                "relationship-label": "org.onap.relationships.inventory.Uses",
                "related-link": "/aai/v16/business/customers/customer/generic/service-subscriptions/service-subscription/ubuntu16",
                "relationship-data": [
                    {
                        "relationship-key": "customer.global-customer-id",
                        "relationship-value": "generic",
                    },
                    {
                        "relationship-key": "service-subscription.service-type",
                        "relationship-value": "ubuntu16",
                    },
                ],
            },
        ]
    },
}


@mock.patch.object(Customer, 'send_message_json')
def test_customer_service_tenant_relations(mock_send):
    """Test the retrieval of service/tenant relations in A&AI."""
    mock_send.return_value = SIMPLE_CUSTOMER
    customer = next(Customer.get_all())
    mock_send.return_value = SERVICE_SUBSCRIPTION
    res = list(customer.service_subscriptions)
    assert len(res) == 2
    assert res[0].service_type == "freeradius"


@mock.patch.object(Customer, "send_message_json")
def test_customers_get_all(mock_send):
    """Test get_all Customer class method."""
    mock_send.return_value = {}
    customers = list(Customer.get_all())
    assert len(customers) == 0

    mock_send.return_value = CUSTOMERS
    customers = list(Customer.get_all())
    assert len(customers) == 1


@mock.patch.object(Customer, "send_message_json")
def test_customer_get_service_subscription_by_service_type(mock_send):
    """Test Customer's get_service_subscription_by_service_type method."""
    mock_send.return_value = CUSTOMERS
    customer = next(Customer.get_all())

    mock_send.return_value = SERVICE_SUBSCRIPTION
    service_subscription = customer.get_service_subscription_by_service_type("freeradius")
    assert service_subscription.service_type == "freeradius"


@mock.patch.object(Customer, "send_message_json")
@mock.patch.object(ServiceSubscription, "send_message_json")
def test_customer_service_subscription_service_instance(mock_send_serv_sub, mock_send):
    """Test Customer's service subscription service instances."""
    mock_send.return_value = CUSTOMERS
    customer = next(Customer.get_all())
    mock_send.return_value = SERVICE_SUBSCRIPTION
    service_subscription = customer.get_service_subscription_by_service_type("freeradius")

    mock_send_serv_sub.return_value = SERVICE_INSTANCES
    service_instances = list(service_subscription.service_instances)
    assert len(service_instances) == 1
    service_instance = service_instances[0]
    assert service_instance.instance_name == "test"
    assert service_instance.instance_id == "5410bf79-2aa3-450e-a324-ec5630dc18cf"
    assert service_instance.service_subscription == service_subscription
    assert service_instance.url == (f"{service_subscription.url}/service-instances/"
                                    f"service-instance/{service_instance.instance_id}")


@mock.patch.object(Customer, "send_message_json")
@mock.patch.object(ServiceSubscription, "send_message_json")
@mock.patch.object(CloudRegion, "send_message_json")
def test_customer_service_subscription_cloud_region(mock_cloud_region, mock_send_serv_sub, mock_send):
    """Test Customer's service subscription cloud region object."""
    mock_send.return_value = CUSTOMERS
    customer = next(Customer.get_all())
    mock_send.return_value = SERVICE_SUBSCRIPTION
    service_subscription = customer.get_service_subscription_by_service_type("freeradius")

    mock_send_serv_sub.return_value = {}
    relationships = list(service_subscription.relationships)
    assert len(relationships) == 0
    with pytest.raises(AttributeError):
        service_subscription.cloud_region
    with pytest.raises(AttributeError):
        service_subscription.tenant

    mock_cloud_region.return_value = CLOUD_REGION
    mock_send_serv_sub.return_value = SERVICE_SUBSCRIPTION_RELATIONSHIPS
    relationships = list(service_subscription.relationships)
    assert len(relationships) == 1
    cloud_region = service_subscription.cloud_region
    assert service_subscription._cloud_region == cloud_region
    assert cloud_region.cloud_owner == "OPNFV"
    assert cloud_region.cloud_region_id == "RegionOne"
    assert cloud_region.cloud_type == "openstack"

    mock_cloud_region.side_effect = ValueError
    with pytest.raises(AttributeError):
        service_subscription.tenant
    mock_cloud_region.side_effect = None
    mock_cloud_region.return_value = TENANT
    tenant = service_subscription.tenant
    assert tenant == service_subscription._tenant
    assert tenant.tenant_id == "4bdc6f0f2539430f9428c852ba606808"
    assert tenant.name == "onap-dublin-daily-vnfs"


@mock.patch.object(Customer, "send_message_json")
def test_customer_get_by_global_customer_id(mock_send):
    """Test Customer's get_by_global_customer_id method."""
    mock_send.return_value = SIMPLE_CUSTOMER_2
    customer = Customer.get_by_global_customer_id("generic")
    assert customer.global_customer_id == "generic"
    assert customer.subscriber_name == "generic"
    assert customer.subscriber_type == "INFRA"
    assert customer.resource_version is not None


@mock.patch.object(Customer, "send_message")
@mock.patch.object(Customer, "send_message_json")
def test_customer_create(mock_send_json, mock_send):
    """Test Customer's create method."""
    mock_send_json.return_value = SIMPLE_CUSTOMER_2
    customer = Customer.create("generic", "generic", "INFRA")
    assert customer.global_customer_id == "generic"
    assert customer.subscriber_name == "generic"
    assert customer.subscriber_type == "INFRA"
    assert customer.resource_version is not None


def test_customer_url():
    """Test Customer's url property."""
    customer = Customer("generic", "generic", "INFRA")
    assert customer.url == (f"{customer.base_url}{customer.api_version}/business/customers/"
                            f"customer/{customer.global_customer_id}?"
                            f"resource-version={customer.resource_version}")


@mock.patch.object(ServiceSubscription, "add_relationship")
def test_service_subscription_link_cloud_region_and_tenant(mock_add_rel):
    """Test service subscription linking with cloud region and tenant.

    Test Relationship object creation
    """
    service_subscription = ServiceSubscription(customer=None,
                                               service_type="test_service_type",
                                               resource_version="test_resource_version")
    cloud_region = CloudRegion(cloud_owner="test_cloud_owner",
                               cloud_region_id="test_cloud_region",
                               orchestration_disabled=True,
                               in_maint=False)
    tenant = Tenant(cloud_region=cloud_region,
                    tenant_id="test_tenant_id",
                    tenant_name="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region, tenant)
    mock_add_rel.assert_called_once()
    relationship = mock_add_rel.call_args[0][0]
    assert relationship.related_to == "tenant"
    assert relationship.related_link == tenant.url
    assert len(relationship.relationship_data) == 3


@mock.patch.object(Customer, "send_message_json")
@mock.patch.object(Customer, "send_message")
def test_customer_subscribe_service(mock_send_message, mock_send_message_json):
    customer = Customer(global_customer_id="test_customer_id",
                        subscriber_name="test_subscriber_name",
                        subscriber_type="test_subscriber_type")
    service = SdcService("test_service")
    service._unique_uuid = "1234"
    mock_send_message_json.side_effect = (ValueError, SERVICE_SUBSCRIPTION)
    customer.subscribe_service(service)
