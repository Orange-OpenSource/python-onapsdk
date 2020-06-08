import time
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import requests
from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription, VnfInstance
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.sdnc.preload import VfModulePreload
from onapsdk.service import Service
from onapsdk.so.deletion import ServiceDeletionRequest, VfModuleDeletionRequest, VnfDeletionRequest
from onapsdk.so.instantiation import (ServiceInstantiation,
                                      VfModuleInstantiation, VnfInstantiation)
from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project

from .urls import AAI_MOCK_URL, SO_MOCK_URL, SDNC_MOCK_URL


@pytest.mark.integration
def test_a_la_carte_instantiation():
    Customer.base_url = AAI_MOCK_URL
    CloudRegion.base_url = AAI_MOCK_URL
    ServiceSubscription.base_url = AAI_MOCK_URL
    ServiceInstance.base_url = AAI_MOCK_URL
    VnfInstance.base_url = AAI_MOCK_URL
    ServiceInstantiation.base_url = SO_MOCK_URL
    VnfInstantiation.base_url = SO_MOCK_URL
    VfModuleInstantiation.base_url = SO_MOCK_URL
    VfModulePreload.base_url = SDNC_MOCK_URL
    ServiceDeletionRequest.base_url = SO_MOCK_URL
    VfModuleDeletionRequest.base_url = SO_MOCK_URL
    VnfDeletionRequest.base_url = SO_MOCK_URL

    requests.get(f"{ServiceInstantiation.base_url}/reset")
    requests.get(f"{Customer.base_url}/reset")
    requests.post(f"{ServiceInstantiation.base_url}/set_aai_mock", json={"AAI_MOCK": AAI_MOCK_URL})

    customer = Customer.create(global_customer_id="test_global_customer_id",
                               subscriber_name="test_subscriber_name",
                               subscriber_type="test_subscriber_type")
    service = Service("test_service")
    service.unique_uuid = str(uuid4())
    service.identifier = str(uuid4())
    service.name = str(uuid4())
    customer.subscribe_service(service)
    service_subscription = customer.get_service_subscription_by_service_type(service.name)
    cloud_region = CloudRegion.create(
        "test_owner", "test_cloud_region", orchestration_disabled=True, in_maint=False
    )
    cloud_region.add_tenant(
        tenant_id="test_tenant_name", tenant_name="test_tenant_name", tenant_context="test_tenant_context"
    )
    tenant = cloud_region.get_tenant(tenant_id="test_tenant_name")
    service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
    owning_entity = OwningEntity(name="test_owning_entity")
    project = Project(name="test_project")

    # Service instantiation
    service._distributed = True
    assert len(list(service_subscription.service_instances)) == 0
    service_instantiation_request = ServiceInstantiation.instantiate_so_ala_carte(
        service,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        project
    )
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_instantiation_request.status == ServiceInstantiation.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 1

    # Vnf instantiation
    service_instance = next(service_subscription.service_instances)
    assert len(list(service_instance.vnf_instances)) == 0
    owning_entity = OwningEntity(name="test_owning_entity")
    project = Project(name="test_project")
    vnf = MagicMock()
    line_of_business = LineOfBusiness(name="test_line_of_business")
    platform = Platform(name="test_platform")
    with pytest.raises(AttributeError):
        service_instance.add_vnf(
            vnf,
            line_of_business,
            platform
        )
    service_instance.orchestration_status = "Active"
    with patch.object(ServiceSubscription, "sdc_service", return_value=service):
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

    with patch.object(ServiceSubscription, "sdc_service", return_value=service) as service_mock:
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

    with patch.object(ServiceSubscription, "sdc_service", return_value=service) as service_mock:
        service_deletion_request = service_instance.delete()
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.IN_PROGRESS
    time.sleep(2)  # After 1 second mocked server changed request status to complete
    assert service_deletion_request.status == ServiceDeletionRequest.StatusEnum.COMPLETED
    assert len(list(service_subscription.service_instances)) == 0
