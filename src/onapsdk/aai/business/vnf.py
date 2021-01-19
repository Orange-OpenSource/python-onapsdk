"""Vnf instance module."""

from typing import Iterable, Iterator

from onapsdk.so.deletion import VnfDeletionRequest
from onapsdk.so.instantiation import VfModuleInstantiation
from onapsdk.exceptions import ResourceNotFound

from .instance import Instance
from .vf_module import VfModuleInstance


class VnfInstance(Instance):  # pylint: disable=too-many-instance-attributes
    """VNF Instance class."""

    def __init__(self,  # pylint: disable=too-many-arguments, too-many-locals
                 service_instance: "ServiceInstance",
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
        super().__init__(resource_version=resource_version,
                         model_invariant_id=model_invariant_id,
                         model_version_id=model_version_id)
        self.service_instance: "ServiceInstance" = service_instance
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
        self.encrypted_access_flag: bool = encrypted_access_flag
        self.model_customization_id: str = model_customization_id
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
        self.persona_model_version: str = persona_model_version
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version

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
    def vnf(self) -> "Vnf":
        """Vnf associated with that vnf instance.

        Raises:
            ResourceNotFound: Could not find VNF for that VNF instance

        Returns:
            Vnf: Vnf object associated with vnf instance

        """
        if not self._vnf:
            for vnf in self.service_instance.service_subscription.sdc_service.vnfs:
                if vnf.metadata["UUID"] == self.model_version_id:
                    self._vnf = vnf
                    return self._vnf

            msg = (
                f'Could not find VNF for the VNF instance'
                f' with model version ID "{self.model_version_id}"'
            )
            raise ResourceNotFound(msg)
        return self._vnf

    @classmethod
    def create_from_api_response(cls, api_response: dict,
                                 service_instance: "ServiceInstance") -> "VnfInstance":
        """Create vnf instance object using HTTP API response dictionary.

        Returns:
            VnfInstance: VnfInstance object

        """
        return cls(service_instance=service_instance,
                   vnf_id=api_response.get("vnf-id"),
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
                   model_invariant_id=api_response.get("model-invariant-id"),
                   model_version_id=api_response.get("model-version-id"),
                   encrypted_access_flag=api_response.get("encrypted-access-flag"),
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

    def add_vf_module(self,  # pylint: disable=too-many-arguments
                      vf_module: "VfModule",
                      cloud_region: "CloudRegion" = None,
                      tenant: "Tenant" = None,
                      vf_module_instance_name: str = None,
                      vnf_parameters: Iterable["InstantiationParameter"] = None)\
                           -> "VfModuleInstantiation":
        """Instantiate vf module for that VNF instance.

        Args:
            vf_module (VfModule): VfModule to instantiate
            cloud_region (CloudRegion, optional): Cloud region to use in instantiation request.
                Defaults to None.
                THAT PROPERTY WILL BE REQUIRED IN ONE OF THE FUTURE RELEASE. REFACTOR YOUR CODE
                TO USE IT!.
            tenant (Tenant, optional): Tenant to use in instnatiation request.
                Defaults to None.
                THAT PROPERTY WILL BE REQUIRED IN ONE OF THE FUTURE RELEASE. REFACTOR YOUR CODE
                TO USE IT!.
            vf_module_instance_name (str, optional): VfModule instance name. Defaults to None.
            vnf_parameters (Iterable[InstantiationParameter], optional): InstantiationParameter
                to use for preloading. Defaults to None.

        Returns:
            VfModuleInstantiation: VfModuleInstantiation request object

        """
        return VfModuleInstantiation.instantiate_ala_carte(
            vf_module,
            self,
            cloud_region=cloud_region,
            tenant=tenant,
            vf_module_instance_name=vf_module_instance_name,
            vnf_parameters=vnf_parameters
        )

    def delete(self) -> "VnfDeletionRequest":
        """Create VNF deletion request.

        Send request to delete VNF instance

        Returns:
            VnfDeletionRequest: Deletion request

        """
        self._logger.debug("Delete %s VNF", self.vnf_id)
        return VnfDeletionRequest.send_request(self)
