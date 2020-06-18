#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Instantion module."""
from abc import ABC
from dataclasses import dataclass
from typing import Iterable
from uuid import uuid4

from onapsdk.onap_service import OnapService
from onapsdk.sdnc import VfModulePreload
from onapsdk.service import Service as SdcService, Vnf, VfModule
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.headers_creator import headers_so_creator
from onapsdk.vid import LineOfBusiness, Platform

from .so_element import OrchestrationRequest


@dataclass
class VnfParameter:
    """Class to store vnf parameter used for preload.

    Contains two values: name of vnf parameter and it's value
    """

    name: str
    value: str


class Instantiation(OrchestrationRequest, ABC):
    """Abstract class used for instantiation."""

    def __init__(self,
                 name: str,
                 request_id: str,
                 instance_id: str) -> None:
        """Instantiate object initialization.

        Initializator used by classes inherited from this abstract class.

        Args:
            name (str): instantiated object name
            request_id (str): request ID
            instance_id (str): instance ID
        """
        super().__init__(request_id)
        self.name: str = name
        self.instance_id: str = instance_id


class VfModuleInstantiation(Instantiation):
    """VF module instantiation class."""

    def __init__(self,
                 name: str,
                 request_id: str,
                 instance_id: str,
                 vf_module: VfModule) -> None:
        """Initialize class object.

        Args:
            name (str): vf module name
            request_id (str): request ID
            instance_id (str): instance ID
            vnf_instantiation (VnfInstantiation): VNF instantiation class object
            vf_module (VfModule): VF module used for instantiation
        """
        super().__init__(name, request_id, instance_id)
        self.vf_module: VfModule = vf_module

    @classmethod
    def instantiate_ala_carte(cls,  # pylint: disable=too-many-arguments
                              vf_module,
                              vnf_instance,
                              vf_module_instance_name: str = None,
                              vnf_parameters: Iterable[VnfParameter] = None
                              ) -> "VfModuleInstantiation":
        """Instantiate VF module.

        Iterate throught vf modules from service Tosca file and instantiate vf modules.

        Args:
            vf_module_instance_name_factory (str, optional): Factory to create VF module names.
                It's going to be a prefix of name. Index of vf module in Tosca file will be
                added to it.
                If no value is provided it's going to be
                "Python_ONAP_SDK_vf_module_service_instance_{str(uuid4())}".
                Defaults to None.
            vnf_parameters (Iterable[VnfParameter], optional): Parameters which are
                going to be used in preload upload for vf modules. Defaults to None.

        Raises:
            AttributeError: VNF is not successfully instantiated.
            ValueError: VF module instnatiation request returns HTTP error code.

        Yields:
            Iterator[VfModuleInstantiation]: VfModuleInstantiation class object.

        """
        sdc_service: SdcService = vnf_instance.service_instance.service_subscription.sdc_service
        if vf_module_instance_name is None:
            vf_module_instance_name = \
                f"Python_ONAP_SDK_vf_module_instance_{str(uuid4())}"
        VfModulePreload.upload_vf_module_preload(
            vnf_instance,
            vf_module_instance_name,
            vf_module,
            vnf_parameters
        )
        response: dict = cls.send_message_json(
            "POST",
            (f"Instantiate {sdc_service.name} "
             f"service vf module {vf_module.name}"),
            (f"{cls.base_url}/onap/so/infra/serviceInstantiation/{cls.api_version}/"
             f"serviceInstances/{vnf_instance.service_instance.instance_id}/vnfs/"
             f"{vnf_instance.vnf_id}/vfModules"),
            data=jinja_env().get_template("instantiate_vf_module_ala_carte.json.j2").
            render(
                vf_module_instance_name=vf_module_instance_name,
                vf_module=vf_module,
                service=sdc_service,
                cloud_region=vnf_instance.service_instance.service_subscription.cloud_region,
                tenant=vnf_instance.service_instance.service_subscription.tenant,
                vnf_instance=vnf_instance
            ),
            headers=headers_so_creator(OnapService.headers),
            exception=ValueError
        )
        return VfModuleInstantiation(
            name=vf_module_instance_name,
            request_id=response["requestReferences"].get("requestId"),
            instance_id=response["requestReferences"].get("instanceId"),
            vf_module=vf_module
        )


