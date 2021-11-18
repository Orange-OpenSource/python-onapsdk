import time
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import requests
from onapsdk.exceptions import StatusError
from onapsdk.aai.business import Customer, ServiceInstance
from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings
from onapsdk.sdc.service import Service, Vnf, VfModule
from onapsdk.so.deletion import ServiceDeletionRequest, VfModuleDeletionRequest, VnfDeletionRequest
from onapsdk.so.instantiation import (ServiceInstantiation, SoService,
                                      VfModuleInstantiation, VnfInstantiation, InstantiationParameter,
                                      VfmoduleParameters, VnfParameters)


@pytest.mark.integration
def test_a_la_carte_instantiation():
    requests.get(f"{ServiceInstantiation.base_url}/reset")
    requests.get(f"{Customer.base_url}/reset")
    requests.post(f"{ServiceInstantiation.base_url}/set_aai_mock", json={"AAI_MOCK": settings.AAI_URL})

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    service = Service("test_service")
    service.unique_uuid = str(uuid4())
    service.identifier = str(uuid4())
    service.name = str(uuid4())
    customer.subscribe_service("service_type")
    service_subscription = customer.get_service_subscription_by_service_type("service_type")
    cloud_region = CloudRegion.create(
        "test_owner", "test_cloud_region", orchestration_disabled=True, in_maint=False
    )
    cloud_region.add_tenant(
        tenant_id="test_tenant_name", tenant_name="test_tenant_name", tenant_context="test_tenant_context"
    )
    tenant = cloud_region.get_tenant(tenant_id="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
    owning_entity = "test_owning_entity"
    project = "test_project"

    # Service instantiation
    service._distributed = True
    assert len(list(service_subscription.service_instances)) == 0
    service_instantiation_request = ServiceInstantiation.instantiate_ala_carte(
        service,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        project,
        service_subscription
    )
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 1

    # Vnf instantiation
    service_instance = next(service_subscription.service_instances)
    assert len(list(service_instance.vnf_instances)) == 0
    owning_entity = "test_owning_entity"
    project = "test_project"
    vnf = MagicMock()
    line_of_business = "test_line_of_business"
    platform = "test_platform"
    with pytest.raises(StatusError):
        service_instance.add_vnf(
            vnf,
            line_of_business,
            platform
        )
    service_instance.orchestration_status = "Active"
    service_instance._sdc_service = service
    with patch.object(ServiceInstance, "sdc_service", return_value=service):
        vnf_instantiation_request = service_instance.add_vnf(
            vnf,
            line_of_business,
            platform
        )
    assert vnf_instantiation_request.status == VnfInstantiation.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert vnf_instantiation_request.status == VnfInstantiation.StatusEnum.COMPLETED
    assert len(list(service_instance.vnf_instances)) == 1
    # VfModule instantiation
    vnf_instance = next(service_instance.vnf_instances)
    assert len(list(vnf_instance.vf_modules)) == 0
    vnf.metadata = {"UUID": vnf_instance.model_version_id}
    vf_module = MagicMock()

    with patch.object(ServiceInstance, "sdc_service", return_value=service) as service_mock:
        service_mock.vnfs = [vnf]
        vf_module_instantiation_request = vnf_instance.add_vf_module(
            vf_module
        )
    assert vf_module_instantiation_request.status == VfModuleInstantiation.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert vf_module_instantiation_request.status == VfModuleInstantiation.StatusEnum.COMPLETED
    assert len(list(vnf_instance.vf_modules)) == 1

    # Cleanup
    vf_module_instance = next(vnf_instance.vf_modules)
    vf_module_deletion_request = vf_module_instance.delete()
    assert vf_module_deletion_request.status == VfModuleDeletionRequest.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert vf_module_deletion_request.status == VfModuleDeletionRequest.StatusEnum.COMPLETED
    assert len(list(vnf_instance.vf_modules)) == 0

    vnf_deletion_request = vnf_instance.delete()
    assert vnf_deletion_request.status == VnfDeletionRequest.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert vnf_deletion_request.status == VnfDeletionRequest.StatusEnum.COMPLETED
    assert len(list(service_instance.vnf_instances)) == 0

    with patch.object(ServiceInstance, "sdc_service", return_value=service) as service_mock:
        service_deletion_request = service_instance.delete()
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 0


@pytest.mark.integration
def test_a_la_carte_vl_instantiation():
    requests.get(f"{ServiceInstantiation.base_url}/reset")
    requests.get(f"{Customer.base_url}/reset")
    requests.post(f"{ServiceInstantiation.base_url}/set_aai_mock", json={"AAI_MOCK": settings.AAI_URL})

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    service = Service("test_service")
    service.unique_uuid = str(uuid4())
    service.identifier = str(uuid4())
    service.name = str(uuid4())
    customer.subscribe_service("service_type")
    service_subscription = customer.get_service_subscription_by_service_type("service_type")
    cloud_region = CloudRegion.create(
        "test_owner", "test_cloud_region", orchestration_disabled=True, in_maint=False
    )
    cloud_region.add_tenant(
        tenant_id="test_tenant_name", tenant_name="test_tenant_name", tenant_context="test_tenant_context"
    )
    tenant = cloud_region.get_tenant(tenant_id="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
    owning_entity = "test_owning_entity"
    project = "test_project"

    # Service instantiation
    service._distributed = True
    assert len(list(service_subscription.service_instances)) == 0
    service_instantiation_request = ServiceInstantiation.instantiate_ala_carte(
        service,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        project,
        service_subscription
    )
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.IN_PROGRESS
    service_instantiation_request.wait_for_finish()
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 1

    # Network instantiation
    service_instance = next(service_subscription.service_instances)
    assert len(list(service_instance.network_instances)) == 0
    owning_entity = "test_owning_entity"
    project = "test_project"
    network = MagicMock()
    line_of_business = "test_line_of_business"
    platform = "test_platform"
    with pytest.raises(AttributeError):
        service_instance.network(
            network,
            line_of_business,
            platform
        )
    service_instance.orchestration_status = "Active"
    with patch.object(ServiceInstance, "sdc_service", return_value=service):
        network_instantiation_request = service_instance.add_network(
            network,
            line_of_business,
            platform
        )
    assert network_instantiation_request.status == VnfInstantiation.StatusEnum.IN_PROGRESS
    network_instantiation_request.wait_for_finish()
    assert network_instantiation_request.status == VnfInstantiation.StatusEnum.COMPLETED
    assert len(list(service_instance.network_instances)) == 1


@pytest.mark.integration
def test_instantiate_macro():
    requests.get(f"{ServiceInstantiation.base_url}/reset")
    requests.get(f"{Customer.base_url}/reset")
    requests.post(f"{ServiceInstantiation.base_url}/set_aai_mock", json={"AAI_MOCK": settings.AAI_URL})

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    service = Service("test_service")
    service._tosca_template = "n/a"
    service._vnfs = [
        Vnf(
            name="test_vnf",
            node_template_type="vf",
            metadata={
                "name": "test_vnf_model",
                "UUID": str(uuid4()),
                "invariantUUID": str(uuid4()),
                "version": "1.0",
                "customizationUUID": str(uuid4())
            },
            properties={},
            capabilities={},
            vf_modules=[
                VfModule(
                    name="TestVnfModel..base..module-0",
                    group_type="vf-module",
                    metadata={
                        "vfModuleModelName": "TestVnfModel..base..module-0",
                        "vfModuleModelUUID": str(uuid4()),
                        "vfModuleModelInvariantUUID": str(uuid4()),
                        "vfModuleModelVersion": "1",
                        "vfModuleModelCustomizationUUID": str(uuid4())
                    },
                    properties={}
                )
            ]
        )
    ]
    service.unique_uuid = str(uuid4())
    service.identifier = str(uuid4())
    service.name = str(uuid4())
    customer.subscribe_service("service_type")
    service_subscription = customer.get_service_subscription_by_service_type("service_type")
    cloud_region = CloudRegion.create(
        "test_owner", "test_cloud_region", orchestration_disabled=True, in_maint=False
    )
    cloud_region.add_tenant(
        tenant_id="test_tenant_name", tenant_name="test_tenant_name", tenant_context="test_tenant_context"
    )
    tenant = cloud_region.get_tenant(tenant_id="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
    owning_entity = "test_owning_entity"
    project = "test_project"
    line_of_business = "test_line_of_business"
    platform = "test_platform"

    vfm_instance_params = [
        InstantiationParameter(name="vfm_param", value="vfm_param_value"),

    ]
    vfm_params = VfmoduleParameters("base", vfm_instance_params)

    vnf_instance_params = [
        InstantiationParameter(name="vnf_param", value="vnf_param_value")
    ]

    vnf_params = VnfParameters("test_vnf_model", vnf_instance_params, [vfm_params])

    # Service instantiation
    service._distributed = True
    assert len(list(service_subscription.service_instances)) == 0
    service_instantiation_request = ServiceInstantiation.instantiate_macro(
        sdc_service=service,
        customer=customer,
        owning_entity=owning_entity,
        project=project,
        line_of_business=line_of_business,
        platform=platform,
        cloud_region=cloud_region,
        tenant=tenant,
        vnf_parameters=[vnf_params],
        service_subscription=service_subscription
    )
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 1
    service_instance = next(service_subscription.service_instances)

    # Cleanup
    with patch.object(ServiceInstance, "sdc_service", return_value=service) as service_mock:
        service_deletion_request = service_instance.delete()
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 0

@pytest.mark.integration
def test_instantiate_macro_multiple_vnf():
    requests.get(f"{ServiceInstantiation.base_url}/reset")
    requests.get(f"{Customer.base_url}/reset")
    requests.post(f"{ServiceInstantiation.base_url}/set_aai_mock", json={"AAI_MOCK": settings.AAI_URL})

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    service = Service("test_service")
    service._tosca_template = "n/a"
    service._vnfs = [
        Vnf(
            name="test_vnf",
            node_template_type="vf",
            metadata={
                "name": "test_vnf_model",
                "UUID": str(uuid4()),
                "invariantUUID": str(uuid4()),
                "version": "1.0",
                "customizationUUID": str(uuid4())
            },
            properties={},
            capabilities={},
            vf_modules=[
                VfModule(
                    name="TestVnfModel..base..module-0",
                    group_type="vf-module",
                    metadata={
                        "vfModuleModelName": "TestVnfModel..base..module-0",
                        "vfModuleModelUUID": str(uuid4()),
                        "vfModuleModelInvariantUUID": str(uuid4()),
                        "vfModuleModelVersion": "1",
                        "vfModuleModelCustomizationUUID": str(uuid4())
                    },
                    properties={}
                )
            ]
        )
    ]
    service.unique_uuid = str(uuid4())
    service.identifier = str(uuid4())
    service.name = str(uuid4())
    customer.subscribe_service("service_type")
    service_subscription = customer.get_service_subscription_by_service_type("service_type")
    cloud_region = CloudRegion.create(
        "test_owner", "test_cloud_region", orchestration_disabled=True, in_maint=False
    )
    cloud_region.add_tenant(
        tenant_id="test_tenant_name", tenant_name="test_tenant_name", tenant_context="test_tenant_context"
    )
    tenant = cloud_region.get_tenant(tenant_id="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
    owning_entity = "test_owning_entity"
    project = "test_project"
    line_of_business = "test_line_of_business"
    platform = "test_platform"

    so_service = SoService.load({
        "subscription_service_type": "service_type",
        "vnfs": [
            {
                "model_name": "test_vnf_model",
                "instance_name": "vnf0",
                "parameters": {
                    "param1": "value1"
                },
                "vf_modules": [
                    {
                        "instance_name": "vnf0_vfm0",
                        "model_name": "base",
                        "parameters": {
                            "vfm_param1": "vfm_value1"
                        }
                    }
                ]
            },
            {
                "model_name": "test_vnf_model",
                "instance_name": "vnf1",
                "parameters": {
                    "param2": "value2"
                },
                "vf_modules": [
                    {
                        "instance_name": "vnf1_vfm0",
                        "model_name": "base",
                        "parameters": {
                            "vfm_param2": "vfm_value2"
                        }
                    }
                ]
            }
        ]
    })

    # Service instantiation
    service._distributed = True
    assert len(list(service_subscription.service_instances)) == 0
    service_instantiation_request = ServiceInstantiation.instantiate_macro(
        sdc_service=service,
        customer=customer,
        owning_entity=owning_entity,
        project=project,
        line_of_business=line_of_business,
        platform=platform,
        cloud_region=cloud_region,
        tenant=tenant,
        so_service=so_service
    )
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 1
    service_instance = next(service_subscription.service_instances)

    # Cleanup
    with patch.object(ServiceInstance, "sdc_service", return_value=service) as service_mock:
        service_deletion_request = service_instance.delete()
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 0
