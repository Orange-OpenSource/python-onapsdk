"""AAI business module."""  # pylint: disable=C0302
from dataclasses import dataclass
from typing import Iterable, Iterator
from urllib.parse import urlencode
from uuid import uuid4

import onapsdk
from onapsdk.so.deletion import (
    ServiceDeletionRequest,
    VnfDeletionRequest,
    VfModuleDeletionRequest
)
from onapsdk.service import Service as SdcService
from onapsdk.utils.jinja import jinja_env

from .aai_element import AaiElement, Relationship
from .cloud_infrastructure import CloudRegion


class VfModuleInstance(AaiElement):  # pylint: disable=R0902
    """Vf module instance class."""

    def __init__(self,  # pylint: disable=R0913, R0914
                 vnf_instance: "VnfInstance",
                 vf_module_id: str,
                 is_base_vf_module: bool,
                 automated_assignment: bool,
                 vf_module_name: str = None,
                 heat_stack_id: str = None,
                 orchestration_status: str = None,
                 resource_version: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 persona_model_version: str = None,
                 model_customization_id: str = None,
                 widget_model_id: str = None,
                 widget_model_version: str = None,
                 contrail_service_instance_fqdn: str = None,
                 module_index: int = None,
                 selflink: str = None) -> None:
        """Vf module initialization.

        Args:
            vnf_instance (VnfInstance): VnfInstance
            vf_module_id (str): Unique ID of vf-module
            is_base_vf_module (bool): used to indicate whether or not this object is base vf module
            automated_assignment (bool): ndicates whether vf-module assignment was done via
                automation or manually
            vf_module_name (str, optional): Name of vf-module. Defaults to None.
            heat_stack_id (str, optional): Heat stack id corresponding to this instance.
                Defaults to None.
            orchestration_status (str, optional): orchestration status of this vf-module,
                mastered by MSO. Defaults to None.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to None.
            model_invariant_id (str, optional): the ASDC model id for this resource or
                service model. Defaults to None.
            model_version_id (str, optional): the ASDC model version for this resource or
                service model. Defaults to None.
            persona_model_version (str, optional): the ASDC model version for this resource or
                service model. Defaults to None.
            model_customization_id (str, optional): captures the id of all the configuration
                used to customize the resource for the service. Defaults to None.
            widget_model_id (str, optional): the ASDC data dictionary widget model.
                This maps directly to the A&AI widget. Defaults to None.
            widget_model_version (str, optional): the ASDC data dictionary version of
                the widget model. This maps directly to the A&AI version of the widget.
                Defaults to None.
            contrail_service_instance_fqdn (str, optional): the Contrail unique ID
                for a service-instance. Defaults to None.
            module_index (int, optional): the index will track the number of modules
                of a given type that have been deployed in a VNF, starting with 0,
                and always choosing the lowest available digit. Defaults to None.
            selflink (str, optional): Path to the controller object. Defaults to None.
        """
        super().__init__()
        self.vnf_instance: "VnfInstance" = vnf_instance
        self.vf_module_id: str = vf_module_id
        self.is_base_vf_module: bool = is_base_vf_module
        self.automated_assignment: bool = automated_assignment
        self.vf_module_name: str = vf_module_name
        self.heat_stack_id: str = heat_stack_id
        self.orchestration_status: str = orchestration_status
        self.resource_version: str = resource_version
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id
        self.persona_model_version: str = persona_model_version
        self.model_customization_id: str = model_customization_id
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version
        self.contrail_service_instance_fqdn: str = contrail_service_instance_fqdn
        self.module_index: int = module_index
        self.selflink: str = selflink

    def __repr__(self) -> str:
        """Object represetation.

        Returns:
            str: Human readble VfModuleInstance representation

        """
        return (f"VfModuleInstance(vf_module_id={self.vf_module_id}, "
                f"is_base_vf_module={self.is_base_vf_module}, "
                f"automated_assignment={self.automated_assignment})")

    @property
    def url(self) -> str:
        """Resource url.

        Returns:
            str: VfModuleInstance url

        """
        return f"{self.vnf_instance.url}/vf-modules/vf-module/{self.vf_module_id}"

    @property
    def vf_module(self) -> "VfModule":
        """Vf module associated with that vf module instance.

        Raises:
            AttributeError: Could not find VF module for that VfModule instance

        Returns:
            VfModule: VfModule object associated with vf module instance

        """
        return self.vnf_instance.vnf.vf_module

    @classmethod
    def create_from_api_response(cls,
                                 api_response: dict,
                                 vnf_instance: "VnfInstance") -> "VfModuleInstance":
        """Create vf module instance object using HTTP API response dictionary.

        Args:
            api_response (dict): HTTP API response content
            vnf_instance (VnfInstance): VnfInstance associated with VfModuleInstance

        Returns:
            VfModuleInstance: VfModuleInstance object

        """
        return cls(
            vnf_instance=vnf_instance,
            vf_module_id=api_response.get("vf-module-id"),
            is_base_vf_module=api_response.get("is-base-vf-module"),
            automated_assignment=api_response.get("automated-assignment"),
            vf_module_name=api_response.get("vf-module-name"),
            heat_stack_id=api_response.get("heat-stack-id"),
            orchestration_status=api_response.get("orchestration-status"),
            resource_version=api_response.get("resource-version"),
            model_invariant_id=api_response.get("model-invariant-id"),
            model_version_id=api_response.get("model-version-id"),
            persona_model_version=api_response.get("persona-model-version"),
            model_customization_id=api_response.get("model-customization-id"),
            widget_model_id=api_response.get("widget-model-id"),
            widget_model_version=api_response.get("widget-model-version"),
            contrail_service_instance_fqdn=api_response.get("contrail-service-instance-fqdn"),
            module_index=api_response.get("module-index"),
            selflink=api_response.get("selflink")
        )

    def delete(self) -> "VfModuleDeletionRequest":
        """Create deletion request.

        Send request to delete VF module instance

        Returns:
            VfModuleDeletionRequest: Deletion request object

        """
        self._logger.debug("Delete %s VF module", self.vf_module_id)
        return VfModuleDeletionRequest.send_request(self)