class VnfInstantiation(Instantiation):
    """VNF instantiation class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 request_id: str,
                 instance_id: str,
                 line_of_business: LineOfBusiness,
                 platform: Platform,
                 vnf: Vnf) -> None:
        """Class VnfInstantion object initialization.

        Args:
            name (str): VNF name
            request_id (str): request ID
            instance_id (str): instance ID
            service_instantiation ([type]): ServiceInstantiation class object
            line_of_business (LineOfBusiness): LineOfBusiness class object
            platform (Platform): Platform class object
            vnf (Vnf): Vnf class object
        """
        super().__init__(name, request_id, instance_id)
        self.line_of_business = line_of_business
        self.platform = platform
        self.vnf = vnf

    @classmethod
    def create_from_request_response(cls, request_response: dict) -> "VnfInstantiation":
        """Create VNF instantiation object based on request details.

        Raises:
            ValueError: Service related with given object doesn't exist
            ValueError: No ServiceInstantiation related with given VNF instantiation
            ValueError: VNF related with given object doesn't exist
            ValueError: Invalid dictionary - couldn't create VnfInstantiation object

        Returns:
            VnfInstantiation: VnfInstantiation object

        """
        if request_response.get("request", {}).get("requestScope") == "vnf" and \
            request_response.get("request", {}).get("requestType") == "createInstance":
            service: SdcService = None
            for related_instance in request_response.get("request", {}).get("requestDetails", {})\
                    .get("relatedInstanceList", []):
                if related_instance.get("relatedInstance", {}).get("modelInfo", {})\
                        .get("modelType") == "service":
                    service = SdcService(related_instance.get("relatedInstance", {})\
                        .get("modelInfo", {}).get("modelName"))
            if not service:
                raise ValueError("No related service in Vnf instance details response")
            vnf: Vnf = None
            for service_vnf in service.vnfs:
                if service_vnf.name == request_response.get("request", {})\
                    .get("requestDetails", {}).get("modelInfo", {}).get("modelCustomizationName"):
                    vnf = service_vnf
            if not vnf:
                raise ValueError("No vnf in service vnfs list")
            return cls(
                name=request_response.get("request", {})\
                    .get("instanceReferences", {}).get("vnfInstanceName"),
                request_id=request_response.get("request", {}).get("requestId"),
                instance_id=request_response.get("request", {})\
                    .get("instanceReferences", {}).get("vnfInstanceId"),
                line_of_business=LineOfBusiness.create(request_response.get("request", {})\
                    .get("requestDetails", {}).get("lineOfBusiness", {}).get("lineOfBusinessName")),
                platform=Platform.create(request_response.get("request", {})\
                    .get("requestDetails", {}).get("platform", {}).get("platformName")),
                vnf=vnf
            )
        raise ValueError("Invalid vnf instantions request dictionary")

    @classmethod
    def get_by_vnf_instance_name(cls, vnf_instance_name: str) -> "VnfInstantiation":
        """Get VNF instantiation request by instance name.

        Raises:
            ValueError: Vnf instance with given name doesn't exist

        Returns:
            VnfInstantiation: Vnf instantiation request object

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Check {vnf_instance_name} service instantiation status",
            (f"{cls.base_url}/onap/so/infra/orchestrationRequests/{cls.api_version}?"
             f"filter=vnfInstanceName:EQUALS:{vnf_instance_name}"),
            headers=headers_so_creator(OnapService.headers)
        )
        if not response.get("requestList", []):
            raise ValueError("Vnf instance doesn't exist")
        for details in response["requestList"]:
            return cls.create_from_request_response(details)
        raise ValueError("No createInstance request found")

    @classmethod
    def instantiate_ala_carte(cls,  # pylint: disable=too-many-arguments
                              aai_service_instance: "ServiceInstance",
                              vnf_object: "Vnf",
                              line_of_business_object: "LineOfBusiness",
                              platform_object: "Platform",
                              vnf_instance_name: str = None) -> "VnfInstantiation":
        """Instantiate Vnf using a'la carte method.

        Args:
            vnf_object (Vnf): Vnf to instantiate
            line_of_business_object (LineOfBusiness): LineOfBusiness to use in instantiation request
            platform_object (Platform): Platform to use in instantiation request
            vnf_instance_name (str, optional): Vnf instance name. Defaults to None.

        Raises:
            ValueError: Instantiate request returns response with HTTP error code

        Returns:
            VnfInstantiation: VnfInstantiation object

        """
        sdc_service: SdcService = aai_service_instance.service_subscription.sdc_service
        if vnf_instance_name is None:
            vnf_instance_name = \
                f"Python_ONAP_SDK_vnf_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            (f"Instantiate {aai_service_instance.service_subscription.sdc_service.name} "
             f"service vnf {vnf_object.name}"),
            (f"{cls.base_url}/onap/so/infra/serviceInstantiation/{cls.api_version}/"
             f"serviceInstances/{aai_service_instance.instance_id}/vnfs"),
            data=jinja_env().get_template("instantiate_vnf_ala_carte.json.j2").
            render(
                vnf_service_instance_name=vnf_instance_name,
                vnf=vnf_object,
                service=sdc_service,
                cloud_region=aai_service_instance.service_subscription.cloud_region,
                tenant=aai_service_instance.service_subscription.tenant,
                line_of_business=line_of_business_object,
                platform=platform_object,
                service_instance=aai_service_instance
            ),
            headers=headers_so_creator(OnapService.headers),
            exception=ValueError
        )
        return VnfInstantiation(
            name=vnf_instance_name,
            request_id=response["requestReferences"]["requestId"],
            instance_id=response["requestReferences"]["instanceId"],
            line_of_business=line_of_business_object,
            platform=platform_object,
            vnf=vnf_object
        )

