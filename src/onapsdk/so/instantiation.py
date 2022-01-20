#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Instantion module."""
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

from dacite import from_dict

from onapsdk.aai.business.owning_entity import OwningEntity
from onapsdk.exceptions import (
    APIError, InvalidResponse, ParameterError, ResourceNotFound, StatusError
)
from onapsdk.onap_service import OnapService
from onapsdk.sdnc import NetworkPreload, VfModulePreload
from onapsdk.sdc.service import Network, Service as SdcService, Vnf, VfModule
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.headers_creator import headers_so_creator

from .so_element import OrchestrationRequest


@dataclass
class SoServiceVfModule:
    """Class to store a VfModule instance parameters."""

    model_name: str
    instance_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    processing_priority: Optional[int] = None


@dataclass
class SoServiceXnf:
    """Class to store a Xnf instance parameters."""

    model_name: str
    instance_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    processing_priority: Optional[int] = None

    @classmethod
    def load(cls, data: Dict[str, Any]) -> "SoServiceVnf":
        """Create a vnf instance description object from the dict.

        Useful if you keep your instance data in file.

        Returns:
            SoServiceVnf: SoServiceVnf object created from the dictionary

        """
        return from_dict(data_class=cls, data=data)


@dataclass
class SoServiceVnf(SoServiceXnf):
    """Class to store a Vnf instance parameters."""

    vf_modules: List[SoServiceVfModule] = field(default_factory=list)


@dataclass
class SoServicePnf(SoServiceXnf):
    """Class to store a Pnf instance parameters."""


@dataclass
class SoService:
    """Class to store SO Service parameters used for macro instantiation.

    Contains value list: List of vnfs to instantiate
    Contains value: subscription service type
    """

    subscription_service_type: str
    vnfs: List[SoServiceVnf] = field(default_factory=list)
    pnfs: List[SoServicePnf] = field(default_factory=list)
    instance_name: Optional[str] = None

    @classmethod
    def load(cls, data: Dict[str, Any]) -> "SoService":
        """Create a service instance description object from the dict.

        Useful if you keep your instance data in file.

        Returns:
            SoService: SoService object created from the dictionary

        """
        return from_dict(data_class=cls, data=data)



@dataclass
class VnfParameters:
    """Class to store vnf parameters used for macro instantiation.

    Contains value lists: List vnf Instantiation parameters and list of
    vfModule parameters
    """

    name: str
    vnf_parameters: Iterable["InstantiationParameter"] = None
    vfmodule_parameters: Iterable["VfmoduleParameters"] = None

@dataclass
class VfmoduleParameters:
    """Class to store vfmodule parameters used for macro instantiation.

    Contains value lists: List of vfModule parameters
    """

    name: str
    vfmodule_parameters: Iterable["InstantiationParameter"] = None


@dataclass
class InstantiationParameter:
    """Class to store instantiation parameters used for preload or macro instantiation.

    Contains two values: name of parameter and it's value
    """

    name: str
    value: str


@dataclass
class Subnet:  # pylint: disable=too-many-instance-attributes
    """Class to store subnet parameters used for preload."""

    name: str
    start_address: str
    gateway_address: str
    role: str = None
    cidr_mask: str = "24"
    ip_version: str = "4"
    dhcp_enabled: bool = False
    dhcp_start_address: Optional[str] = None
    dhcp_end_address: Optional[str] = None

    def __post_init__(self) -> None:
        """Post init subnet method.

        Checks if both dhcp_start_address and dhcp_end_address values are
        provided if dhcp is enabled.

        Raises:
            ParameterError: Neither dhcp_start_addres
                    nor dhcp_end_address are provided

        """
        if self.dhcp_enabled and \
            not all([self.dhcp_start_address,
                     self.dhcp_end_address]):
            msg = "DHCP is enabled but neither DHCP " \
                  "start nor end adresses are provided."
            raise ParameterError(msg)


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