class VnfInstance(AaiElement):  # pylint: disable=R0902
    """VNF Instance class."""

    def __init__(self,  # pylint: disable=R0913, R0914, R0915
                 vnf_id: str,
                 vnf_type: str,
                 in_maint: bool,
                 is_closed_loop_disabled: bool,
                 vnf_name: str = None,
                 service_id: str = None,
                 regional_resource_zone: str = None,
                 prov_status: str = None,
                 operational_status: str = None,
                 equipment_role: str = None,
                 orchestration_status: str = None,
                 vnf_package_name: str = None,
                 vnf_discriptor_name: str = None,
                 job_id: str = None,
                 heat_stack_id: str = None,
                 mso_catalog_key: str = None,
                 management_option: str = None,
                 ipv4_oam_address: str = None,
                 ipv4_loopback0_address: str = None,
                 nm_lan_v6_address: str = None,
                 management_v6_address: str = None,
                 vcpu: int = None,
                 vcpu_units: str = None,
                 vmemory: int = None,
                 vmemory_units: str = None,
                 vdisk: int = None,
                 vdisk_units: str = None,
                 nshd: int = None,
                 nvm: int = None,
                 nnet: int = None,
                 resource_version: str = None,
                 encrypted_access_flag: bool = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 persona_model_version: str = None,
                 model_customization_id: str = None,
                 widget_model_id: str = None,
                 widget_model_version: str = None,
                 as_number: str = None,
                 regional_resource_subzone: str = None,
                 nf_type: str = None,
                 nf_function: str = None,
                 nf_role: str = None,
                 nf_naming_code: str = None,
                 selflink: str = None,
                 ipv4_oam_gateway_address: str = None,
                 ipv4_oam_gateway_address_prefix_length: int = None,
                 vlan_id_outer: int = None,
                 nm_profile_name: str = None) -> None:
        """Vnf instance object initialization.

        Args:
            vnf_id (str): Unique id of VNF. This is unique across the graph.
            vnf_type (str): String capturing type of vnf, that was intended to identify
                the ASDC resource. This field has been overloaded in service-specific ways and
                clients should expect changes to occur in the future to this field as ECOMP
                matures.
            in_maint (bool): used to indicate whether or not this object is in maintenance mode
                (maintenance mode = true). This field (in conjunction with prov-status)
                is used to suppress alarms and vSCL on VNFs/VMs.
            is_closed_loop_disabled (bool): used to indicate whether closed loop function is
                enabled on this node
            vnf_name (str, optional): Name of VNF. Defaults to None.
            service_id (str, optional): Unique identifier of service, does not necessarily map to
                ASDC service models. Defaults to None.
            regional_resource_zone (str, optional): Regional way of organizing pservers, source of
                truth should define values. Defaults to None.
            prov_status (str, optional): Trigger for operational monitoring of this resource by
                Service Assurance systems. Defaults to None.
            operational_status (str, optional): Indicator for whether the resource is considered
                operational. Valid values are in-service-path and out-of-service-path.
                Defaults to None.
            equipment_role (str, optional): Client should send valid enumerated value.
                Defaults to None.
            orchestration_status (str, optional): Orchestration status of this VNF, used by MSO.
                Defaults to None.
            vnf_package_name (str, optional): vnf package name. Defaults to None.
            vnf_discriptor_name (str, optional): vnf discriptor name. Defaults to None.
            job_id (str, optional): job id corresponding to vnf. Defaults to None.
            heat_stack_id (str, optional): Heat stack id corresponding to this instance,
                managed by MSO. Defaults to None.
            mso_catalog_key (str, optional): Corresponds to the SDN-C catalog id used to
                configure this VCE. Defaults to None.
            management_option (str, optional): identifier of managed customer. Defaults to None.
            ipv4_oam_address (str, optional): Address tail-f uses to configure generic-vnf,
                also used for troubleshooting and is IP used for traps generated by generic-vnf.
                Defaults to None.
            ipv4_loopback0_address (str, optional): v4 Loopback0 address. Defaults to None.
            nm_lan_v6_address (str, optional): v6 Loopback address. Defaults to None.
            management_v6_address (str, optional): v6 management address. Defaults to None.
            vcpu (int, optional): number of vcpus ordered for this instance of VNF,
                used for VNFs with no vservers/flavors, to be used only by uCPE. Defaults to None.
            vcpu_units (str, optional): units associated with vcpu, used for VNFs with no
                vservers/flavors, to be used only by uCPE. Defaults to None.
            vmemory (int, optional): number of GB of memory ordered for this instance of VNF,
                used for VNFs with no vservers/flavors, to be used only by uCPE. Defaults to None.
            vmemory_units (str, optional): units associated with vmemory, used for VNFs with
                no vservers/flavors, to be used only by uCPE. Defaults to None.
            vdisk (int, optional): number of vdisks ordered for this instance of VNF,
                used for VNFs with no vservers/flavors, to be used only uCPE. Defaults to None.
            vdisk_units (str, optional): units associated with vdisk, used for VNFs with
                no vservers/flavors, to be used only by uCPE. Defaults to None.
            nshd (int, optional): number of associated SHD in vnf. Defaults to None.
            nvm (int, optional): number of vms in vnf. Defaults to None.
            nnet (int, optional): number of network in vnf. Defaults to None.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to None.
            encrypted_access_flag (bool, optional): indicates whether generic-vnf access uses SSH.
                Defaults to None.
            model_invariant_id (str, optional): the ASDC model id for this resource or
                service model. Defaults to None.
            model_version_id (str, optional): the ASDC model version for this resource or
                service model. Defaults to None.
            persona_model_version (str, optional): the ASDC model version for this resource or
                service model. Defaults to None.
            model_customization_id (str, optional): captures the id of all the configuration used
                to customize the resource for the service. Defaults to None.
            widget_model_id (str, optional): the ASDC data dictionary widget model. This maps
                directly to the A&AI widget. Defaults to None.
            widget_model_version (str, optional): the ASDC data dictionary version of
                the widget model.This maps directly to the A&AI version of the widget.
                Defaults to None.
            as_number (str, optional): as-number of the VNF. Defaults to None.
            regional_resource_subzone (str, optional): represents sub zone of the rr plane.
                Defaults to None.
            nf_type (str, optional): Generic description of the type of NF. Defaults to None.
            nf_function (str, optional): English description of Network function that
                the specific VNF deployment is providing. Defaults to None.
            nf_role (str, optional): role in the network that this model will be providing.
                Defaults to None.
            nf_naming_code (str, optional): string assigned to this model used for naming purposes.
                Defaults to None.
            selflink (str, optional): Path to the controller object. Defaults to None.
            ipv4_oam_gateway_address (str, optional): Gateway address. Defaults to None.
            ipv4_oam_gateway_address_prefix_length (int, optional): Prefix length for oam-address.
                Defaults to None.
            vlan_id_outer (int, optional): Temporary location for S-TAG to get to VCE.
                Defaults to None.
            nm_profile_name (str, optional): Network Management profile of this VNF.
                Defaults to None.

        """
        super().__init__()
        self.vnf_id: str = vnf_id
        self.vnf_type: str = vnf_type
        self.in_maint: bool = in_maint
        self.is_closed_loop_disabled: bool = is_closed_loop_disabled
        self.vnf_name: str = vnf_name
        self.service_id: str = service_id
        self.regional_resource_zone: str = regional_resource_zone
        self.prov_status: str = prov_status
        self.operational_status: str = operational_status
        self.equipment_role: str = equipment_role
        self.orchestration_status: str = orchestration_status
        self.vnf_package_name: str = vnf_package_name
        self.vnf_discriptor_name: str = vnf_discriptor_name
        self.job_id: str = job_id
        self.heat_stack_id: str = heat_stack_id
        self.mso_catalog_key: str = mso_catalog_key
        self.management_option: str = management_option
        self.ipv4_oam_address: str = ipv4_oam_address
        self.ipv4_loopback0_address: str = ipv4_loopback0_address
        self.nm_lan_v6_address: str = nm_lan_v6_address
        self.management_v6_address: str = management_v6_address
        self.vcpu: int = vcpu
        self.vcpu_units: str = vcpu_units
        self.vmemory: int = vmemory
        self.vmemory_units: str = vmemory_units
        self.vdisk: int = vdisk
        self.vdisk_units: str = vdisk_units
        self.nshd: int = nshd
        self.nvm: int = nvm
        self.nnet: int = nnet
        self.resource_version: str = resource_version
        self.encrypted_access_flag: bool = encrypted_access_flag
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id
        self.persona_model_version: str = persona_model_version
        self.model_customization_id: str = model_customization_id
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version
        self.as_number: str = as_number
        self.regional_resource_subzone: str = regional_resource_subzone
        self.nf_type: str = nf_type
        self.nf_function: str = nf_function
        self.nf_role: str = nf_role
        self.nf_naming_code: str = nf_naming_code
        self.selflink: str = selflink
        self.ipv4_oam_gateway_address: str = ipv4_oam_gateway_address
        self.ipv4_oam_gateway_address_prefix_length: int = ipv4_oam_gateway_address_prefix_length
        self.vlan_id_outer: int = vlan_id_outer
        self.nm_profile_name: str = nm_profile_name

        self._vnf: "Vnf" = None

    def __repr__(self) -> str:
        """Vnf instance object representation.

        Returns:
            str: Human readable vnf instance representation

        """
        return (f"VnfInstance(vnf_id={self.vnf_id}, vnf_type={self.vnf_type}, "
                f"in_maint={self.in_maint}, "
                f"is_closed_loop_disabled={self.is_closed_loop_disabled})")

    @property
    def url(self) -> str:
        """Vnf instance url.

        Returns:
            str: VnfInstance url

        """
        return f"{self.base_url}{self.api_version}/network/generic-vnfs/generic-vnf/{self.vnf_id}"

    @property
    def vf_modules(self) -> Iterator[VfModuleInstance]:
        """Vf modules associated with vnf instance.

        Yields:
            VfModuleInstance: VfModuleInstance associated with VnfInstance

        """
        for vf_module in self.send_message_json("GET",
                                                f"GET VNF {self.vnf_name} VF modules",
                                                f"{self.url}/vf-modules").get("vf-module", []):
            yield VfModuleInstance.create_from_api_response(vf_module, self)

    @property
    def service_instance(self) -> "ServiceInstance":
        """Service instance associated with vnf instance.

        Every VnfInstace has to be associated with some ServiceInstance.

        Raises:
            AttributeError: No associated ServiceInstance found

        Returns:
            ServiceInstance: ServiceInstance object

        """
        customer: "Customer" = None
        service_subscription_type: str = None
        service_instance_id: str = None
        for relationship in self.relationships:
            if relationship.related_to == "service-instance":
                for data in relationship.relationship_data:
                    if data["relationship-key"] == "customer.global-customer-id":
                        customer = Customer.get_by_global_customer_id(
                            data["relationship-value"])
                    if data["relationship-key"] == "service-subscription.service-type":
                        service_subscription_type = data["relationship-value"]
                    if data["relationship-key"] == "service-instance.service-instance-id":
                        service_instance_id = data["relationship-value"]
        if not all([customer, service_subscription_type, service_instance_id]):
            raise AttributeError("VnfInstance has no valid service instance relationship")
        service_subscription: "ServiceSubscription" = \
            customer.get_service_subscription_by_service_type(service_subscription_type)
        return service_subscription.get_service_instance_by_id(service_instance_id)

    @property
    def vnf(self) -> "Vnf":
        """Vnf associated with that vnf instance.

        Raises:
            AttributeError: Could not find VNF for that VNF instance

        Returns:
            Vnf: Vnf object associated with vnf instance

        """
        if not self._vnf:
            for vnf in self.service_instance.service_subscription.sdc_service.vnfs:
                if vnf.metadata["UUID"] == self.model_version_id:
                    self._vnf = vnf
                    return self._vnf
            raise AttributeError("Couldn't find VNF for VNF instance")
        return self._vnf

    @classmethod
    def create_from_api_response(cls, api_response: dict) -> "VnfInstance":
        """Create vnf instance object using HTTP API response dictionary.

        Returns:
            VnfInstance: VnfInstance object

        """
        return cls(vnf_id=api_response.get("vnf-id"),
                   vnf_type=api_response.get("vnf-type"),
                   in_maint=api_response.get("in-maint"),
                   is_closed_loop_disabled=api_response.get("is-closed-loop-disabled"),
                   vnf_name=api_response.get("vnf-name"),
                   service_id=api_response.get("service-id"),
                   regional_resource_zone=api_response.get("regional-resource-zone"),
                   prov_status=api_response.get("prov-status"),
                   operational_status=api_response.get("operational-status"),
                   equipment_role=api_response.get("equipment-role"),
                   orchestration_status=api_response.get("orchestration-status"),
                   vnf_package_name=api_response.get("vnf-package-name"),
                   vnf_discriptor_name=api_response.get("vnf-discriptor-name"),
                   job_id=api_response.get("job-id"),
                   heat_stack_id=api_response.get("heat-stack-id"),
                   mso_catalog_key=api_response.get("mso-catalog-key"),
                   management_option=api_response.get("management-option"),
                   ipv4_oam_address=api_response.get("ipv4-oam-address"),
                   ipv4_loopback0_address=api_response.get("ipv4-loopback0-address"),
                   nm_lan_v6_address=api_response.get("nm-lan-v6-address"),
                   management_v6_address=api_response.get("management-v6-address"),
                   vcpu=api_response.get("vcpu"),
                   vcpu_units=api_response.get("vcpu-units"),
                   vmemory=api_response.get("vmemory"),
                   vmemory_units=api_response.get("vmemory-units"),
                   vdisk=api_response.get("vdisk"),
                   vdisk_units=api_response.get("vdisk-units"),
                   nshd=api_response.get("nshd"),
                   nvm=api_response.get("nvm"),
                   nnet=api_response.get("nnet"),
                   resource_version=api_response.get("resource-version"),
                   encrypted_access_flag=api_response.get("encrypted-access-flag"),
                   model_invariant_id=api_response.get("model-invariant-id"),
                   model_version_id=api_response.get("model-version-id"),
                   persona_model_version=api_response.get("persona-model-version"),
                   model_customization_id=api_response.get("model-customization-id"),
                   widget_model_id=api_response.get("widget-model-id"),
                   widget_model_version=api_response.get("widget-model-version"),
                   as_number=api_response.get("as-number"),
                   regional_resource_subzone=api_response.get("regional-resource-subzone"),
                   nf_type=api_response.get("nf-type"),
                   nf_function=api_response.get("nf-function"),
                   nf_role=api_response.get("nf-role"),
                   nf_naming_code=api_response.get("nf-naming-code"),
                   selflink=api_response.get("selflink"),
                   ipv4_oam_gateway_address=api_response.get("ipv4-oam-gateway-address"),
                   ipv4_oam_gateway_address_prefix_length=\
                       api_response.get("ipv4-oam-gateway-address-prefix-length"),
                   vlan_id_outer=api_response.get("vlan-id-outer"),
                   nm_profile_name=api_response.get("nm-profile-name"))

    def add_vf_module(self,
                      vf_module: "VfModule",
                      vf_module_instance_name: str = None,
                      use_vnf_api=False,
                      vnf_parameters: Iterable["VnfParameter"] = None) -> "VfModuleInstantiation":
        """Instantiate vf module for that VNF instance.

        Args:
            vf_module (VfModule): VfModule to instantiate
            vf_module_instance_name (str, optional): VfModule instance name. Defaults to None.
            use_vnf_api (bool, optional): Flague which determines if VNF_API should be used.
                Set to False to use GR_API. Defaults to False.
            vnf_parameters (Iterable[VnfParameter], optional): VnfParameters to use for preloading.
                Defaults to None.

        Returns:
            VfModuleInstantiation: VfModuleInstantiation request object

        """
        return onapsdk.so.instantiation.VfModuleInstantiation.instantiate_ala_carte(
            vf_module,
            self,
            vf_module_instance_name,
            use_vnf_api,
            vnf_parameters
        )

    def delete(self) -> "VnfDeletionRequest":
        """Create VNF deletion request.

        Send request to delete VNF instance

        Returns:
            VnfDeletionRequest: Deletion request

        """
        self._logger.debug("Delete %s VNF", self.vnf_id)
        return VnfDeletionRequest.send_request(self)


