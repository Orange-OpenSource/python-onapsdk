"""Service instance module."""

from typing import Iterator

from onapsdk.so.deletion import ServiceDeletionRequest
from onapsdk.so.instantiation import VnfInstantiation

from .instance import Instance
from .vnf import VnfInstance


class ServiceInstance(Instance):  # pylint: disable=too-many-instance-attributes
    """Service instanve class."""

    def __init__(self,  # pylint: disable=too-many-arguments, too-many-locals
                 service_subscription: "ServiceSubscription",
                 instance_id: str,
                 instance_name: str = None,
                 service_type: str = None,
                 service_role: str = None,
                 environment_context: str = None,
                 workload_context: str = None,
                 created_at: str = None,
                 updated_at: str = None,
                 resource_version: str = None,
                 description: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 persona_model_version: str = None,
                 widget_model_id: str = None,
                 widget_model_version: str = None,
                 bandwith_total: str = None,
                 vhn_portal_url: str = None,
                 service_instance_location_id: str = None,
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
            widget_model_id (str, optional): The ASDC data dictionary widget model. This maps
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
        super().__init__(resource_version=resource_version, model_version_id=model_version_id,
                         persona_model_version=persona_model_version,
                         widget_model_id=widget_model_id,
                         widget_model_version=widget_model_version)
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
        self.bandwith_total: str = bandwith_total
        self.vhn_portal_url: str = vhn_portal_url
        self.service_instance_location_id: str = service_instance_location_id
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
                                           exception=ValueError),
                    self)

    def add_vnf(self,  # pylint: disable=too-many-arguments
                vnf: "Vnf",
                line_of_business: "LineOfBusiness",
                platform: "Platform",
                vnf_instance_name: str = None) -> "VnfInstantiation":
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

        Raises:
            AttributeError: Service orchestration status is not "Active"
            ValueError: Instantiation request error.

        Returns:
            VnfInstantiation: VnfInstantiation request object

        """
        if self.orchestration_status != "Active":
            raise AttributeError("Service has invalid orchestration status")
        return VnfInstantiation.instantiate_ala_carte(
            self,
            vnf,
            line_of_business,
            platform,
            vnf_instance_name
        )

    def delete(self) -> "ServiceDeletionRequest":
        """Create service deletion request.

        Send a request to delete service instance

        Returns:
            ServiceDeletionRequest: Deletion request object

        """
        self._logger.debug("Delete %s service instance", self.instance_id)
        return ServiceDeletionRequest.send_request(self)
