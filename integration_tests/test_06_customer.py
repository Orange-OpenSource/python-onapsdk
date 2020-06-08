from uuid import uuid4

import pytest

import requests
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer, ServiceSubscription
from onapsdk.service import Service

from .urls import AAI_MOCK_URL


@pytest.mark.integration
def test_create_customer():

    Customer.base_url = AAI_MOCK_URL
    requests.get(f"{Customer.base_url}/reset")

    customers = list(Customer.get_all())
    assert len(customers) == 0

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    assert customer.global_customer_id == "test_global_customer_id"
    assert customer.subscriber_name == "test_subscriber_name"
    assert customer.subscriber_type == "test_subscriber_type"

    customers = list(Customer.get_all())
    assert len(customers) == 1


@pytest.mark.integration
def test_subscribe_service():

    Customer.base_url = AAI_MOCK_URL
    requests.get(f"{Customer.base_url}/reset")

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    assert len(list(customer.service_subscriptions)) == 0

    service = Service("test_service")
    service.unique_uuid = str(uuid4())
    customer.subscribe_service(service)
    assert len(list(customer.service_subscriptions)) == 1
    assert customer.get_service_subscription_by_service_type(service.name)


@pytest.mark.integration
def test_link_service_subscription_to_cloud_region_and_tenant():

    Customer.base_url = AAI_MOCK_URL
    CloudRegion.base_url = AAI_MOCK_URL
    ServiceSubscription.base_url = AAI_MOCK_URL
    requests.get(f"{Customer.base_url}/reset")

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    service = Service("test_service")
    service.unique_uuid = str(uuid4())
    customer.subscribe_service(service)
    service_subscription = customer.get_service_subscription_by_service_type(service.name)

    assert len(list(service_subscription.relationships)) == 0
    with pytest.raises(AttributeError):
        service_subscription.cloud_region
    with pytest.raises(AttributeError):
        service_subscription.tenant

    cloud_region = CloudRegion.create(
        "test_owner", "test_cloud_region", orchestration_disabled=True, in_maint=False
    )
    cloud_region.add_tenant(
        tenant_id="test_tenant_name", tenant_name="test_tenant_name", tenant_context="test_tenant_context"
    )
    tenant = cloud_region.get_tenant(tenant_id="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
    assert service_subscription.cloud_region
    assert service_subscription.tenant
