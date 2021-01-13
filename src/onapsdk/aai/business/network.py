"""Network instance module."""

from onapsdk.so.deletion import NetworkDeletionRequest

from .instance import Instance


class NetworkInstance(Instance):  # pylint: disable=too-many-instance-attributes
    """Network instance class."""

    def __init__(self,  # pylint: disable=too-many-arguments, too-many-locals
                 service_instance: "ServiceInstance",
                 network_id: str,
                 is_bound_to_vpn: bool,
                 is_provider_network: bool,
                 is_shared_network: bool,
                 is_external_network: bool,
                 network_name: str = None,
                 network_type: str = None,
                 network_role: str = None,
                 network_technology: str = None,
                 neutron_network_id: str = None,
                 service_id: str = None,
                 network_role_instance: str = None,
                 resource_version: str = None,
                 orchestration_status: str = None,
                 heat_stack_id: str = None,
                 mso_catalog_key: str = None,
                 model_invariant_id: str = None,
                 contrail_network_fqdn: str = None,
                 persona_model_version: str = None,
                 model_version_id: str = None,
                 model_customization_id: str = None,
                 widget_model_id: str = None,
                 physical_network_name: str = None,
                 widget_model_version: str = None,
                 selflink: str = None,
                 operational_status: str = None,
                 is_trunked: bool = None):
        """Network instance object initialization.

        Args:
            service_instance (ServiceInstance): Service instance object
            network_id (str): Network ID, should be uuid. Unique across A&AI.
            is_bound_to_vpn (bool): Set to true if bound to VPN
            is_provider_network (bool): boolean indicatating whether or not network
                is a provider network.
            is_shared_network (bool): boolean indicatating whether
                or not network is a shared network.
            is_external_network (bool): boolean indicatating whether
                or not network is an external network.
            network_name (str, optional): Name of the network, governed by some naming convention.
                Defaults to None.
            network_type (str, optional): Type of the network. Defaults to None.
            network_role (str, optional): Role the network. Defaults to None.
            network_technology (str, optional): Network technology. Defaults to None.
            neutron_network_id (str, optional): Neutron network id of this Interface.
                Defaults to None.
            service_id (str, optional): Unique identifier of service from ASDC.
                Does not strictly map to ASDC services. Defaults to None.
            network_role_instance (str, optional): network role instance. Defaults to None.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to None.
            orchestration_status (str, optional): Orchestration status of this VNF,
                mastered by MSO. Defaults to None.
            heat_stack_id (str, optional): Heat stack id corresponding to this instance,
                managed by MSO. Defaults to None.
            mso_catalog_key (str, optional): Corresponds to the SDN-C catalog id used to
                configure this VCE. Defaults to None.
            contrail_network_fqdn (str, optional): Contrail FQDN for the network. Defaults to None.
            model_invariant_id (str, optional): the ASDC model id for this resource
                or service model. Defaults to None.
            model_version_id (str, optional): the ASDC model version for this resource
                or service model. Defaults to None.
            persona_model_version (str, optional): the ASDC model version for this resource
                or service model. Defaults to None.
            model_customization_id (str, optional): captures the id of all the configuration
                used to customize the resource for the service. Defaults to None.
            widget_model_id (str, optional): the ASDC data dictionary widget model.
                This maps directly to the A&AI widget. Defaults to None.
            widget_model_version (str, optional): the ASDC data dictionary version of
                the widget model. This maps directly to the A&AI version of the widget.
                Defaults to None.
            physical_network_name (str, optional): Name associated with the physical network.
                Defaults to None.
            selflink (str, optional): Path to the controller object. Defaults to None.
            operational_status (str, optional): Indicator for whether the resource is considered
                operational. Defaults to None.
            is_trunked (bool, optional): Trunked network indication. Defaults to None.
        """
        super().__init__(resource_version=resource_version,
                         model_version_id=model_version_id,
                         model_invariant_id=model_invariant_id)
        self.service_instance: "ServiceInstance" = service_instance
        self.network_id: str = network_id
        self.is_bound_to_vpn: bool = is_bound_to_vpn
        self.is_provider_network: bool = is_provider_network
        self.is_shared_network: bool = is_shared_network
        self.is_external_network: bool = is_external_network
        self.network_name: str = network_name
        self.network_type: str = network_type
        self.network_role: str = network_role
        self.network_technology: str = network_technology
        self.neutron_network_id: str = neutron_network_id
        self.service_id: str = service_id
        self.network_role_instance: str = network_role_instance
        self.orchestration_status: str = orchestration_status
        self.heat_stack_id: str = heat_stack_id
        self.mso_catalog_key: str = mso_catalog_key
        self.contrail_network_fqdn: str = contrail_network_fqdn
        self.model_customization_id: str = model_customization_id
        self.physical_network_name: str = physical_network_name
        self.selflink: str = selflink
        self.operational_status: str = operational_status
        self.is_trunked: bool = is_trunked
        self.persona_model_version: str = persona_model_version
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version

    def __repr__(self) -> str:
        """Network instance object representation.

        Returns:
            str: Human readable network instance representation

        """
        return (f"NetworkInstance(network_id={self.network_id}, "
                f"network_name={self.network_name}, "
                f"is_bound_to_vpn={self.is_bound_to_vpn}, "
                f"is_provider_network={self.is_provider_network}, "
                f"is_shared_network={self.is_shared_network}, "
                f"is_external_network={self.is_external_network}, "
                f"orchestration_status={self.orchestration_status})")

    @property
    def url(self) -> str:
        """Network instance url.

        Returns:
            str: NetworkInstance url

        """
        return f"{self.base_url}{self.api_version}/network/l3-networks/l3-network/{self.network_id}"

    @classmethod
    def create_from_api_response(cls, api_response: dict,
                                 service_instance: "ServiceInstance") -> "NetworkInstance":
        """Create network instance object using HTTP API response dictionary.

        Args:
            api_response (dict): A&AI API response dictionary
            service_instance (ServiceInstance): Service instance with which network is related

        Returns:
            VnfInstance: VnfInstance object

        """
        return cls(service_instance=service_instance,
                   network_id=api_response["network-id"],
                   is_bound_to_vpn=api_response["is-bound-to-vpn"],
                   is_provider_network=api_response["is-provider-network"],
                   is_shared_network=api_response["is-shared-network"],
                   is_external_network=api_response["is-external-network"],
                   network_name=api_response.get("network-name"),
                   network_type=api_response.get("network-type"),
                   network_role=api_response.get("network-role"),
                   network_technology=api_response.get("network-technology"),
                   neutron_network_id=api_response.get("neutron-network-id"),
                   service_id=api_response.get("service-id"),
                   network_role_instance=api_response.get("network-role-instance"),
                   resource_version=api_response.get("resource-version"),
                   orchestration_status=api_response.get("orchestration-status"),
                   heat_stack_id=api_response.get("heat-stack-id"),
                   mso_catalog_key=api_response.get("mso-catalog-key"),
                   model_invariant_id=api_response.get("model-invariant-id"),
                   contrail_network_fqdn=api_response.get("contrail-network-fqdn"),
                   model_version_id=api_response.get("model-version-id"),
                   model_customization_id=api_response.get("model-customization-id"),
                   widget_model_id=api_response.get("widget-model-id"),
                   persona_model_version=api_response.get("persona-model-version"),
                   physical_network_name=api_response.get("physical-network-name"),
                   selflink=api_response.get("selflink"),
                   widget_model_version=api_response.get("widget-model-version"),
                   operational_status=api_response.get("operational-status"),
                   is_trunked=api_response.get("is-trunked"))

    def delete(self) -> "NetworkDeletionRequest":
        """Create network deletion request.

        Send request to delete network instance

        Returns:
            NetworkDeletionRequest: Deletion request

        """
        self._logger.debug("Delete %s network", self.network_id)
        return NetworkDeletionRequest.send_request(self)