class VfModuleInstantiation(Instantiation):  # pytest: disable=too-many-ancestors
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
                              vf_module: "VfModule",
                              vnf_instance: "VnfInstance",
                              cloud_region: "CloudRegion",
                              tenant: "Tenant",
                              vf_module_instance_name: str = None,
                              vnf_parameters: Iterable["InstantiationParameter"] = None,
                              use_preload: bool = True) -> "VfModuleInstantiation":
        """Instantiate VF module.

        Iterate throught vf modules from service Tosca file and instantiate vf modules.

        Args:
            vf_module (VfModule): VfModule to instantiate
            vnf_instance (VnfInstance): VnfInstance object
            cloud_region (CloudRegion, optional): Cloud region to use in instantiation request.
                Defaults to None.
            tenant (Tenant, optional): Tenant to use in instnatiation request.
                Defaults to None.
            vf_module_instance_name_factory (str, optional): Factory to create VF module names.
                It's going to be a prefix of name. Index of vf module in Tosca file will be
                added to it.
                If no value is provided it's going to be
                "Python_ONAP_SDK_vf_module_service_instance_{str(uuid4())}".
                Defaults to None.
            vnf_parameters (Iterable[InstantiationParameter], optional): Parameters which are
                going to be used in preload upload for vf modules or passed in "userParams".
                Defaults to None.
            use_preload (bool, optional): This flag determines whether instantiation parameters
                are used as preload or "userParams" content. Defaults to True

        Yields:
            Iterator[VfModuleInstantiation]: VfModuleInstantiation class object.

        """
        if vf_module_instance_name is None:
            vf_module_instance_name = \
                f"Python_ONAP_SDK_vf_module_instance_{str(uuid4())}"
        if use_preload:
            VfModulePreload.upload_vf_module_preload(
                vnf_instance,
                vf_module_instance_name,
                vf_module,
                vnf_parameters
            )
            vnf_parameters = None
        sdc_service: SdcService = vnf_instance.service_instance.sdc_service
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
                cloud_region=cloud_region,
                tenant=tenant,
                vnf_instance=vnf_instance,
                vf_module_parameters=vnf_parameters or []
            ),
            headers=headers_so_creator(OnapService.headers)
        )
        return VfModuleInstantiation(
            name=vf_module_instance_name,
            request_id=response["requestReferences"].get("requestId"),
            instance_id=response["requestReferences"].get("instanceId"),
            vf_module=vf_module
        )