class ServiceInstance(AaiElement):  # pylint: disable=R0902
    """Service instanve class."""

    def __init__(self,  # pylint: disable=R0913, R0914
                 service_subscription: "ServiceSubscription",
                 instance_id: str,
                 instance_name: str = None,
                 service_type: str = None,
                 service_role: str = None,
                 environment_context: str = None,
                 workload_context: str = None,
                 created_at: str = None,
                 updated_at: str = None,
                 description: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 persona_model_version: str = None,
                 widget_model_id: str = None,
                 widget_model_version: str = None,
                 bandwith_total: str = None,
                 vhn_portal_url: str = None,
                 service_instance_location_id: str = None,
                 resource_version: str = None,
                 selflink: str = None,
                 orchestration_status: str = None,
                 input_parameters: str = None) -> None:
        """Service instance object initialization.

        Args:
            service_subscription (ServiceSubscription): service subscription which is belongs to
            instance_id (str): Uniquely identifies this instance of a service
            instance_name (str, optional): This field will store a name assigned to
                the service-instance. Defaults to None.
            service_type (str, optional): String capturing type of service. Defaults to None.
            service_role (str, optional): String capturing the service role. Defaults to None.
            environment_context (str, optional): This field will store the environment context
                assigned to the service-instance. Defaults to None.
            workload_context (str, optional): This field will store the workload context assigned to
                the service-instance. Defaults to None.
            created_at (str, optional): Create time of Network Service. Defaults to None.
            updated_at (str, optional): Last update of Network Service. Defaults to None.
            description (str, optional): Short description for service-instance. Defaults to None.
            model_invariant_id (str, optional): The ASDC model id for this resource or
                service model. Defaults to None.
            model_version_id (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
            persona_model_version (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
            widget_model_id (str, optional): he ASDC data dictionary widget model. This maps
                directly to the A&AI widget. Defaults to None.
            widget_model_version (str, optional): The ASDC data dictionary version of the widget
                model. This maps directly to the A&AI version of the widget. Defaults to None.
            bandwith_total (str, optional): Indicates the total bandwidth to be used for this
                service. Defaults to None.
            vhn_portal_url (str, optional): URL customers will use to access the vHN Portal.
                Defaults to None.
            service_instance_location_id (str, optional): An identifier that customers assign to
                the location where this service is being used. Defaults to None.
            resource_version (str, optional): Used for optimistic concurrency. Must be empty on
                create, valid on update and delete. Defaults to None.
            selflink (str, optional): Path to the controller object. Defaults to None.
            orchestration_status (str, optional): Orchestration status of this service.
                Defaults to None.
            input_parameters (str, optional): String capturing request parameters from SO to
                pass to Closed Loop. Defaults to None.
        """
        super().__init__()
        self.service_subscription: "ServiceSubscription" = service_subscription
        self.instance_id: str = instance_id
        self.instance_name: str = instance_name
        self.service_type: str = service_type
        self.service_role: str = service_role
        self.environment_context: str = environment_context
        self.workload_context: str = workload_context
        self.created_at: str = created_at
        self.updated_at: str = updated_at
        self.description: str = description
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id
        self.persona_model_version: str = persona_model_version
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version
        self.bandwith_total: str = bandwith_total
        self.vhn_portal_url: str = vhn_portal_url
        self.service_instance_location_id: str = service_instance_location_id
        self.resource_version: str = resource_version
        self.selflink: str = selflink
        self.orchestration_status: str = orchestration_status
        self.input_parameters: str = input_parameters

    def __repr__(self) -> str:
        """Service instance object representation.

        Returns:
            str: Human readable service instance representation

        """
        return (f"ServiceInstance(instance_id={self.instance_id}, "
                f"instance_name={self.instance_name})")

    @property
    def url(self) -> str:
        """Service instance resource URL.

        Returns:
            str: Service instance url

        """
        return (
            f"{self.service_subscription.url}/service-instances/service-instance/{self.instance_id}"
        )

    @property
    def vnf_instances(self) -> Iterator[VnfInstance]:
        """Vnf instances associated with service instance.

        Returns iterator of VnfInstances representing VNF instantiated for that service

        Raises:
            ValueError: Request sent to get vnf instances returns HTTP error code.

        Yields:
            VnfInstance: VnfInstance object

        """
        for relationship in self.relationships:
            if relationship.related_to == "generic-vnf":
                yield VnfInstance.create_from_api_response(\
                    self.send_message_json("GET",
                                           f"Get {self.instance_id} VNF",
                                           f"{self.base_url}{relationship.related_link}",
                                           exception=ValueError))

    def add_vnf(self,  # pylint: disable=R0913
                vnf: "Vnf",
                line_of_business: "LineOfBusiness",
                platform: "Platform",
                vnf_instance_name: str = None,
                use_vnf_api: bool = False) -> "VnfInstantiation":
        """Add vnf into service instance.

        Instantiate VNF.

        Args:
            vnf (Vnf): Vnf from service configuration to instantiate
            line_of_business (LineOfBusiness): LineOfBusiness to use in instantiation request
            platform (Platform): Platform to use in instantiation request
            vnf_instance_name (str, optional): VNF instantion name.
                If no value is provided it's going to be
                "Python_ONAP_SDK_vnf_instance_{str(uuid4())}".
                Defaults to None.
            use_vnf_api (bool, optional): Flague to determine if VNF_API or GR_API
                should be used to instantiate. Defaults to False.

        Raises:
            AttributeError: Service orchestration status is not "Active"
            ValueError: Instantiation request error.

        Returns:
            VnfInstantiation: VnfInstantiation request object

        """
        if self.orchestration_status != "Active":
            raise AttributeError("Service has invalid orchestration status")
        return onapsdk.so.instantiation.VnfInstantiation.instantiate_ala_carte(
            self,
            vnf,
            line_of_business,
            platform,
            vnf_instance_name,
            use_vnf_api
        )

    def delete(self) -> "ServiceDeletionRequest":
        """Create service deletion request.

        Send a request to delete service instance

        Returns:
            ServiceDeletionRequest: Deletion request object

        """
        self._logger.debug("Delete %s service instance", self.instance_id)
        return ServiceDeletionRequest.send_request(self)


