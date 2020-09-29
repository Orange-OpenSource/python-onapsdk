"""VF module instance."""

from onapsdk.so.deletion import VfModuleDeletionRequest

from .instance import Instance


class VfModuleInstance(Instance):  # pylint: disable=too-many-instance-attributes
    """Vf module instance class."""

    def __init__(self,  # pylint: disable=too-many-arguments, too-many-locals
                 vnf_instance: "VnfInstance",
                 vf_module_id: str,
                 is_base_vf_module: bool,
                 automated_assignment: bool,
                 vf_module_name: str = None,
                 heat_stack_id: str = None,
                 resource_version: str = None,
                 model_invariant_id: str = None,
                 orchestration_status: str = None,
                 persona_model_version: str = None,
                 model_version_id: str = None,
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
        super().__init__(resource_version=resource_version, model_version_id=model_version_id,
                         model_invariant_id=model_invariant_id,
                         persona_model_version=persona_model_version,
                         widget_model_id=widget_model_id,
                         widget_model_version=widget_model_version)
        self.vnf_instance: "VnfInstance" = vnf_instance
        self.vf_module_id: str = vf_module_id
        self.is_base_vf_module: bool = is_base_vf_module
        self.automated_assignment: bool = automated_assignment
        self.vf_module_name: str = vf_module_name
        self.heat_stack_id: str = heat_stack_id
        self.orchestration_status: str = orchestration_status
        self.model_customization_id: str = model_customization_id
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
