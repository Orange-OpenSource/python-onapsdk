#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test AaiElement module."""
from unittest import mock

import pytest

from onapsdk.aai.aai_element import AaiElement, Relationship
from onapsdk.aai.cloud_infrastructure import (
    CloudRegion,
    Complex,
    EsrSystemInfo,
    Tenant
)
from onapsdk.aai.business import Customer
from onapsdk.aai.service_design_and_creation import Service, Model
from onapsdk.onap_service import OnapService


# pylint: disable=C0301
TENANT = {
    "tenant": [
        {
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
    ]
}


CLOUD_REGIONS = {
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
            "orchestration-disabled": False,
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


COMPLEXES = {
    "complex": [
        {
            "city": "",
            "data-center-code": "1234",
            "street1": "",
            "street2": "",
            "physical-location-id": "integration_test_complex",
            "identity-url": "",
            "lata": "",
            "elevation": "",
            "state": "",
            "physical-location-type": "",
            "longitude": "",
            "relationship-list": {
                "relationship": [
                    {
                        "related-to-property": [
                            {
                                "property-value": "OwnerType",
                                "property-key": "cloud-region.owner-defined-type",
                            }
                        ],
                        "relationship-label": "org.onap.relationships.inventory.LocatedIn",
                        "related-link": "/aai/v16/cloud-infrastructure/cloud-regions/cloud-region/CloudOwner/RegionOne",
                        "relationship-data": [
                            {
                                "relationship-key": "cloud-region.cloud-owner",
                                "relationship-value": "CloudOwner",
                            },
                            {
                                "relationship-key": "cloud-region.cloud-region-id",
                                "relationship-value": "RegionOne",
                            },
                        ],
                        "related-to": "cloud-region",
                    }
                ]
            },
            "resource-version": "1581510773583",
            "latitude": "",
            "complex-name": "integration_test_complex",
            "postal-code": "",
            "country": "",
            "region": "",
        },
        {
            "city": "Beijing",
            "data-center-code": "example-data-center-code-val-5556",
            "street1": "example-street1-val-34205",
            "street2": "example-street2-val-99210",
            "physical-location-id": "My_Complex",
            "identity-url": "example-identity-url-val-56898",
            "lata": "example-lata-val-46073",
            "elevation": "example-elevation-val-30253",
            "state": "example-state-val-59487",
            "physical-location-type": "example-physical-location-type-val-7608",
            "longitude": "106.4074",
            "resource-version": "1581504768889",
            "latitude": "39.9042",
            "complex-name": "My_Complex",
            "postal-code": "100000",
            "country": "example-country-val-94173",
            "region": "example-region-val-13893",
        },
    ]
}


CLOUD_REGION_RELATIONSHIP = {
    "relationship": [
        {
            "relationship-label": "org.onap.relationships.inventory.LocatedIn",
            "related-link": "/aai/v16/cloud-infrastructure/complexes/complex/integration_test_complex",
            "relationship-data": [
                {
                    "relationship-key": "complex.physical-location-id",
                    "relationship-value": "integration_test_complex",
                }
            ],
            "related-to": "complex",
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


SUBSCRIPTION_TYPES_NO_RESOURCES = {
    "requestError": {
        "serviceException": {
            "messageId": "SVC3001",
            "text": ("Resource not found for %1 using id " + "%2 (msg=%3) +(ec=%4)"),
            "variables": [
                "GET",
                "service-design-and-creation/services",
                (
                    "Node Not Found:No Node of type service found at: "
                    + "/service-design-and-creation/services"
                ),
                "ERR.5.4.6114",
            ],
        }
    }
}


SUBSCRIPTION_TYPES_LIST = {
    "service": [
        {
            "service-id": "f4bcf0b0-b44e-423a-8357-5758afc14e88",
            "service-description": "ubuntu16",
            "resource-version": "1561218639393",
        },
        {
            "service-id": "2e812e77-e437-46c4-8e8e-908fbc7e176c",
            "service-description": "freeradius",
            "resource-version": "1561219163076",
        },
        {
            "service-id": "f208de57-0e02-4505-a0fa-375b13ad24ac",
            "service-description": "ims",
            "resource-version": "1561219799684",
        },
    ]
}


CUSTOMERS_NO_RESOURCES = {
    "requestError": {
        "serviceException": {
            "messageId": "SVC3001",
            "text": ("Resource not found for %1 using id " + "%2 (msg=%3) +(ec=%4)"),
            "variables": [
                "GET",
                "business/customers",
                (
                    "Node Not Found:No Node of type customer found at: "
                    + "business/customers"
                ),
                "ERR.5.4.6114",
            ],
        }
    }
}


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


ESR_SYSTEM_INFO = {
    'esr-system-info': [
        {
            'esr-system-info-id': 'c2d5e75d-56fd-47bc-af31-95607b26fa93',
            'service-url': 'http://keystone:5000/v3',
            'user-name': 'test-devel',
            'password': 'test-devel',
            'system-type': 'openstack',
            'cloud-domain': 'Default',
            'resource-version': '1586436352654'
        }
    ]
}


CLOUD_REGIONS_ITERATOR = (
    cloud_region
    for cloud_region in [
        CloudRegion(
            cloud_owner="OPNFV",
            cloud_region_id="RegionOne",
            cloud_type="openstack",
            owner_defined_type="N/A",
            cloud_region_version="pike",
            identity_url=None,
            cloud_zone="OPNFV LaaS",
            complex_name="Cruguil",
            sriov_automation=None,
            cloud_extra_info=None,
            upgrade_cycle=None,
            orchestration_disabled=False,
            in_maint=False,
            resource_version=None,
        )
    ]
)
# pylint: enable=C0301


def test_init():
    """Test the initialization."""
    element = AaiElement()
    assert isinstance(element, OnapService)


def test_class_variables():
    """Test the class variables."""
    assert AaiElement.server == "AAI"
    assert AaiElement.base_url == "https://aai.api.sparky.simpledemo.onap.org:30233"
    assert AaiElement.api_version == "/aai/v16"
    assert AaiElement.headers == {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-fromappid": "AAI",
        "x-transactionid": "0a3f6713-ba96-4971-a6f8-c2da85a3176e",
        "authorization": "Basic QUFJOkFBSQ=="}

@mock.patch.object(AaiElement, 'send_message_json')
def test_customers(mock_send):
    """Test get_customer function of A&AI."""
    mock_send.return_value = SIMPLE_CUSTOMER
    assert len(list(Customer.get_all())) == 1
    aai_customer_1 = next(Customer.get_all())
    assert aai_customer_1.global_customer_id == "generic"
    assert aai_customer_1.subscriber_name == "generic"
    assert aai_customer_1.subscriber_type == "INFRA"
    assert aai_customer_1.resource_version == "1561218640404"
    mock_send.assert_called_with("GET", 'get customers', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_customers_no_resources(mock_send):
    """Test get_customer function with no customer declared in A&AI."""
    mock_send.return_value = CUSTOMERS_NO_RESOURCES
    assert len(list(Customer.get_all())) == 0
    mock_send.assert_called_with("GET", 'get customers', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_subscription_type_list(mock_send):
    """Test the getter of subscription types in A&AI."""
    mock_send.return_value = {}
    assert len(list(Service.get_all())) == 0
    assert len(list(Service.get_all())) == 0

    mock_send.return_value = SUBSCRIPTION_TYPES_LIST
    assert len(list(Service.get_all())) == 3
    assert len(list(Service.get_all())) == 3
    subscriptions = Service.get_all()
    aai_service_1 = next(subscriptions)
    aai_service_2 = next(subscriptions)
    aai_service_3 = next(subscriptions)
    assert aai_service_1.service_id == "f4bcf0b0-b44e-423a-8357-5758afc14e88"
    assert aai_service_1.service_description == "ubuntu16"
    assert aai_service_1.resource_version == "1561218639393"
    assert aai_service_2.service_id == "2e812e77-e437-46c4-8e8e-908fbc7e176c"
    assert aai_service_2.service_description == "freeradius"
    assert aai_service_2.resource_version == "1561219163076"
    assert aai_service_3.service_id == "f208de57-0e02-4505-a0fa-375b13ad24ac"
    assert aai_service_3.service_description == "ims"
    assert aai_service_3.resource_version == "1561219799684"
    mock_send.assert_called_with("GET", 'get subscriptions', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_subscription_types_no_resources(mock_send):
    """Test get_customer function with no customer declared in A&AI."""
    mock_send.return_value = SUBSCRIPTION_TYPES_NO_RESOURCES
    assert len(list(Service.get_all())) == 0
    mock_send.assert_called_with("GET", 'get subscriptions', mock.ANY)

@mock.patch.object(AaiElement, 'send_message_json')
def test_cloud_regions(mock_send):
    """Test get cloud regions from A&AI."""
    mock_send.return_value = CLOUD_REGION
    assert len(list(CloudRegion.get_all())) == 1
    cloud_region = next(CloudRegion.get_all())
    assert cloud_region.cloud_owner == "OPNFV"
    assert cloud_region.cloud_type == "openstack"
    assert cloud_region.complex_name == "Cruguil"

    cloud_region = next(CloudRegion.get_all())
    assert cloud_region.cloud_owner == "OPNFV"
    assert cloud_region.cloud_type == "openstack"
    assert cloud_region.complex_name == "Cruguil"

    mock_send.return_value = {}
    cloud_regions = list(CloudRegion.get_all())
    assert len(cloud_regions) == 0

    with pytest.raises(StopIteration):
        cloud_region = next(CloudRegion.get_all())

    mock_send.return_value = CLOUD_REGIONS
    cloud_regions = list(CloudRegion.get_all())
    assert len(cloud_regions) == 1

@mock.patch.object(CloudRegion, "send_message")
def test_cloud_region_creation(mock_send):
    """Test cloud region creation"""
    cloud_region = CloudRegion.create(
        cloud_owner="test_owner",
        cloud_region_id="test_cloud_region",
        orchestration_disabled=False,
        in_maint=True,
        owner_defined_type="Test",
        cloud_zone="Test zone",
        sriov_automation="Test",
        upgrade_cycle="Test"
    )
    assert cloud_region.cloud_owner == "test_owner"
    assert cloud_region.cloud_region_id == "test_cloud_region"
    assert cloud_region.orchestration_disabled == False
    assert cloud_region.in_maint == True
    assert cloud_region.cloud_type == ""
    assert cloud_region.owner_defined_type == "Test"
    assert cloud_region.cloud_region_version == ""
    assert cloud_region.identity_url == ""
    assert cloud_region.cloud_zone == "Test zone"
    assert cloud_region.complex_name == ""
    assert cloud_region.sriov_automation == "Test"
    assert cloud_region.cloud_extra_info == ""
    assert cloud_region.upgrade_cycle == "Test"

@mock.patch.object(CloudRegion, 'get_all')
@mock.patch.object(AaiElement, 'send_message_json')
def test_tenants_info(mock_send, mock_cloud_regions):
    """Test get Tenant from A&AI."""
    mock_cloud_regions.return_value = CLOUD_REGIONS_ITERATOR
    mock_send.return_value = TENANT
    cloud_name = "RegionOne"
    cloud_region = CloudRegion.get_by_id("DT", cloud_name)
    res = list(cloud_region.tenants)
    assert len(res) == 1
    assert isinstance(res[0], Tenant)
    tenant = res[0]
    assert tenant.tenant_id == "4bdc6f0f2539430f9428c852ba606808"
    assert tenant.name == "onap-dublin-daily-vnfs"
    assert tenant.context is None
    assert tenant.resource_version == "1562591004273"
    assert tenant.url == (
        f"{tenant.base_url}{tenant.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
        f"OPNFV/RegionOne/tenants/tenant/4bdc6f0f2539430f9428c852ba606808?"
        f"resource-version=1562591004273"
    )

@mock.patch.object(CloudRegion, 'get_all')
@mock.patch.object(AaiElement, 'send_message_json')
def test_tenants_info_wrong_cloud_name(mock_send, mock_cloud_regions):
    """Test get Tenant from A&AI."""
    mock_cloud_regions.return_value = CLOUD_REGIONS_ITERATOR
    mock_send.return_value = TENANT
    cloud_name = "Wrong_cloud_name"
    with pytest.raises(Exception) as excinfo:
        CloudRegion.get_by_id("DT", cloud_name)
    assert "not found" in str(excinfo.value)


@mock.patch.object(CloudRegion, "send_message_json")
def test_cloud_regions_relationship(mock_send):
    """Test cloud region relationship property."""
    mock_send.return_value = CLOUD_REGION_RELATIONSHIP
    cloud_region = CloudRegion(cloud_owner="tester", cloud_region_id="test",
                               orchestration_disabled=True, in_maint=False)
    relationship = next(cloud_region.relationships)
    assert isinstance(relationship, Relationship)
    assert relationship.relationship_label == "org.onap.relationships.inventory.LocatedIn"
    assert relationship.related_link == \
        "/aai/v16/cloud-infrastructure/complexes/complex/integration_test_complex"
    assert relationship.related_to == "complex"
    assert relationship.relationship_data[0]["relationship-key"] == "complex.physical-location-id"
    assert relationship.relationship_data[0]["relationship-value"] == "integration_test_complex"


@mock.patch.object(CloudRegion, "send_message_json")
def test_cloud_regions_esr_system_infos(mock_send):
    """Test cloud region esr system info"""
    mock_send.return_value = ESR_SYSTEM_INFO
    cloud_region = CloudRegion(cloud_owner="tester", cloud_region_id="test",
                               orchestration_disabled=True, in_maint=False)
    esr_system_info = next(cloud_region.esr_system_infos)
    assert isinstance(esr_system_info, EsrSystemInfo)
    assert esr_system_info.esr_system_info_id == "c2d5e75d-56fd-47bc-af31-95607b26fa93"
    assert esr_system_info.user_name == "test-devel"
    assert esr_system_info.password == "test-devel"
    assert esr_system_info.system_type == "openstack"
    assert esr_system_info.resource_version == "1586436352654"
    assert esr_system_info.system_name is None
    assert esr_system_info.esr_type is None
    assert esr_system_info.vendor is None
    assert esr_system_info.version is None
    assert esr_system_info.service_url == "http://keystone:5000/v3"
    assert esr_system_info.protocol is None
    assert esr_system_info.ssl_cacert is None
    assert esr_system_info.ssl_insecure is None
    assert esr_system_info.ip_address is None
    assert esr_system_info.port is None
    assert esr_system_info.cloud_domain == "Default"
    assert esr_system_info.default_tenant is None
    assert esr_system_info.passive is None
    assert esr_system_info.remote_path is None
    assert esr_system_info.system_status is None
    assert esr_system_info.openstack_region_id is None

@mock.patch.object(Complex, "send_message")
def test_create_complex(mock_send):
    """Test complex creation"""
    cmplx = Complex.create(
        name="test complex",
        physical_location_id="somewhere",
        data_center_code="5555",
        physical_location_type="test",
        city="Test City",
        postal_code="55555",
        region="Test region",
        elevation="TestElevation",
    )

    assert cmplx.name == "test complex"
    assert cmplx.physical_location_id == "somewhere"
    assert cmplx.identity_url == ""
    assert cmplx.physical_location_type == "test"
    assert cmplx.street1 == ""
    assert cmplx.street2 == ""
    assert cmplx.city == "Test City"
    assert cmplx.state == ""
    assert cmplx.postal_code == "55555"
    assert cmplx.country == ""
    assert cmplx.region == "Test region"
    assert cmplx.latitude == ""
    assert cmplx.longitude == ""
    assert cmplx.elevation == "TestElevation"
    assert cmplx.lata == ""


@mock.patch.object(Complex, "send_message_json")
def text_get_all_complexes(mock_send):
    """Test get_all Complex class method."""
    mock_send.return_value = {}
    assert len(list(Complex.get_all())) == 0

    mock_send.return_value = COMPLEXES
    assert len(list(Complex.get_all())) == 2


def test_filter_none_value():
    """Test method to filter out None value keys from dictionary."""
    ret: dict = AaiElement.filter_none_key_values({"a": None})
    assert not ret

    ret: dict = AaiElement.filter_none_key_values({"a": "b", "c": None})
    assert ret == {"a": "b"}

    ret: dict = AaiElement.filter_none_key_values({"a": "b", "c": "d"})
    assert ret == {"a": "b", "c": "d"}


@mock.patch.object(AaiElement, "send_message")
def test_add_relationship(mock_send):
    """Test add_relationship method."""
    cloud_region = CloudRegion(cloud_owner="tester", cloud_region_id="test",
                               orchestration_disabled=True, in_maint=False)
    cloud_region.add_relationship(Relationship(related_to="test",
                                               related_link="test",
                                               relationship_data={}))


# # -----------------------------------------------------------------------------
# def test_check_aai_resource_service():
#     """Test that a given service instance is in A&AI."""
#     pass

# def test_check_aai_resource_service_not_found():
#     """Test that a given service instance is not in A&AI (cleaned)."""
#     pass

# def test_check_aai_resource_vnf():
#     """Test that a given vnf is in A&AI."""
#     pass

# def test_check_aai_resource_vnf_not_found():
#     """Test that a given vnf is not in A&AI (cleaned)."""
#     pass

# def test_check_aai_resource_module():
#     """Test that a given module is in A&AI."""
#     pass

# def test_check_aai_resource_module_not_found():
#     """Test that a given module is not in A&AI (cleaned)."""
#     pass

# def test_check_aai_net_module():
#     """Test that a given net is in A&AI."""
#     pass

# def test_check_aai_resource_net_not_found():
#     """Test that a given net is not in A&AI (cleaned)."""
#     pass


# pylint: disable=C0301
SIMPLE_MODEL = {
    "model": [
        {
            "model-invariant-id": "1234567890",
            "model-type": "generic",
            "resource-version": "1561218640404",
        }
    ]
}
# pylint: enable=C0301


def test_service_url():
    """Test service property"""
    service = Service("12345", "description", "version1.0")
    assert service.url == (f"{service.base_url}{service.api_version}/service-design-and-creation/services/service/"
                f"{service.service_id}?resource-version={service.resource_version}")


@mock.patch.object(Service, 'send_message')
def test_service_create(mock_send):
    """Test service creation"""
    Service.create("1234", "description")
    mock_send.assert_called_once()
    method, description, url = mock_send.call_args[0]
    assert method == "PUT"
    assert description == "Create A&AI service"
    assert url == (f"{Service.base_url}{Service.api_version}/service-design-and-creation/"
                   f"services/service/1234")


def test_model_init():
    """Test model initailization"""
    model = Model("12345", "ubuntu", "version16")
    assert isinstance(model, Model)


def test_model_url():
    """Test Model's url property"""
    model = Model("12345", "ubuntu", "version16")
    assert model.url == (f"{model.base_url}{model.api_version}/service-design-and-creation/models/"
                         f"model/{model.invariant_id}?resource-version={model.resource_version}")


@mock.patch.object(Model, 'send_message_json')
def test_zero_model_get_all(mock_send_message_json):
    """Test get_all Model class method"""
    mock_send_message_json.return_value = {}
    Model.get_all()
    assert len(list(Model.get_all())) == 0


@mock.patch.object(Model, 'send_message_json')
def test_model_get_all(mock_send_message_json):
    """Test get_all Model class method"""
    mock_send_message_json.return_value = SIMPLE_MODEL
    Model.get_all()
    assert len(list(Model.get_all())) == 1
    model_1 = next(Model.get_all())
    assert model_1.invariant_id == "1234567890"
    assert model_1.model_type == "generic"
    assert model_1.resource_version == "1561218640404"
    mock_send_message_json.assert_called_with("GET", 'Get A&AI sdc models', mock.ANY)