class NodeTemplateInstantiation(Instantiation, ABC):  # pytest: disable=too-many-ancestors
    """Base class for service's node_template object instantiation."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 request_id: str,
                 instance_id: str,
                 line_of_business: str,
                 platform: str) -> None:
        """Node template object initialization.

        Args:
            name (str): Node template name
            request_id (str): Node template instantiation request ID
            instance_id (str): Node template instance ID
            line_of_business (str): LineOfBusiness name
            platform (str): Platform name
        """
        super().__init__(name, request_id, instance_id)
        self.line_of_business = line_of_business
        self.platform = platform


class VnfInstantiation(NodeTemplateInstantiation):  # pylint: disable=too-many-ancestors
    """VNF instantiation class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 request_id: str,
                 instance_id: str,
                 line_of_business: str,
                 platform: str,
                 vnf: Vnf) -> None:
        """Class VnfInstantion object initialization.

        Args:
            name (str): VNF name
            request_id (str): request ID
            instance_id (str): instance ID
            service_instantiation ([type]): ServiceInstantiation class object
            line_of_business (str): LineOfBusiness name
            platform (str): Platform name
            vnf (Vnf): Vnf class object
        """
        super().__init__(name, request_id, instance_id, line_of_business, platform)
        self.vnf = vnf

    @classmethod
    def create_from_request_response(cls, request_response: dict) -> "VnfInstantiation":
        """Create VNF instantiation object based on request details.

        Raises:
            ResourceNotFound: Service related with given object doesn't exist
            ResourceNotFound: No ServiceInstantiation related with given VNF instantiation
            ResourceNotFound: VNF related with given object doesn't exist
            InvalidResponse: Invalid dictionary - couldn't create VnfInstantiation object

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
                raise ResourceNotFound("No related service in Vnf instance details response")
            vnf: Vnf = None
            for service_vnf in service.vnfs:
                if service_vnf.name == request_response.get("request", {})\
                    .get("requestDetails", {}).get("modelInfo", {}).get("modelCustomizationName"):
                    vnf = service_vnf
            if not vnf:
                raise ResourceNotFound("No vnf in service vnfs list")
            return cls(
                name=request_response.get("request", {})\
                    .get("instanceReferences", {}).get("vnfInstanceName"),
                request_id=request_response.get("request", {}).get("requestId"),
                instance_id=request_response.get("request", {})\
                    .get("instanceReferences", {}).get("vnfInstanceId"),
                line_of_business=request_response.get("request", {})\
                    .get("requestDetails", {}).get("lineOfBusiness", {}).get("lineOfBusinessName"),
                platform=request_response.get("request", {})\
                    .get("requestDetails", {}).get("platform", {}).get("platformName"),
                vnf=vnf
            )
        raise InvalidResponse("Invalid vnf instantions in response dictionary's requestList")

    @classmethod
    def get_by_vnf_instance_name(cls, vnf_instance_name: str) -> "VnfInstantiation":
        """Get VNF instantiation request by instance name.

        Raises:
            InvalidResponse: Vnf instance with given name does not contain
                requestList or the requestList does not contain any details.

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
        key = "requestList"
        if not response.get(key, []):
            raise InvalidResponse(f"{key} of a Vnf instance is missing.")
        for details in response[key]:
            return cls.create_from_request_response(details)
        msg = f"No details available in response dictionary's {key}."
        raise InvalidResponse(msg)

    @classmethod
    def instantiate_ala_carte(cls,  # pylint: disable=too-many-arguments
                              aai_service_instance: "ServiceInstance",
                              vnf_object: "Vnf",
                              line_of_business: str,
                              platform: str,
                              cloud_region: "CloudRegion",
                              tenant: "Tenant",
                              sdc_service: "SdcService",
                              vnf_instance_name: str = None,
                              vnf_parameters: Iterable["InstantiationParameter"] = None
                              ) -> "VnfInstantiation":
        """Instantiate Vnf using a'la carte method.

        Args:
            vnf_object (Vnf): Vnf to instantiate
            line_of_business_object (LineOfBusiness): LineOfBusiness to use in instantiation request
            platform_object (Platform): Platform to use in instantiation request
            cloud_region (CloudRegion): Cloud region to use in instantiation request.
            tenant (Tenant): Tenant to use in instnatiation request.
            vnf_instance_name (str, optional): Vnf instance name. Defaults to None.
            vnf_parameters (Iterable[InstantiationParameter], optional): Instantiation parameters
                that are sent in the request. Defaults to None

        Returns:
            VnfInstantiation: VnfInstantiation object

        """
        if vnf_instance_name is None:
            vnf_instance_name = \
                f"Python_ONAP_SDK_vnf_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            (f"Instantiate {sdc_service.name} "
             f"service vnf {vnf_object.name}"),
            (f"{cls.base_url}/onap/so/infra/serviceInstantiation/{cls.api_version}/"
             f"serviceInstances/{aai_service_instance.instance_id}/vnfs"),
            data=jinja_env().get_template("instantiate_vnf_ala_carte.json.j2").
            render(
                instance_name=vnf_instance_name,
                vnf=vnf_object,
                service=sdc_service,
                cloud_region=cloud_region or \
                    next(aai_service_instance.service_subscription.cloud_regions),
                tenant=tenant or next(aai_service_instance.service_subscription.tenants),
                line_of_business=line_of_business,
                platform=platform,
                service_instance=aai_service_instance,
                vnf_parameters=vnf_parameters or []
            ),
            headers=headers_so_creator(OnapService.headers)
        )
        return VnfInstantiation(
            name=vnf_instance_name,
            request_id=response["requestReferences"]["requestId"],
            instance_id=response["requestReferences"]["instanceId"],
            line_of_business=line_of_business,
            platform=platform,
            vnf=vnf_object
        )

    @classmethod
    def instantiate_macro(cls,  # pylint: disable=too-many-arguments, too-many-locals
                          aai_service_instance: "ServiceInstance",
                          vnf_object: "Vnf",
                          line_of_business: str,
                          platform: str,
                          cloud_region: "CloudRegion",
                          tenant: "Tenant",
                          sdc_service: "SdcService",
                          vnf_instance_name: str = None,
                          vnf_parameters: Iterable["InstantiationParameter"] = None,
                          so_vnf: "SoServiceVnf" = None
                          ) -> "VnfInstantiation":
        """Instantiate Vnf using macro method.

        Args:
            aai_service_instance (ServiceInstance): Service instance associated with request
            vnf_object (Vnf): Vnf to instantiate
            line_of_business (LineOfBusiness): LineOfBusiness to use in instantiation request
            platform (Platform): Platform to use in instantiation request
            cloud_region (CloudRegion): Cloud region to use in instantiation request.
            tenant (Tenant): Tenant to use in instantiation request.
            vnf_instance_name (str, optional): Vnf instance name. Defaults to None.
            vnf_parameters (Iterable[InstantiationParameter], optional): Instantiation parameters
                that are sent in the request. Defaults to None
            so_vnf (SoServiceVnf): object with vnf instance parameters

        Returns:
            VnfInstantiation: VnfInstantiation object

        """
        owning_entity_id = None
        project = "OnapsdkProject"

        for relationship in aai_service_instance.relationships:
            if relationship.related_to == "owning-entity":
                owning_entity_id = relationship.relationship_data.pop().get("relationship-value")
            if relationship.related_to == "project":
                project = relationship.relationship_data.pop().get("relationship-value")

        owning_entity = OwningEntity.get_by_owning_entity_id(
            owning_entity_id=owning_entity_id)

        if so_vnf:
            template_file = "instantiate_vnf_macro_so_vnf.json.j2"
            if so_vnf.instance_name:
                vnf_instance_name = so_vnf.instance_name
        else:
            template_file = "instantiate_vnf_macro.json.j2"
            if vnf_instance_name is None:
                vnf_instance_name = \
                    f"Python_ONAP_SDK_vnf_instance_{str(uuid4())}"

        response: dict = cls.send_message_json(
            "POST",
            (f"Instantiate {sdc_service.name} "
             f"service vnf {vnf_object.name}"),
            (f"{cls.base_url}/onap/so/infra/serviceInstantiation/{cls.api_version}/"
             f"serviceInstances/{aai_service_instance.instance_id}/vnfs"),
            data=jinja_env().get_template(template_file).render(
                instance_name=vnf_instance_name,
                vnf=vnf_object,
                service=sdc_service,
                cloud_region=cloud_region or \
                             next(aai_service_instance.service_subscription.cloud_regions),
                tenant=tenant or next(aai_service_instance.service_subscription.tenants),
                project=project,
                owning_entity=owning_entity,
                line_of_business=line_of_business,
                platform=platform,
                service_instance=aai_service_instance,
                vnf_parameters=vnf_parameters or [],
                so_vnf=so_vnf
            ),
            headers=headers_so_creator(OnapService.headers)
        )

        return VnfInstantiation(
            name=vnf_instance_name,
            request_id=response["requestReferences"]["requestId"],
            instance_id=response["requestReferences"]["instanceId"],
            line_of_business=line_of_business,
            platform=platform,
            vnf=vnf_object
        )