@dataclass
class ServiceSubscription(AaiElement):
    """Service subscription class."""

    service_type: str
    resource_version: str
    customer: "Customer"

    def __init__(self, customer: "Customer", service_type: str, resource_version: str) -> None:
        """Service subscription object initialization.

        Args:
            customer (Customer): Customer object
            service_type (str): Service type
            resource_version (str): Service subscription resource version
        """
        super().__init__()
        self.customer: "Customer" = customer
        self.service_type: str = service_type
        self.resource_version: str = resource_version

    def _get_service_instance_by_filter_parameter(self,
                                                  filter_parameter_name: str,
                                                  filter_parameter_value: str) -> ServiceInstance:
        """Call a request to get service instance with given filter parameter and value.

        Args:
            filter_parameter_name (str): Name of parameter to filter
            filter_parameter_value (str): Value of filter parameter

        Raises:
            ValueError: Service instance with given filter parameters
                doesn't exist

        Returns:
            ServiceInstance: ServiceInstance object

        """
        service_instance: dict = self.send_message_json(
            "GET",
            f"Get service instance with {filter_parameter_value} {filter_parameter_name}",
            f"{self.url}/service-instances?{filter_parameter_name}={filter_parameter_value}",
            exception=ValueError
        )["service-instance"][0]
        return ServiceInstance(
            service_subscription=self,
            instance_id=service_instance.get("service-instance-id"),
            instance_name=service_instance.get("service-instance-name"),
            service_type=service_instance.get("service-type"),
            service_role=service_instance.get("service-role"),
            environment_context=service_instance.get("environment-context"),
            workload_context=service_instance.get("workload-context"),
            created_at=service_instance.get("created-at"),
            updated_at=service_instance.get("updated-at"),
            description=service_instance.get("description"),
            model_invariant_id=service_instance.get("model-invariant-id"),
            model_version_id=service_instance.get("model-version-id"),
            persona_model_version=service_instance.get("persona-model-version"),
            widget_model_id=service_instance.get("widget-model-id"),
            widget_model_version=service_instance.get("widget-model-version"),
            bandwith_total=service_instance.get("bandwidth-total"),
            vhn_portal_url=service_instance.get("vhn-portal-url"),
            service_instance_location_id=service_instance.get("service-instance-location-id"),
            resource_version=service_instance.get("resource-version"),
            selflink=service_instance.get("selflink"),
            orchestration_status=service_instance.get("orchestration-status"),
            input_parameters=service_instance.get("input-parameters")
        )

    @classmethod
    def create_from_api_response(cls,
                                 api_response: dict,
                                 customer: "Customer") -> "ServiceSubscription":
        """Create service subscription using API response dict.

        Returns:
            ServiceSubscription: ServiceSubscription object.

        """
        return cls(
            service_type=api_response.get("service-type"),
            resource_version=api_response.get("resource-version"),
            customer=customer
        )

    @property
    def url(self) -> str:
        """Cloud region object url.

        URL used to call CloudRegion A&AI API

        Returns:
            str: CloudRegion object url

        """
        return (
            f"{self.base_url}{self.api_version}/business/customers/"
            f"customer/{self.customer.global_customer_id}/service-subscriptions/"
            f"service-subscription/{self.service_type}"
        )

    @property
    def service_instances(self) -> Iterator[ServiceInstance]:
        """Service instances.

        Yields:
            Iterator[ServiceInstance]: Service instance

        """
        for service_instance in \
            self.send_message_json("GET",
                                   (f"Get all service instances for {self.service_type} service "
                                    f"subscription"),
                                   f"{self.url}/service-instances").get("service-instance", []):
            yield ServiceInstance(
                service_subscription=self,
                instance_id=service_instance.get("service-instance-id"),
                instance_name=service_instance.get("service-instance-name"),
                service_type=service_instance.get("service-type"),
                service_role=service_instance.get("service-role"),
                environment_context=service_instance.get("environment-context"),
                workload_context=service_instance.get("workload-context"),
                created_at=service_instance.get("created-at"),
                updated_at=service_instance.get("updated-at"),
                description=service_instance.get("description"),
                model_invariant_id=service_instance.get("model-invariant-id"),
                model_version_id=service_instance.get("model-version-id"),
                persona_model_version=service_instance.get("persona-model-version"),
                widget_model_id=service_instance.get("widget-model-id"),
                widget_model_version=service_instance.get("widget-model-version"),
                bandwith_total=service_instance.get("bandwidth-total"),
                vhn_portal_url=service_instance.get("vhn-portal-url"),
                service_instance_location_id=service_instance.get("service-instance-location-id"),
                resource_version=service_instance.get("resource-version"),
                selflink=service_instance.get("selflink"),
                orchestration_status=service_instance.get("orchestration-status"),
                input_parameters=service_instance.get("input-parameters")
            )

    @property
    def cloud_region(self) -> "CloudRegion":
        """Cloud region associated with service subscription.

        Raises:
            AttributeError: Service subscription has no associated cloud region.

        Returns:
            CloudRegion: CloudRegion object

        """
        cloud_owner: str = None
        cloud_region: str = None
        for relationship in self.relationships:
            if relationship.related_to == "tenant":
                for data in relationship.relationship_data:
                    if data["relationship-key"] == "cloud-region.cloud-owner":
                        cloud_owner = data["relationship-value"]
                    if data["relationship-key"] == "cloud-region.cloud-region-id":
                        cloud_region = data["relationship-value"]
        if not all([cloud_owner, cloud_region]):
            raise AttributeError("ServiceSubscription has no CloudOwner and/or "
                                 "CloudRegion relationship")
        return CloudRegion.get_by_id(cloud_owner, cloud_region)

    @property
    def tenant(self) -> "Tenant":
        """Tenant associated with service subscription.

        Raises:
            AttributeError: Service subscription has no associated tenants

        Returns:
            Tenant: Tenant object

        """
        for relationship in self.relationships:
            if relationship.related_to == "tenant":
                for data in relationship.relationship_data:
                    if data["relationship-key"] == "tenant.tenant-id":
                        return self.cloud_region.get_tenant(data["relationship-value"])
        raise AttributeError("ServiceSubscription has no tenant relationship")

    @property
    def sdc_service(self) -> "SdcService":
        """Sdc service.

        SDC service associated with service subscription.

        Returns:
            SdcService: SdcService object

        """
        return SdcService(self.service_type)

    def get_service_instance_by_id(self, service_instance_id) -> ServiceInstance:
        """Get service instance using it's ID.

        Args:
            service_instance_id (str): ID of the service instance

        Raises:
            ValueError: service subscription has no related service instance with given ID

        Returns:
            ServiceInstance: ServiceInstance object

        """
        return self._get_service_instance_by_filter_parameter(
            "service-instance-id",
            service_instance_id
        )

    def get_service_instance_by_name(self, service_instance_name: str) -> ServiceInstance:
        """Get service instance using it's name.

        Args:
            service_instance_name (str): Name of the service instance

        Raises:
            ValueError: service subscription has no related service instance with given name

        Returns:
            ServiceInstance: ServiceInstance object

        """
        return self._get_service_instance_by_filter_parameter(
            "service-instance-name",
            service_instance_name
        )

    def link_to_cloud_region_and_tenant(self,
                                        cloud_region: "CloudRegion",
                                        tenant: "Tenant") -> None:
        """Create relationship between object and cloud region with tenant.

        Args:
            cloud_region (CloudRegion): Cloud region to link to
            tenant (Tenant): Cloud region tenant to link to
        """
        relationship: Relationship = Relationship(
            related_to="tenant",
            related_link=tenant.url,
            relationship_data=[
                {
                    "relationship-key": "cloud-region.cloud-owner",
                    "relationship-value": cloud_region.cloud_owner,
                },
                {
                    "relationship-key": "cloud-region.cloud-region-id",
                    "relationship-value": cloud_region.cloud_region_id,
                },
                {
                    "relationship-key": "tenant.tenant-id",
                    "relationship-value": tenant.tenant_id,
                },
            ],
            related_to_property=[
                {"property-key": "tenant.tenant-name", "property-value": tenant.name}
            ],
        )
        self.add_relationship(relationship)