class ServiceInstantiation(Instantiation):
    """Service instantiation class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 request_id: str,
                 instance_id: str,
                 sdc_service: "SdcService",
                 cloud_region: "CloudRegion",
                 tenant: "Tenant",
                 customer: "Customer",
                 owning_entity: "OwningEntity",
                 project: "Project") -> None:
        """Class ServiceInstantiation object initialization.

        Args:
            name (str): service instance name
            request_id (str): service instantiation request ID
            instance_id (str): service instantiation ID
            sdc_service (SdcService): SdcService class object
            cloud_region (CloudRegion): CloudRegion class object
            tenant (Tenant): Tenant class object
            customer (Customer): Customer class object
            owning_entity (OwningEntity): OwningEntity class object
            project (Project): Project class object

        """
        super().__init__(name, request_id, instance_id)
        self.sdc_service = sdc_service
        self.cloud_region = cloud_region
        self.tenant = tenant
        self.customer = customer
        self.owning_entity = owning_entity
        self.project = project

    @classmethod
    def instantiate_so_ala_carte(cls,  # pylint: disable=too-many-arguments
                                 sdc_service: "SdcService",
                                 cloud_region: "CloudRegion",
                                 tenant: "Tenant",
                                 customer: "Customer",
                                 owning_entity: "OwningEntity",
                                 project: "Project",
                                 service_instance_name: str = None) -> "ServiceInstantiationc":
        """Instantiate service using SO a'la carte request.

        Args:
            sdc_service (SdcService): Service to instantiate
            cloud_region (CloudRegion): Cloud region to use in instantiation request
            tenant (Tenant): Tenant to use in instantiation request
            customer (Customer): Customer to use in instantiation request
            owning_entity (OwningEntity): Owning entity to use in instantiation request
            project (Project): Project to use in instantiation request
            service_instance_name (str, optional): Service instance name. Defaults to None.

        Raises:
            ValueError: Instantiation request returns HTTP error code.

        Returns:
            ServiceInstantiation: instantiation request object

        """
        if not sdc_service.distributed:
            raise ValueError("Service is not distributed")
        if service_instance_name is None:
            service_instance_name = f"Python_ONAP_SDK_service_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            f"Instantiate {sdc_service.name} service a'la carte",
            (f"{cls.base_url}/onap/so/infra/"
             f"serviceInstantiation/{cls.api_version}/serviceInstances"),
            data=jinja_env().get_template("instantiate_ala_carte.json.j2").
            render(
                sdc_service=sdc_service,
                cloud_region=cloud_region,
                tenant=tenant,
                customer=customer,
                owning_entity=owning_entity,
                service_instance_name=service_instance_name,
                project=project
            ),
            headers=headers_so_creator(OnapService.headers),
            exception=ValueError
        )
        return cls(
            name=service_instance_name,
            request_id=response["requestReferences"].get("requestId"),
            instance_id=response["requestReferences"].get("instanceId"),
            sdc_service=sdc_service,
            cloud_region=cloud_region,
            tenant=tenant,
            customer=customer,
            owning_entity=owning_entity,
            project=project
        )

    @property
    def aai_service_instance(self) -> "ServiceInstance":
        """Service instane associated with service instantiation request.

        Raises:
            AttributeError: Service is not instantiated
            AttributeError: A&AI resource is not created

        Returns:
            ServiceInstance: ServiceInstance

        """
        if self.status != self.StatusEnum.COMPLETED:
            raise AttributeError("Service not instantiated")
        try:
            service_subscription: "ServiceSubscription" = \
                self.customer.get_service_subscription_by_service_type(self.sdc_service.name)
            return service_subscription.get_service_instance_by_name(self.name)
        except ValueError:
            self._logger.error("A&AI resources not created properly")
            raise AttributeError
