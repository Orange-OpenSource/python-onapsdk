#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI VNF module."""

from unittest import mock

import pytest

from onapsdk.aai.aai_element import AaiElement
from onapsdk.aai.business import ServiceInstance, VnfInstance, PnfInstance, VfModuleInstance
from onapsdk.so.deletion import VnfDeletionRequest
from onapsdk.so.instantiation import VfModuleInstantiation, VnfInstantiation, SoService
from onapsdk.exceptions import ResourceNotFound, StatusError


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
    service_instance.sdc_service.vnfs = []
    with pytest.raises(ResourceNotFound) as exc:
        vnf_instance.vnf
    assert exc.type == ResourceNotFound
    assert vnf_instance._vnf is None

    vnf = mock.MagicMock()
    vnf.model_version_id = "test_model_version_id"
    service_instance.sdc_service.vnfs = [vnf]
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


@mock.patch.object(VnfInstance, "_execute_so_action")
@mock.patch.object(VnfInstance, "vnf")
def test_vnf_update(mock_vnf, mock_vnf_instantiation):

    property_skip_true = mock.MagicMock()
    property_skip_true.name = "skip_post_instantiation_configuration"
    property_skip_true.value = "false"

    vnf_instance = mock.MagicMock()
    vnf_instance.vnf = mock_vnf
    vnf_instance.vnf.properties = (item for item in [property_skip_true])

    vnf_instance = VnfInstance(vnf_instance,
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True)

    vnf_instance.update([mock.MagicMock()])
    mock_vnf_instantiation.assert_called_once()

    property_skip_false = mock.MagicMock()
    property_skip_false.name = "skip_post_instantiation_configuration"
    property_skip_false.value = "true"

    vnf_instance2 = mock.MagicMock()
    vnf_instance2.vnf = mock_vnf
    vnf_instance2.vnf.properties = (item for item in [property_skip_false])

    vnf_instance2 = VnfInstance(vnf_instance2,
                                vnf_id="test_vnf_id",
                                vnf_type="test_vnf_type",
                                in_maint=False,
                                is_closed_loop_disabled=True)

    with pytest.raises(StatusError):
        vnf_instance2.update([mock.MagicMock()])


@mock.patch.object(VnfInstance, "_execute_so_action")
def test_vnf_healthcheck(mock_vnf_instantiation):

    instance = mock.MagicMock()
    vnf_instance = VnfInstance(instance,
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True)

    vnf_instance.healthcheck()
    mock_vnf_instantiation.assert_called_once()


@mock.patch.object(VnfInstance, "_build_so_input")
@mock.patch.object(VnfInstantiation, "so_action")
def test_vnf_execute_so_action(mock_build_so_input, mock_so_action):

    instance = mock.MagicMock()

    relation_1 = mock.MagicMock()
    relation_1.related_to = "line-of-business"
    relation_1.relationship_data = [{"relationship-value": "test"}]
    relation_2 = mock.MagicMock()
    relation_2.related_to = "platform"
    relation_2.relationship_data = [{"relationship-value": "test"}]

    vnf_instance = VnfInstance(instance,
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True)

    vnf_instance.service_instance = mock.MagicMock()
    vnf_instance.service_instance.active = True

    type(vnf_instance).relationships = mock.PropertyMock(return_value=[relation_1, relation_2])

    vnf_instance._execute_so_action(operation_type="test",
                                    vnf_parameters=[mock.MagicMock()])
    mock_so_action.assert_called_once()

    vnf_instance.service_instance.active = False
    with pytest.raises(StatusError):
        vnf_instance._execute_so_action(operation_type="test",
                                        vnf_parameters=[mock.MagicMock()])


@mock.patch.object(VnfInstance, "send_message")
def test_build_so_input(mock_send_message):

    pnf = mock.MagicMock()
    pnf.model_version_id = "test_pnf_model_version_id"
    pnf.model_name = "test_model"

    vnf = mock.MagicMock()
    vnf.model_version_id = "test_vnf_model_version_id"
    vnf.model_name = "vnf_test_model"

    vf_module = mock.MagicMock()
    vf_module.model_version_id = "test_vfm_model_version_id"
    vf_module.model_name = "test..vfm_model..name"

    vnf.vf_modules = [vf_module]

    instance = mock.MagicMock()
    instance.service_subscription = mock.MagicMock()
    instance.service_subscription.service_type = "1234"

    instance.sdc_service.pnfs = [pnf]
    instance.sdc_service.vnfs = [vnf]

    pnf_instance = PnfInstance(instance,
                               pnf_name="test_pnf",
                               in_maint=False,
                               model_version_id="test_pnf_model_version_id")

    vnf_instance = VnfInstance(instance,
                               vnf_name="test_name",
                               vnf_id="test_vnf_id",
                               vnf_type="test_vnf_type",
                               in_maint=False,
                               is_closed_loop_disabled=True,
                               model_version_id="test_vnf_model_version_id")

    vf_module_instance = VfModuleInstance(vnf_instance=vnf_instance,
                                          vf_module_name="test_vfm_name",
                                          model_version_id="test_vfm_model_version_id",
                                          vf_module_id="test_vf_module_id",
                                          is_base_vf_module=True,
                                          automated_assignment=False)

    vnf_instance.vnf.vf_modules = [vf_module]
    type(vnf_instance).vf_modules = mock.PropertyMock(return_value=[vf_module_instance])
    instance.pnfs = [pnf_instance]
    instance.vnf_instances = [vnf_instance]

    test_so_input_no_params = vnf_instance._build_so_input()

    assert isinstance(test_so_input_no_params, SoService)
    assert len(test_so_input_no_params.vnfs[0].parameters) == 0

    vnf_param1 = mock.MagicMock()
    vnf_param1.name = "test_name"
    vnf_param1.value = "test_value"

    test_so_input = vnf_instance._build_so_input([vnf_param1])

    assert isinstance(test_so_input, SoService)
    assert test_so_input.subscription_service_type == "1234"
    assert not test_so_input.instance_name
    assert len(test_so_input.vnfs) == 1

    test_so_input_vnf = test_so_input.vnfs[0]

    assert test_so_input_vnf.model_name == "vnf_test_model"
    assert test_so_input_vnf.instance_name == "test_name"
    assert len(test_so_input_vnf.parameters) == 1
    assert test_so_input_vnf.parameters["test_name"] == "test_value"
    assert len(test_so_input_vnf.vf_modules) == 1

    test_so_input_vnf_vf_module = test_so_input_vnf.vf_modules[0]

    assert test_so_input_vnf_vf_module.model_name == "vfm_model"
    assert test_so_input_vnf_vf_module.instance_name == "test_vfm_name"
    assert len(test_so_input_vnf_vf_module.parameters) == 0

    assert len(test_so_input.pnfs) == 1
    assert test_so_input.pnfs[0].model_name == "test_model"
    assert test_so_input.pnfs[0].instance_name == "test_pnf"
