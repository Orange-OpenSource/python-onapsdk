#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service module."""
import base64
import pathlib as Path
import time
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO, TextIOWrapper
from os import makedirs
from typing import Dict, List, Callable, Iterator, Optional, Type, Union, Any, BinaryIO
from zipfile import ZipFile, BadZipFile

import oyaml as yaml
from requests import Response

import onapsdk.constants as const
from onapsdk.exceptions import (ParameterError, RequestError, ResourceNotFound,
                                StatusError, ValidationError)
from onapsdk.sdc.category_management import ServiceCategory
from onapsdk.sdc.properties import NestedInput, Property
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.utils.configuration import (components_needing_distribution,
                                         tosca_path)
from onapsdk.utils.headers_creator import headers_sdc_creator, headers_sdc_artifact_upload
from onapsdk.utils.jinja import jinja_env


@dataclass
class VfModule:  # pylint: disable=too-many-instance-attributes
    """VfModule dataclass."""

    name: str
    group_type: str
    model_name: str
    model_version_id: str
    model_invariant_uuid: str
    model_version: str
    model_customization_id: str
    properties: Iterator[Property]


@dataclass
class NodeTemplate:  # pylint: disable=too-many-instance-attributes
    """Node template dataclass.

    Base class for Vnf, Pnf and Network classes.
    """

    name: str
    node_template_type: str
    model_name: str
    model_version_id: str
    model_invariant_id: str
    model_version: str
    model_customization_id: str
    model_instance_name: str
    component: "Component"

    @property
    def properties(self) -> Iterator["Property"]:
        """Node template properties.

        Returns:
            Iterator[Property]: Node template properties iterator

        """
        return self.component.properties


@dataclass
class Vnf(NodeTemplate):
    """Vnf dataclass."""

    vf_modules: List[VfModule] = field(default_factory=list)


@dataclass
class Pnf(NodeTemplate):
    """Pnf dataclass."""


class Network(NodeTemplate):  # pylint: disable=too-few-public-methods
    """Network dataclass."""


class ServiceInstantiationType(Enum):
    """Service instantiation type enum class.

    Service can be instantiated using `A-la-carte` or `Macro` flow.
    It has to be determined during design time. That class stores these
    two values to set during initialization.

    """

    A_LA_CARTE = "A-la-carte"
    MACRO = "Macro"