class Customer(AaiElement):
    """Customer class."""

    def __init__(self,
                 global_customer_id: str,
                 subscriber_name: str,
                 subscriber_type: str,
                 resource_version: str = None) -> None:
        """Initialize Customer class object.

        Args:
            global_customer_id (str): Global customer id used across ONAP to
                uniquely identify customer.
            subscriber_name (str): Subscriber name, an alternate way to retrieve a customer.
            subscriber_type (str): Subscriber type, a way to provide VID with
                only the INFRA customers.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update
                and delete. Defaults to None.

        """
        super().__init__()
        self.global_customer_id: str = global_customer_id
        self.subscriber_name: str = subscriber_name
        self.subscriber_type: str = subscriber_type
        self.resource_version: str = resource_version

    def __repr__(self) -> str:  # noqa
        """Customer description.

        Returns:
            str: Customer object description

        """
        return (f"Customer(global_customer_id={self.global_customer_id}, "
                f"subscriber_name={self.subscriber_name}, "
                f"subscriber_type={self.subscriber_type}, "
                f"resource_version={self.resource_version})")

    def get_service_subscription_by_service_type(self, service_type: str) -> ServiceSubscription:
        """Get subscribed service by service type.

        Call a request to get service subscriptions filtered by service-type parameter.

        Args:
            service_type (str): Service type

        Raises:
            ValueError: No service subscription with given service-type.

        Returns:
            ServiceSubscription: Service subscription

        """
        response: dict = self.send_message_json(
            "GET",
            f"Get service subscription with {service_type} service type",
            (f"{self.base_url}{self.api_version}/business/customers/"
             f"customer/{self.global_customer_id}/service-subscriptions"
             f"?service-type={service_type}"),
            exception=ValueError
        )
        return ServiceSubscription.create_from_api_response(response["service-subscription"][0],
                                                            self)

    @classmethod
    def get_all(cls,
                global_customer_id: str = None,
                subscriber_name: str = None,
                subscriber_type: str = None) -> Iterator["Customer"]:
        """Get all customers.

        Call an API to retrieve all customers. It can be filtered
            by global-customer-id, subscriber-name and/or subsriber-type.

        Args:
            global_customer_id (str): global-customer-id to filer customers by. Defaults to None.
            subscriber_name (str): subscriber-name to filter customers by. Defaults to None.
            subscriber_type (str): subscriber-type to filter customers by. Defaults to None.

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "global-customer-id": global_customer_id,
                "subscriber-name": subscriber_name,
                "subscriber-type": subscriber_type,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/business/customers?"
                    f"{urlencode(filter_parameters)}")
        for customer in cls.send_message_json("GET", "get customers", url).get("customer", []):
            yield Customer(
                global_customer_id=customer["global-customer-id"],
                subscriber_name=customer["subscriber-name"],
                subscriber_type=customer["subscriber-type"],
                resource_version=customer["resource-version"],
            )

    @classmethod
    def get_by_global_customer_id(cls, global_customer_id: str) -> "Customer":
        """Get customer by it's global customer id.

        Args:
            global_customer_id (str): global customer ID

        Returns:
            Customer: Customer with given global_customer_id

        Raises:
            ValueError: Customer with given global_customer_id doesn't exist

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Get {global_customer_id} customer",
            f"{cls.base_url}{cls.api_version}/business/customers/customer/{global_customer_id}",
            exception=ValueError
        )
        print(response)
        return Customer(
            global_customer_id=response["global-customer-id"],
            subscriber_name=response["subscriber-name"],
            subscriber_type=response["subscriber-type"],
            resource_version=response["resource-version"],
        )

    @classmethod
    def create(cls,
               global_customer_id: str,
               subscriber_name: str,
               subscriber_type: str) -> "Customer":
        """Create customer.

        Args:
            global_customer_id (str): Global customer id used across ONAP
                to uniquely identify customer.
            subscriber_name (str): Subscriber name, an alternate way
                to retrieve a customer.
            subscriber_type (str): Subscriber type, a way to provide
                VID with only the INFRA customers.

        Returns:
            Customer: Customer object.

        """
        url: str = (
            f"{cls.base_url}{cls.api_version}/business/customers/"
            f"customer/{global_customer_id}"
        )
        cls.send_message(
            "PUT",
            "declare customer",
            url,
            data=jinja_env()
            .get_template("customer_create.json.j2")
            .render(
                global_customer_id=global_customer_id,
                subscriber_name=subscriber_name,
                subscriber_type=subscriber_type,
            ),
        )
        response: dict = cls.send_message_json(
            "GET", "get created customer", url
        )  # Call API one more time to get Customer's resource version
        return Customer(
            global_customer_id=response["global-customer-id"],
            subscriber_name=response["subscriber-name"],
            subscriber_type=response["subscriber-type"],
            resource_version=response["resource-version"],
        )

    @property
    def url(self) -> str:
        """Return customer object url.

        Unique url address to get customer's data.

        Returns:
            str: Customer object url

        """
        return (
            f"{self.base_url}{self.api_version}/business/customers/customer/"
            f"{self.global_customer_id}?resource-version={self.resource_version}"
        )

    @property
    def service_subscriptions(self) -> Iterator[ServiceSubscription]:
        """Service subscriptions of customer resource.

        Yields:
            ServiceSubscription: ServiceSubscription object

        """
        response: dict = self.send_message_json(
            "GET",
            "get customer service subscriptions",
            f"{self.base_url}{self.api_version}/business/customers/"
            f"customer/{self.global_customer_id}/service-subscriptions"
        )
        for service_subscription in response.get("service-subscription", []):
            yield ServiceSubscription.create_from_api_response(
                service_subscription,
                self
            )

    def subscribe_service(self, service: SdcService) -> "ServiceSubscription":
        """Create SDC Service subscription.

        If service is already subscribed it won't create a new resource but use the
            existing one.

        Args:
            service (SdcService): SdcService object to subscribe.

        Raises:
            ValueError: Request response with HTTP error code

        """
        try:
            return self.get_service_subscription_by_service_type(service.name)
        except ValueError:
            pass
        self.send_message(
            "PUT",
            "Create service subscription",
            (f"{self.base_url}{self.api_version}/business/customers/"
             f"customer/{self.global_customer_id}/service-subscriptions/"
             f"service-subscription/{service.name}"),
            data=jinja_env()
            .get_template("customer_service_subscription_create.json.j2")
            .render(
                service_id=service.unique_uuid,
            ),
            exception=ValueError
        )
        return self.get_service_subscription_by_service_type(service.name)