class ServiceInstantiation(Instantiation):  # pylint: disable=too-many-ancestors
    """Service instantiation class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 request_id: str,
                 instance_id: str,
                 sdc_service: "SdcService",
                 cloud_region: "CloudRegion",
                 tenant: "Tenant",
                 customer: "Customer",
                 owning_entity: OwningEntity,
                 project: str) -> None:
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
            project (str): Project name

        """
        super().__init__(name, request_id, instance_id)
        self.sdc_service = sdc_service
        self.cloud_region = cloud_region
        self.tenant = tenant
        self.customer = customer
        self.owning_entity = owning_entity
        self.project = project

    @classmethod
    def instantiate_ala_carte(cls,  # pylint: disable=too-many-arguments
                              sdc_service: "SdcService",
                              cloud_region: "CloudRegion",
                              tenant: "Tenant",
                              customer: "Customer",
                              owning_entity: OwningEntity,
                              project: str,
                              service_subscription: "ServiceSubscription",
                              service_instance_name: str = None,
                              enable_multicloud: bool = False) -> "ServiceInstantiation":
        """Instantiate service using SO a'la carte request.

        Args:
            sdc_service (SdcService): Service to instantiate
            cloud_region (CloudRegion): Cloud region to use in instantiation request
            tenant (Tenant): Tenant to use in instantiation request
            customer (Customer): Customer to use in instantiation request
            owning_entity (OwningEntity): Owning entity to use in instantiation request
            project (str): Project name to use in instantiation request
            service_subscription (ServiceSubscription): Customer's service subsription.
            service_instance_name (str, optional): Service instance name. Defaults to None.
            enable_multicloud (bool, optional): Determines if Multicloud should be enabled
                for instantiation request. Defaults to False.

        Raises:
            StatusError: if a service is not distributed.

        Returns:
            ServiceInstantiation: instantiation request object

        """
        if not sdc_service.distributed:
            msg = f"Service {sdc_service.name} is not distributed."
            raise StatusError(msg)
        if service_instance_name is None:
            service_instance_name = f"Python_ONAP_SDK_service_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            f"Instantiate {sdc_service.name} service a'la carte",
            (f"{cls.base_url}/onap/so/infra/"
             f"serviceInstantiation/{cls.api_version}/serviceInstances"),
            data=jinja_env().get_template("instantiate_service_ala_carte.json.j2").
            render(
                sdc_service=sdc_service,
                cloud_region=cloud_region,
                tenant=tenant,
                customer=customer,
                owning_entity=owning_entity,
                service_instance_name=service_instance_name,
                project=project,
                enable_multicloud=enable_multicloud,
                service_subscription=service_subscription
            ),
            headers=headers_so_creator(OnapService.headers)
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

    # pylint: disable=too-many-arguments, too-many-locals
    @classmethod
    def instantiate_macro(cls,
                          sdc_service: "SdcService",
                          customer: "Customer",
                          owning_entity: OwningEntity,
                          project: str,
                          line_of_business: str,
                          platform: str,
                          aai_service: "AaiService" = None,
                          cloud_region: "CloudRegion" = None,
                          tenant: "Tenant" = None,
                          service_instance_name: str = None,
                          vnf_parameters: Iterable["VnfParameters"] = None,
                          enable_multicloud: bool = False,
                          so_service: "SoService" = None,
                          service_subscription: "ServiceSubscription" = None
                          ) -> "ServiceInstantiation":
        """Instantiate service using SO macro request.

        Args:
            sdc_service (SdcService): Service to instantiate
            customer (Customer): Customer to use in instantiation request
            owning_entity (OwningEntity): Owning entity to use in instantiation request
            project (Project): Project name to use in instantiation request
            line_of_business_object (LineOfBusiness): LineOfBusiness name to use
                in instantiation request
            platform_object (Platform): Platform name to use in instantiation request
            aai_service (AaiService): Service object from aai sdc
            cloud_region (CloudRegion): Cloud region to use in instantiation request
            tenant (Tenant): Tenant to use in instantiation request
            service_instance_name (str, optional): Service instance name. Defaults to None.
            vnf_parameters: (Iterable[VnfParameters]): Parameters which are
                going to be used for vnfs instantiation. Defaults to None.
            enable_multicloud (bool, optional): Determines if Multicloud should be enabled
                for instantiation request. Defaults to False.
            so_service (SoService, optional): SO values to use in instantiation request
            service_subscription(ServiceSubscription, optional): Customer service subscription
                for the instantiated service. Required if so_service is not provided.

        Raises:
            StatusError: if a service is not distributed.

        Returns:
            ServiceInstantiation: instantiation request object

        """
        template_file = "instantiate_service_macro.json.j2"
        if so_service:
            template_file = "instantiate_multi_vnf_service_macro.json.j2"
            if so_service.instance_name:
                service_instance_name = so_service.instance_name
        else:
            if not service_subscription:
                raise ParameterError("If no so_service is provided, "
                                     "service_subscription parameter is required!")
            if service_instance_name is None:
                service_instance_name = f"Python_ONAP_SDK_service_instance_{str(uuid4())}"
        if not sdc_service.distributed:
            msg = f"Service {sdc_service.name} is not distributed."
            raise StatusError(msg)

        response: dict = cls.send_message_json(
            "POST",
            f"Instantiate {sdc_service.name} service macro",
            (f"{cls.base_url}/onap/so/infra/"
             f"serviceInstantiation/{cls.api_version}/serviceInstances"),
            data=jinja_env().get_template(template_file). \
                render(
                    so_service=so_service,
                    sdc_service=sdc_service,
                    cloud_region=cloud_region,
                    tenant=tenant,
                    customer=customer,
                    owning_entity=owning_entity,
                    project=project,
                    aai_service=aai_service,
                    line_of_business=line_of_business,
                    platform=platform,
                    service_instance_name=service_instance_name,
                    vnf_parameters=vnf_parameters,
                    enable_multicloud=enable_multicloud,
                    service_subscription=service_subscription
                ),
            headers=headers_so_creator(OnapService.headers)
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
        """Service instance associated with service instantiation request.

        Raises:
            StatusError: if a service is not instantiated -
                not in COMPLETE status.
            APIError: A&AI resource is not created

        Returns:
            ServiceInstance: ServiceInstance

        """
        required_status = self.StatusEnum.COMPLETED
        if self.status != required_status:
            msg = (f"Service {self.name} is not instantiated - "
                   f"not in {required_status} status.")
            raise StatusError(msg)
        try:
            service_subscription: "ServiceSubscription" = \
                self.customer.get_service_subscription_by_service_type(self.sdc_service.name)
            return service_subscription.get_service_instance_by_name(self.name)
        except APIError as exc:
            self._logger.error("A&AI resources not created properly")
            raise exc


class NetworkInstantiation(NodeTemplateInstantiation):  # pylint: disable=too-many-ancestors
    """Network instantiation class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 request_id: str,
                 instance_id: str,
                 line_of_business: str,
                 platform: str,
                 network: Network) -> None:
        """Class NetworkInstantiation object initialization.

        Args:
            name (str): VNF name
            request_id (str): request ID
            instance_id (str): instance ID
            service_instantiation ([type]): ServiceInstantiation class object
            line_of_business (str): LineOfBusiness name
            platform (str): Platform name
            vnf (Network): Network class object
        """
        super().__init__(name, request_id, instance_id, line_of_business, platform)
        self.network = network

    @classmethod
    def instantiate_ala_carte(cls,  # pylint: disable=too-many-arguments
                              aai_service_instance: "ServiceInstance",
                              network_object: "Network",
                              line_of_business: str,
                              platform: str,
                              cloud_region: "CloudRegion",
                              tenant: "Tenant",
                              network_instance_name: str = None,
                              subnets: Iterable[Subnet] = None) -> "NetworkInstantiation":
        """Instantiate Network using a'la carte method.

        Args:
            network_object (Network): Network to instantiate
            line_of_business (str): LineOfBusiness name to use in instantiation request
            platform (str): Platform name to use in instantiation request
            cloud_region (CloudRegion): Cloud region to use in instantiation request.
            tenant (Tenant): Tenant to use in instnatiation request.
            network_instance_name (str, optional): Network instance name. Defaults to None.

        Returns:
            NetworkInstantiation: NetworkInstantiation object

        """
        if network_instance_name is None:
            network_instance_name = \
                f"Python_ONAP_SDK_network_instance_{str(uuid4())}"
        NetworkPreload.upload_network_preload(network=network_object,
                                              network_instance_name=network_instance_name,
                                              subnets=subnets)
        response: dict = cls.send_message_json(
            "POST",
            (f"Instantiate {aai_service_instance.sdc_service.name} "
             f"service network {network_object.name}"),
            (f"{cls.base_url}/onap/so/infra/serviceInstantiation/{cls.api_version}/"
             f"serviceInstances/{aai_service_instance.instance_id}/networks"),
            data=jinja_env().get_template("instantiate_network_ala_carte.json.j2").
            render(
                instance_name=network_instance_name,
                network=network_object,
                service=aai_service_instance.sdc_service,
                cloud_region=cloud_region or \
                    next(aai_service_instance.service_subscription.cloud_regions),
                tenant=tenant or next(aai_service_instance.service_subscription.tenants),
                line_of_business=line_of_business,
                platform=platform,
                service_instance=aai_service_instance,
                subnets=subnets
            ),
            headers=headers_so_creator(OnapService.headers)
        )
        return cls(
            name=network_instance_name,
            request_id=response["requestReferences"]["requestId"],
            instance_id=response["requestReferences"]["instanceId"],
            line_of_business=line_of_business,
            platform=platform,
            network=network_object
        )