class Service(SdcResource):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    ONAP Service Object used for SDC operations.

    Attributes:
        name (str): the name of the service. Defaults to "ONAP-test-Service".
        identifier (str): the unique ID of the service from SDC.
        status (str): the status of the service from SDC.
        version (str): the version ID of the service from SDC.
        uuid (str): the UUID of the Service (which is different from
                    identifier, don't ask why...)
        distribution_status (str):  the status of distribution in the different
                                    ONAP parts.
        distribution_id (str): the ID of the distribution when service is
                               distributed.
        distributed (bool): True if the service is distributed
        unique_identifier (str): Yet Another ID, just to puzzle us...

    """

    SERVICE_PATH = "services"

    def __init__(self, name: str = None, version: str = None, sdc_values: Dict[str, str] = None,  # pylint: disable=too-many-arguments
                 resources: List[SdcResource] = None, properties: List[Property] = None,
                 inputs: List[Union[Property, NestedInput]] = None,
                 instantiation_type: Optional[ServiceInstantiationType] = \
                     None,
                 category: str = None):
        """
        Initialize service object.

        Args:
            name (str, optional): the name of the service
            version (str, optional): the version of the service
            sdc_values (Dict[str, str], optional): dictionary of values
                returned by SDC
            resources (List[SdcResource], optional): list of SDC resources
            properties (List[Property], optional): list of properties to add to service.
                None by default.
            inputs (List[Union[Property, NestedInput]], optional): list of inputs
                to declare for service. It can be both Property or NestedInput object.
                None by default.
            instantiation_type (ServiceInstantiationType, optional): service instantiation
                type. ServiceInstantiationType.A_LA_CARTE by default
            category (str, optional): service category name

        """
        super().__init__(sdc_values=sdc_values, version=version, properties=properties,
                         inputs=inputs, category=category)
        self.name: str = name or "ONAP-test-Service"
        self.distribution_status = None
        self.category_name: str = category
        if sdc_values:
            self.distribution_status = sdc_values['distributionStatus']
            self.category_name = sdc_values["category"]
        self.resources = resources or []
        self._instantiation_type: Optional[ServiceInstantiationType] = instantiation_type
        self._distribution_id: str = None
        self._distributed: bool = False
        self._resource_type: str = "services"
        self._tosca_model: bytes = None
        self._tosca_template: str = None
        self._vnfs: list = None
        self._pnfs: list = None
        self._networks: list = None
        self._vf_modules: list = None

    @classmethod
    def get_by_unique_uuid(cls, unique_uuid: str) -> "Service":
        """Get the service model using unique uuid.

        Returns:
            Service: object with provided unique_uuid

        Raises:
            ResourceNotFound: No service with given unique_uuid exists

        """
        services: List["Service"] = cls.get_all()
        for service in services:
            if service.unique_uuid == unique_uuid:
                return service
        raise ResourceNotFound("Service with given unique uuid doesn't exist")

    def onboard(self) -> None:
        """Onboard the Service in SDC.

        Raises:
            StatusError: service has an invalid status
            ParameterError: no resources, no properties for service
                in DRAFT status

        """
        # first Lines are equivalent for all onboard functions but it's more
        # readable
        if not self.status:
            # equivalent step as in onboard-function in sdc_resource
            self.create()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.DRAFT:
            if not any([self.resources, self._properties_to_add]):
                raise ParameterError("No resources nor properties were given")
            self.declare_resources_and_properties()
            self.checkin()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.CHECKED_IN:
            self.certify()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.CERTIFIED:
            self.distribute()
            self.onboard()
        elif self.status == const.DISTRIBUTED:
            self._logger.info("Service %s onboarded", self.name)
        else:
            self._logger.error("Service has invalid status: %s", self.status)
            raise StatusError(self.status)

    @property
    def distribution_id(self) -> str:
        """Return and lazy load the distribution_id."""
        if not self._distribution_id:
            self.load_metadata()
        return self._distribution_id

    @distribution_id.setter
    def distribution_id(self, value: str) -> None:
        """Set value for distribution_id."""
        self._distribution_id = value

    @property
    def distributed(self) -> bool:
        """Return and lazy load the distributed state."""
        if not self._distributed:
            self._check_distributed()
        return self._distributed

    @property
    def tosca_template(self) -> str:
        """Service tosca template file.

        Get tosca template from service tosca model bytes.

        Returns:
            str: Tosca template file

        """
        if not self._tosca_template and self.tosca_model:
            self._unzip_csar_file(BytesIO(self.tosca_model),
                                  self._load_tosca_template)
        return self._tosca_template

    @property
    def tosca_model(self) -> bytes:
        """Service's tosca model file.

        Send request to get service TOSCA model,

        Returns:
            bytes: TOSCA model file bytes

        """
        if not self._tosca_model:
            url = "{}/services/{}/toscaModel".format(self._base_url(),
                                                     self.identifier)
            headers = self.headers.copy()
            headers["Accept"] = "application/octet-stream"
            self._tosca_model = self.send_message(
                "GET",
                "Download Tosca Model for {}".format(self.name),
                url,
                headers=headers).content
        return self._tosca_model

    def create_node_template(self,
                             node_template_type: Type[NodeTemplate],
                             component: "Component") -> NodeTemplate:
        """Create a node template type object.

        The base of the all node template types objects (Vnf, Pnf, Network) is the
        same. The difference is only for the Vnf which can have vf modules associated with.
        Vf modules could have "vf_module_label" property with"base_template_dummy_ignore"
        value. These vf modules should be ignored/

        Args:
            node_template_type (Type[NodeTemplate]): Node template class type
            component (Component): Component on which base node template object should be created

        Returns:
            NodeTemplate: Node template object created from component

        """
        node_template: NodeTemplate = node_template_type(
            name=component.name,
            node_template_type=component.tosca_component_name,
            model_name=component.component_name,
            model_version_id=component.sdc_resource.identifier,
            model_invariant_id=component.sdc_resource.unique_uuid,
            model_version=component.sdc_resource.version,
            model_customization_id=component.customization_uuid,
            model_instance_name=self.name,
            component=component
        )
        if node_template_type is Vnf:
            if component.group_instances:
                for vf_module in component.group_instances:
                    if not any([property_def["name"] == "vf_module_label"] and \
                            property_def["value"] == "base_template_dummy_ignore" for \
                                property_def in vf_module["properties"]):
                        node_template.vf_modules.append(VfModule(
                            name=vf_module["name"],
                            group_type=vf_module["type"],
                            model_name=vf_module["groupName"],
                            model_version_id=vf_module["groupUUID"],
                            model_invariant_uuid=vf_module["invariantUUID"],
                            model_version=vf_module["version"],
                            model_customization_id=vf_module["customizationUUID"],
                            properties=(
                                Property(
                                    name=property_def["name"],
                                    property_type=property_def["type"],
                                    description=property_def["description"],
                                    value=property_def["value"]
                                ) for property_def in vf_module["properties"] \
                                    if property_def["value"] and not (
                                        property_def["name"] == "vf_module_label" and \
                                            property_def["value"] == "base_template_dummy_ignore"
                                    )
                            )
                        ))
        return node_template

    def __has_component_type(self, origin_type: str) -> bool:
        """Check if any of Service's component type is provided origin type.

        In template generation is checked if Service has some types of components,
            based on that blocks are added to the request template. It's not
            the best option to get all components to check if at least one with
            given type exists for conditional statement.

        Args:
            origin_type (str): Type to check if any component exists.

        Returns:
            bool: True if service has at least one component with given origin type,
                False otherwise

        """
        return any((component.origin_type == origin_type for component in self.components))

    @property
    def has_vnfs(self) -> bool:
        """Check if service has at least one VF component."""
        return self.__has_component_type("VF")

    @property
    def has_pnfs(self) -> bool:
        """Check if service has at least one PNF component."""
        return self.__has_component_type("PNF")

    @property
    def has_vls(self) -> bool:
        """Check if service has at least one VL component."""
        return self.__has_component_type("VL")

    @property
    def vnfs(self) -> Iterator[Vnf]:
        """Service Vnfs.

        Load VNFs from components generator.
        It creates a generator of the vf modules as well, but without
            vf modules which has "vf_module_label" property value equal
            to "base_template_dummy_ignore".

        Returns:
            Iterator[Vnf]: Vnf objects iterator

        """
        for component in self.components:
            if component.origin_type == "VF":
                yield self.create_node_template(Vnf, component)

    @property
    def pnfs(self) -> Iterator[Pnf]:
        """Service Pnfs.

        Load PNFS from components generator.

        Returns:
            Iterator[Pnf]: Pnf objects generator

        """
        for component in self.components:
            if component.origin_type == "PNF":
                yield self.create_node_template(Pnf, component)

    @property
    def networks(self) -> Iterator[Network]:
        """Service networks.

        Load networks from service's components generator.

        Returns:
            Iterator[Network]: Network objects generator

        """
        for component in self.components:
            if component.origin_type == "VL":
                yield self.create_node_template(Network, component)

    @property
    def deployment_artifacts_url(self) -> str:
        """Deployment artifacts url.

        Returns:
            str: SdcResource Deployment artifacts url

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/filteredDataByParams?include=deploymentArtifacts")

    @property
    def add_deployment_artifacts_url(self) -> str:
        """Add deployment artifacts url.

        Returns:
            str: Url used to add deployment artifacts

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/artifacts")

    @property
    def properties_url(self) -> str:
        """Properties url.

        Returns:
            str: SdcResource properties url

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/filteredDataByParams?include=properties")

    @property
    def metadata_url(self) -> str:
        """Metadata url.

        Returns:
            str: Service metadata url

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/filteredDataByParams?include=metadata")

    @property
    def resource_inputs_url(self) -> str:
        """Service inputs url.

        Returns:
            str: Service inputs url

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}")

    @property
    def set_input_default_value_url(self) -> str:
        """Url to set input default value.

        Returns:
            str: SDC API url used to set input default value

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/update/inputs")

    @property
    def origin_type(self) -> str:
        """Service origin type.

        Value needed for composition. It's used for adding SDC resource
            as an another SDC resource component.
            For Service that value has to be set to "ServiceProxy".

        Returns:
            str: Service resource origin type

        """
        return "ServiceProxy"

    @property
    def instantiation_type(self) -> ServiceInstantiationType:
        """Service instantiation type.

        One of `ServiceInstantiationType` enum value.

        Returns:
            ServiceInstantiationType: Service instantiation type

        """
        if not self._instantiation_type:
            if not self.created():
                self._instantiation_type = ServiceInstantiationType.A_LA_CARTE
            else:
                response: str = self.send_message_json("GET",
                                                       f"Get service {self.name} metadata",
                                                       self.metadata_url)["metadata"]\
                                                                         ["instantiationType"]
                self._instantiation_type = ServiceInstantiationType(response)
        return self._instantiation_type

    def create(self) -> None:
        """Create the Service in SDC if not already existing."""
        self._create("service_create.json.j2",
                     name=self.name,
                     instantiation_type=self.instantiation_type.value,
                     category=self.category)

    def declare_resources_and_properties(self) -> None:
        """Delcare resources and properties.

        It declares also inputs.

        """
        for resource in self.resources:
            self.add_resource(resource)
        for property_to_add in self._properties_to_add:
            self.add_property(property_to_add)
        for input_to_add in self._inputs_to_add:
            self.declare_input(input_to_add)

    def checkin(self) -> None:
        """Checkin Service."""
        self._verify_lcm_to_sdc(const.DRAFT, const.CHECKIN)

    def submit(self) -> None:
        """Really submit the SDC Service."""
        self._verify_lcm_to_sdc(const.CHECKED_IN, const.SUBMIT_FOR_TESTING)

    def start_certification(self) -> None:
        """Start Certification on Service."""
        headers = headers_sdc_creator(SdcResource.headers)
        self._verify_lcm_to_sdc(const.CHECKED_IN,
                                const.START_CERTIFICATION,
                                headers=headers)

    def certify(self) -> None:
        """Certify Service in SDC."""
        headers = headers_sdc_creator(SdcResource.headers)
        self._verify_lcm_to_sdc(const.CHECKED_IN,
                                const.CERTIFY,
                                headers=headers)

    def approve(self) -> None:
        """Approve Service in SDC."""
        headers = headers_sdc_creator(SdcResource.headers)
        self._verify_approve_to_sdc(const.CERTIFIED,
                                    const.APPROVE,
                                    headers=headers)

    def distribute(self) -> None:
        """Apptove Service in SDC."""
        headers = headers_sdc_creator(SdcResource.headers)
        self._verify_distribute_to_sdc(const.CERTIFIED,
                                       const.DISTRIBUTE,
                                       headers=headers)

    def get_tosca(self) -> None:
        """Get Service tosca files and save it."""
        url = "{}/services/{}/toscaModel".format(self._base_url(),
                                                 self.identifier)
        headers = self.headers.copy()
        headers["Accept"] = "application/octet-stream"
        result = self.send_message("GET",
                                   "Download Tosca Model for {}".format(
                                       self.name),
                                   url,
                                   headers=headers)
        if result:
            self._create_tosca_file(result)

    def _create_tosca_file(self, result: Response) -> None:
        """Create Service Tosca files from HTTP response."""
        csar_filename = "service-{}-csar.csar".format(self.name)
        makedirs(tosca_path(), exist_ok=True)
        with open((tosca_path() + csar_filename), 'wb') as csar_file:
            for chunk in result.iter_content(chunk_size=128):
                csar_file.write(chunk)
        try:
            self._unzip_csar_file(tosca_path() + csar_filename,
                                  self._write_csar_file)
        except BadZipFile as exc:
            self._logger.exception(exc)

    def _check_distributed(self) -> bool:
        """Check if service is distributed and update status accordingly."""
        url = "{}/services/distribution/{}".format(self._base_create_url(),
                                                   self.distribution_id)
        headers = headers_sdc_creator(SdcResource.headers)

        status = {}
        for component in components_needing_distribution():
            status[component] = False

        try:
            result = self.send_message_json("GET",
                                            "Check distribution for {}".format(
                                                self.name),
                                            url,
                                            headers=headers)
        except ResourceNotFound:
            msg = f"No distributions found for {self.name} of {self.__class__.__name__}."
            self._logger.debug(msg)
        else:
            status = self._update_components_status(status, result)

        for state in status.values():
            if not state:
                self._distributed = False
                return
        self._distributed = True

    def _update_components_status(self, status: Dict[str, bool],
                                  result: Response) -> Dict[str, bool]:
        """Update components distribution status."""
        distrib_list = result['distributionStatusList']
        self._logger.debug("[SDC][Get Distribution] distrib_list = %s",
                           distrib_list)
        for elt in distrib_list:
            status = self._parse_components_status(status, elt)
        return status

    def _parse_components_status(self, status: Dict[str, bool],
                                 element: Dict[str, Any]) -> Dict[str, bool]:
        """Parse components distribution status."""
        for key in status:
            if ((key in element['omfComponentID'])
                    and (const.DOWNLOAD_OK in element['status'])):
                status[key] = True
                self._logger.info(("[SDC][Get Distribution] Service "
                                   "distributed in %s"), key)
        return status

    def load_metadata(self) -> None:
        """Load Metada of Service and retrieve informations."""
        url = "{}/services/{}/distribution".format(self._base_create_url(),
                                                   self.identifier)
        headers = headers_sdc_creator(SdcResource.headers)
        result = self.send_message_json("GET",
                                        "Get Metadata for {}".format(
                                            self.name),
                                        url,
                                        headers=headers)
        if ('distributionStatusOfServiceList' in result
                and len(result['distributionStatusOfServiceList']) > 0):
            # API changed and the latest distribution is not added to the end
            # of distributions list but inserted as the first one.
            dist_status = result['distributionStatusOfServiceList'][0]
            self._distribution_id = dist_status['distributionID']

    @classmethod
    def _get_all_url(cls) -> str:
        """
        Get URL for all elements in SDC.

        Returns:
            str: the url

        """
        return "{}/{}".format(cls._base_url(), cls._sdc_path())

    def _really_submit(self) -> None:
        """Really submit the SDC Service in order to enable it."""
        result = self._action_to_sdc(const.CERTIFY,
                                     action_type="lifecycleState")
        if result:
            self.load()

    def _specific_copy(self, obj: 'Service') -> None:
        """
        Copy specific properties from object.

        Args:
            obj (Service): the object to "copy"

        """
        super()._specific_copy(obj)
        self.category_name = obj.category_name

    def _verify_distribute_to_sdc(self, desired_status: str,
                                  desired_action: str, **kwargs) -> None:
        self._verify_action_to_sdc(desired_status, desired_action,
                                   "distribution", **kwargs)

    def _verify_approve_to_sdc(self, desired_status: str, desired_action: str,
                               **kwargs) -> None:
        self._verify_action_to_sdc(desired_status, desired_action,
                                   "distribution-state", **kwargs)

    def _verify_lcm_to_sdc(self, desired_status: str, desired_action: str,
                           **kwargs) -> None:
        self._verify_action_to_sdc(desired_status, desired_action,
                                   "lifecycleState", **kwargs)

    def _verify_action_to_sdc(self, desired_status: str, desired_action: str,
                              action_type: str, **kwargs) -> None:
        """
        Verify action to SDC.

        Verify that object is in right state before launching the action on
        SDC.

        Raises:
            StatusError: if current status is not the desired status.

        Args:
            desired_status (str): the status the object should be
            desired_action (str): the action we want to perform
            action_type (str): the type of action ('distribution-state' or
                               'lifecycleState')
            **kwargs: any specific stuff to give to requests

        """
        self._logger.info("attempting to %s Service %s in SDC", desired_action,
                          self.name)
        if self.status == desired_status and self.created():
            self._action_to_sdc(desired_action,
                                action_type=action_type,
                                **kwargs)
            self.load()
        elif not self.created():
            self._logger.warning("Service %s in SDC is not created", self.name)
        elif self.status != desired_status:
            msg = (f"Service {self.name} in SDC is in status {self.status} "
                   f"and it should be in status {desired_status}")
            raise StatusError(msg)

    @staticmethod
    def _unzip_csar_file(zip_file: Union[str, BytesIO],
                         function: Callable[[str,
                                             TextIOWrapper], None]) -> None:
        """
        Unzip Csar File and perform an action on the file.

        Raises:
            ValidationError: CSAR file has no service template

        """
        folder = "Definitions"
        prefix = "service-"
        suffix = "-template.yml"
        with ZipFile(zip_file) as myzip:
            service_template = None
            for name in myzip.namelist():
                if (name[-13:] == suffix
                        and name[:20] == f"{folder}/{prefix}"):
                    service_template = name

            if not service_template:
                msg = (f"CSAR file has no service template. "
                       f"Valid path: {folder}/{prefix}*{suffix}")
                raise ValidationError(msg)

            with myzip.open(service_template) as template_file:
                function(service_template, template_file)

    @staticmethod
    def _write_csar_file(service_template: str,
                         template_file: TextIOWrapper) -> None:
        """Write service temple into a file."""
        with open(tosca_path() + service_template[12:], 'wb') as file:
            file.write(template_file.read())

    # _service_template is not used but function generation is generic
    # pylint: disable-unused-argument
    def _load_tosca_template(self, _service_template: str,
                             template_file: TextIOWrapper) -> None:
        """Load Tosca template."""
        self._tosca_template = yaml.safe_load(template_file.read())

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.SERVICE_PATH

    def get_nf_unique_id(self, nf_name: str) -> str:
        """
        Get nf (network function) uniqueID.

        Get nf uniqueID from service nf in sdc.

        Args:
            nf_name (str): the nf from which we extract the unique ID

        Returns:
            the nf unique ID

        Raises:
            ResourceNotFound: Couldn't find NF by name.

        """
        url = f"{self._base_create_url()}/services/{self.unique_identifier}"
        request_return = self.send_message_json('GET',
                                                'Get nf unique ID',
                                                url)

        for instance in filter(lambda x: x["componentName"] == nf_name,
                               request_return["componentInstances"]):
            return instance["uniqueId"]

        raise ResourceNotFound(f"NF '{nf_name}'")


    def add_artifact_to_vf(self, vnf_name: str, artifact_type: str,
                           artifact_name: str, artifact: BinaryIO = None):
        """
        Add artifact to vf.

        Add artifact to vf using payload data.

        Raises:
            RequestError: file upload (POST request) for an artifact fails.

        Args:
            vnf_name (str): the vnf which we want to add the artifact
            artifact_type (str): all SDC artifact types are supported (DCAE_*, HEAT_*, ...)
            artifact_name (str): the artifact file name including its extension
            artifact (str): binary data to upload

        """
        missing_identifier = self.get_nf_unique_id(vnf_name)
        url = (f"{self._base_create_url()}/services/{self.unique_identifier}/"
               f"resourceInstance/{missing_identifier}/artifacts")
        template = jinja_env().get_template("add_artifact_to_vf.json.j2")
        data = template.render(artifact_name=artifact_name,
                               artifact_label=f"sdk{Path.PurePosixPath(artifact_name).stem}",
                               artifact_type=artifact_type,
                               b64_artifact=base64.b64encode(artifact).decode('utf-8'))
        headers = headers_sdc_artifact_upload(base_header=self.headers,
                                              data=data)
        try:
            self.send_message('POST',
                              'Add artifact to vf',
                              url,
                              headers=headers,
                              data=data)
        except RequestError as exc:
            self._logger.error(("an error occured during file upload for an Artifact"
                                "to VNF %s"), vnf_name)
            raise exc

    def get_component_properties_url(self, component: "Component") -> str:
        """Url to get component's properties.

        This method is here because component can have different url when
            it's a component of another SDC resource type, eg. for service and
            for VF components have different urls.
            Also for VL origin type components properties url is different than
            for the other types.

        Args:
            component (Component): Component object to prepare url for

        Returns:
            str: Component's properties url

        """
        if component.origin_type == "VL":
            return super().get_component_properties_url(component)
        return (f"{self.resource_inputs_url}/"
                f"componentInstances/{component.unique_id}/{component.actual_component_uid}/inputs")

    def get_component_properties_value_set_url(self, component: "Component") -> str:
        """Url to set component property value.

        This method is here because component can have different url when
            it's a component of another SDC resource type, eg. for service and
            for VF components have different urls.
            Also for VL origin type components properties url is different than
            for the other types.

        Args:
            component (Component): Component object to prepare url for

        Returns:
            str: Component's properties url

        """
        if component.origin_type == "VL":
            return super().get_component_properties_value_set_url(component)
        return (f"{self.resource_inputs_url}/"
                f"resourceInstance/{component.unique_id}/inputs")

    def get_category_for_new_resource(self) -> ServiceCategory:
        """Get category for service not created in SDC yet.

        If no category values are provided default category is going to be used.

        Returns:
            ServiceCategory: Category of the new service

        """
        if not self._category_name:
            return ServiceCategory.get(name="Network Service")
        return ServiceCategory.get(name=self._category_name)
