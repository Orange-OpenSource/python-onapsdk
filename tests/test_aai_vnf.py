#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI VNF module."""

from unittest import mock

import pytest

from onapsdk.aai.business import ServiceInstance, VnfInstance
from onapsdk.so.deletion import VnfDeletionRequest
from onapsdk.so.instantiation import VfModuleInstantiation
from onapsdk.exceptions import ResourceNotFound


VNF_INSTANCE = {
    "vnf-id":"6d644ab5-254d-4a49-98fe-0f481c099f1a",
    "vnf-name":"Python_ONAP_SDK_vnf_instance_14856120-e946-46ce-bf5f-384b20209f9c",
    "vnf-type":"testService11/testVF11 0",
    "service-id":"1234",
    "prov-status":"PREPROV",
    "orchestration-status":"Inventoried",
    "in-maint":True,
    "is-closed-loop-disabled":False,
    "resource-version":"1590395148980",
    "model-invariant-id":"a3285832-77d5-4ab2-95c5-217070de77c9",
    "model-version-id":"0da841b9-f787-4ce0-9227-a23092a4a035",
    "model-customization-id":"9426293e-bc5d-4fd3-8236-85190f1142aa",
    "selflink":"restconf/config/GENERIC-RESOURCE-API:services/service/5410bf79-2aa3-450e-a324-ec5630dc18cf/service-data/vnfs/vnf/6d644ab5-254d-4a49-98fe-0f481c099f1a/vnf-data/vnf-topology/",
    "relationship-list":{
        "relationship":[
            {
                "related-to":"tenant",
                "relationship-label":"org.onap.relationships.inventory.BelongsTo",
                "related-link":"/aai/v19/cloud-infrastructure/cloud-regions/cloud-region/DT/RegionOne/tenants/tenant/89788fdf49514f94963b12a6c0cfdc71",
                "relationship-data":[
                    {
                        "relationship-key":"cloud-region.cloud-owner",
                        "relationship-value":"DT"
                    },
                    {
                        "relationship-key":"cloud-region.cloud-region-id",
                        "relationship-value":"RegionOne"
                    },
                    {
                        "relationship-key":"tenant.tenant-id",
                        "relationship-value":"89788fdf49514f94963b12a6c0cfdc71"
                    }
                ],
                "related-to-property":[
                    {
                        "property-key":"tenant.tenant-name",
                        "property-value":"onap-devel"
                    }
                ]
            },
            {
                "related-to":"cloud-region",
                "relationship-label":"org.onap.relationships.inventory.LocatedIn",
                "related-link":"/aai/v19/cloud-infrastructure/cloud-regions/cloud-region/DT/RegionOne",
                "relationship-data":[
                    {
                        "relationship-key":"cloud-region.cloud-owner",
                        "relationship-value":"DT"
                    },{
                        "relationship-key":"cloud-region.cloud-region-id",
                        "relationship-value":"RegionOne"
                    }
                ],
                "related-to-property":[
                    {
                        "property-key":"cloud-region.owner-defined-type",
                        "property-value":""
                    }
                ]
            },
            {
                "related-to":"service-instance",
                "relationship-label":"org.onap.relationships.inventory.ComposedOf",
                "related-link":"/aai/v19/business/customers/customer/generic/service-subscriptions/service-subscription/testService11/service-instances/service-instance/5410bf79-2aa3-450e-a324-ec5630dc18cf",
                "relationship-data":[
                    {
                        "relationship-key":"customer.global-customer-id",
                        "relationship-value":"generic"
                    },
                    {
                        "relationship-key":"service-subscription.service-type",
                        "relationship-value":"testService11"
                    },
                    {
                        "relationship-key":"service-instance.service-instance-id",
                        "relationship-value":"5410bf79-2aa3-450e-a324-ec5630dc18cf"
                    }
                ],
                "related-to-property":[
                    {
                        "property-key":"service-instance.service-instance-name",
                        "property-value":"test22"
                    }
                ]
            },
            {
                "related-to":"availability-zone",
                "relationship-label":"org.onap.relationships.inventory.Uses",
                "related-link":"/aai/v19/cloud-infrastructure/cloud-regions/cloud-region/DT/RegionOne/availability-zones/availability-zone/nova",
                "relationship-data":[
                    {
                        "relationship-key":"cloud-region.cloud-owner",
                        "relationship-value":"DT"
                    },
                    {
                        "relationship-key":"cloud-region.cloud-region-id",
                        "relationship-value":"RegionOne"
                    },
                    {
                        "relationship-key":"availability-zone.availability-zone-name",
                        "relationship-value":"nova"
                    }
                ]
            },
            {
                "related-to":"availability-zone",
                "relationship-label":"org.onap.relationships.inventory.Uses",
                "related-link":"/aai/v19/cloud-infrastructure/cloud-regions/cloud-region/DT/RegionOne/availability-zones/availability-zone/brittany",
                "relationship-data":[
                    {
                        "relationship-key":"cloud-region.cloud-owner",
                        "relationship-value":"DT"
                    },
                    {
                        "relationship-key":"cloud-region.cloud-region-id",
                        "relationship-value":"RegionOne"
                    },
                    {
                        "relationship-key":"availability-zone.availability-zone-name",
                        "relationship-value":"brittany"
                    }
                ]
            },
            {
                "related-to":"platform",
                "relationship-label":"org.onap.relationships.inventory.Uses",
                "related-link":"/aai/v19/business/platforms/platform/Python_ONAPSDK_Platform",
                "relationship-data":[
                    {
                        "relationship-key":"platform.platform-name",
                        "relationship-value":"Python_ONAPSDK_Platform"
                    }
                ]
            },
            {
                "related-to":"line-of-business",
                "relationship-label":"org.onap.relationships.inventory.Uses",
                "related-link":"/aai/v19/business/lines-of-business/line-of-business/Python_ONAPSDK_LineOfBusiness",
                "relationship-data":[
                    {
                        "relationship-key":"line-of-business.line-of-business-name",
                        "relationship-value":"Python_ONAPSDK_LineOfBusiness"
                    }
                ]
            }
        ]
    }
}