class OwningEntity(AaiElement):
    """Owning entity class."""

    def __init__(self, name: str, owning_entity_id: str, resource_version: str) -> None:
        """Owning entity object initialization.

        Args:
            name (str): Owning entity name
            owning_entity_id (str): owning entity ID
            resource_version (str): resource version
        """
        super().__init__()
        self.name: str = name
        self.owning_entity_id: str = owning_entity_id
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Owning entity object representation.

        Returns:
            str: Owning entity object representation

        """
        return f"OwningEntity(name={self.name}, owning_entity_id={self.owning_entity_id})"

    @property
    def url(self) -> str:
        """Owning entity object url.

        Returns:
            str: Url

        """
        return (f"{self.base_url}{self.api_version}/business/owning-entities/owning-entity/"
                f"{self.owning_entity_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls) -> Iterator["OwningEntity"]:
        """Get all owning entities.

        Yields:
            OwningEntity: OwningEntity object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/owning-entities"
        for owning_entity in cls.send_message_json("GET",
                                                   "Get A&AI owning entities",
                                                   url).get("owning-entity", []):
            yield cls(
                owning_entity.get("owning-entity-name"),
                owning_entity.get("owning-entity-id"),
                owning_entity.get("resource-version")
            )

    @classmethod
    def get_by_owning_entity_id(cls, owning_entity_id: str) -> "OwningEntity":
        """Get owning entity by it's ID.

        Args:
            owning_entity_id (str): owning entity object id

        Returns:
            OwningEntity: OwningEntity object

        """
        response: dict = cls.send_message_json(
            "GET",
            "Get A&AI owning entity",
            (f"{cls.base_url}{cls.api_version}/business/owning-entities/"
             f"owning-entity/{owning_entity_id}"),
            exception=ValueError
        )
        return cls(
            response.get("owning-entity-name"),
            response.get("owning-entity-id"),
            response.get("resource-version")
        )

    @classmethod
    def get_by_owning_entity_name(cls, owning_entity_name: str) -> "OwningEntity":
        """Get owning entity resource by it's name.

        Raises:
            ValueError: Owning entity with given name doesn't exist

        Returns:
            OwningEntity: Owning entity with given name

        """
        for owning_entity in cls.get_all():
            if owning_entity.name == owning_entity_name:
                return owning_entity
        raise ValueError

    @classmethod
    def create(cls, name: str, owning_entity_id: str = None) -> "OwningEntity":
        """Create owning entity A&AI resource.

        Args:
            name (str): owning entity name
            owning_entity_id (str): owning entity ID. Defaults to None.

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            OwningEntity: Created OwningEntity object

        """
        if not owning_entity_id:
            owning_entity_id = str(uuid4())
        cls.send_message(
            "PUT",
            "Declare A&AI owning entity",
            (f"{cls.base_url}{cls.api_version}/business/owning-entities/"
             f"owning-entity/{owning_entity_id}"),
            data=jinja_env().get_template("aai_owning_entity_create.json.j2").render(
                owning_entity_name=name,
                owning_entity_id=owning_entity_id
            ),
            exception=ValueError
        )
        return cls.get_by_owning_entity_id(owning_entity_id)