VF_MODULE = {
    "vf-module": [
        {
            "vf-module-id": "test-module-id",
            "is-base-vf-module": True,
            "automated-assignment": False,
            "vf-module-name": "test_vf_module",
            "heat-stack-id": "test_heat_stack_id",
            "orchestration-status": "test_orchestration_status",
            "resource-version": "1590395148980",
            "model-invariant-id": "test_model_invariant_id",
            "model-version-id": "test_model_version_id"
        }
    ]
}


@mock.patch.object(VnfDeletionRequest, "send_request")
def test_vnf_instance(mock_vnf_deletion_request):
    service_instance = ServiceInstance(None,
                                       instance_id="test_service_instance_id")
    vnf_instance = VnfInstance(service_instance,
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True)
    assert vnf_instance.service_instance == service_instance
    assert vnf_instance.vnf_id == "test_vnf_id"
    assert vnf_instance.vnf_type == "test_vnf_type"
    assert vnf_instance.in_maint is False
    assert vnf_instance.is_closed_loop_disabled is True
    assert vnf_instance._vnf is None
    assert vnf_instance.url == (f"{vnf_instance.base_url}{vnf_instance.api_version}/network/"
                                f"generic-vnfs/generic-vnf/{vnf_instance.vnf_id}")
    vnf_instance.delete()
    mock_vnf_deletion_request.assert_called_once_with(vnf_instance, True)


@mock.patch.object(VnfInstance, "send_message_json")
def test_vnf_instance_vf_modules(mock_vnf_instance_send_message_json):
    service_instance = mock.MagicMock()
    vnf_instance = VnfInstance(service_instance,
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True)
    mock_vnf_instance_send_message_json.return_value = {"vf-module": []}
    vf_modules = list(vnf_instance.vf_modules)
    assert len(vf_modules) == 0

    mock_vnf_instance_send_message_json.return_value = VF_MODULE
    vf_modules = list(vnf_instance.vf_modules)
    assert len(vf_modules) == 1


def test_vnf_instance_vnf():
    service_instance = mock.MagicMock()
    vnf_instance = VnfInstance(service_instance,
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True,
                               model_version_id="test_model_version_id")
    assert vnf_instance._vnf is None
    service_instance.service_subscription.sdc_service.vnfs = []
    with pytest.raises(ResourceNotFound) as exc:
        vnf_instance.vnf
    assert exc.type == ResourceNotFound
    assert vnf_instance._vnf is None

    vnf = mock.MagicMock()
    vnf.model_version_id = "test_model_version_id"
    service_instance.service_subscription.sdc_service.vnfs = [vnf]
    assert vnf == vnf_instance.vnf
    assert vnf_instance._vnf is not None
    assert vnf_instance.vnf == vnf_instance._vnf


@mock.patch.object(VfModuleInstantiation, "instantiate_ala_carte")
def test_vnf_add_vf_module(mock_vf_module_instantiation):
    vnf_instance = VnfInstance(mock.MagicMock(),
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True,
                               model_version_id="test_model_version_id")
    vnf_instance.add_vf_module(mock.MagicMock())
    mock_vf_module_instantiation.assert_called_once()
