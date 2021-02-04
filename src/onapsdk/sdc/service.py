#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service module."""
import base64
import pathlib as Path
import re
import string
import time
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO, TextIOWrapper
from os import makedirs
from typing import Dict, List, Callable, Union, Any, BinaryIO
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
class VfModule:
    """VfModule dataclass."""

    name: str
    group_type: str
    metadata: dict
    properties: dict


@dataclass
class NodeTemplate:
    """Node template dataclass.

    Base class for Vnf, Pnf and Network classes.
    """

    name: str
    node_template_type: str
    metadata: dict
    properties: dict
    capabilities: dict



@dataclass
class Vnf(NodeTemplate):
    """Vnf dataclass."""

    vf_modules: List[VfModule] = field(default_factory=list)

    @property
    def tosca_groups_parsed_name(self) -> str:
        """Property used to associate vf modules.

        It's created using the vnf name by with all
            characters before first `_` lowercase, then
            from all letters and numbers after first `_` are concatenated.

        Returns:
            str: String used to associate vf modules from tosca template

        """
        prefix, suffix = self.name.split("_", 1)
        return "_".join([prefix.lower(),
                         "".join(filter(lambda x: x in [*string.ascii_letters,
                                                        *string.digits], suffix)).lower()])


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
                 instantiation_type: ServiceInstantiationType = \
                     ServiceInstantiationType.A_LA_CARTE,
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
        self.instantiation_type: ServiceInstantiationType = instantiation_type
        self._distribution_id: str = None
        self._distributed: bool = False
        self._resource_type: str = "services"
        self._tosca_model: bytes = None
        self._tosca_template: str = None
        self._vnfs: list = None
        self._pnfs: list = None
        self._networks: list = None
        self._vf_modules: list = None

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

    @property
    def vnfs(self) -> List[Vnf]:
        """Service Vnfs.

        Load VNFs from service's tosca file

        Raises:
            ParameterError: Service has no TOSCA template

        Returns:
            List[Vnf]: Vnf objects list

        """
        if not self.tosca_template:
            raise ParameterError("Service has no TOSCA template.")
        if self._vnfs is None:
            self._vnfs = []
            for node_template_name, values in \
                self.tosca_template.get("topology_template", {}).get(
                        "node_templates", {}).items():
                if re.match("org.openecomp.resource.vf.*", values["type"]):
                    vnf: Vnf = Vnf(
                        name=node_template_name,
                        node_template_type=values["type"],
                        metadata=values["metadata"],
                        properties=values["properties"],
                        capabilities=values.get("capabilities", {})
                    )
                    # vnf.associate_vf_module(self.vf_modules)
                    self._vnfs.append(vnf)
            self.associate_vf_modules()
        return self._vnfs

    @property
    def pnfs(self) -> List[Pnf]:
        """Service Pnfs.

        Load PNFs from service's tosca file

        Raises:
            ParameterError: Service has no TOSCA template

        Returns:
            List[Pnf]: Pnf objects list

        """
        if not self.tosca_template:
            raise ParameterError("Service has no TOSCA template")
        if self._pnfs is None:
            self._pnfs = []
            for node_template_name, values in \
                self.tosca_template.get("topology_template", {}).get(
                        "node_templates", {}).items():
                if re.match("org.openecomp.resource.pnf.*", values["type"]):
                    pnf: Pnf = Pnf(
                        name=node_template_name,
                        node_template_type=values["type"],
                        metadata=values["metadata"],
                        properties=values["properties"],
                        capabilities=values.get("capabilities", {})
                    )
                    self._pnfs.append(pnf)
        return self._pnfs

    @property
    def networks(self) -> List[Network]:
        """Service networks.

        Load networks from service's tosca file

        Raises:
            ParameterError: Service has no TOSCA template

        Returns:
            List[Network]: Network objects list

        """
        if not self.tosca_template:
            raise ParameterError("Service has no TOSCA template")
        if self._networks is None:
            self._networks = []
            for node_template_name, values in \
                self.tosca_template.get("topology_template", {}).get(
                        "node_templates", {}).items():
                if re.match("org.openecomp.resource.vl.*", values["type"]):
                    self._networks.append(Network(
                        name=node_template_name,
                        node_template_type=values["type"],
                        metadata=values["metadata"],
                        properties=values["properties"],
                        capabilities=values.get("capabilities", {})
                    ))
        return self._networks

    @property
    def vf_modules(self) -> List[VfModule]:
        """Service VF modules.

        Load VF modules from service's tosca file

        Returns:
            List[VfModule]: VfModule objects list

        """
        if self._vf_modules is None:
            self._vf_modules = []
            groups: dict = self.tosca_template.get(
                "topology_template", {}).get("groups", {})
            for group_name, values in groups.items():
                self._vf_modules.append(VfModule(
                    name=group_name,
                    group_type=values["type"],
                    metadata=values["metadata"],
                    properties=values["properties"]
                ))
        return self._vf_modules


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

    def create(self) -> None:
        """Create the Service in SDC if not already existing."""
        self._create("service_create.json.j2",
                     name=self.name,
                     instantiation_type=self.instantiation_type.value,
                     category=self.category)

    def add_resource(self, resource: SdcResource) -> None:
        """
        Add a Resource to the service.

        Args:
            resource (SdcResource): the resource to add

        """
        if self.status == const.DRAFT:
            url = "{}/{}/{}/resourceInstance".format(self._base_create_url(),
                                                     self._sdc_path(),
                                                     self.unique_identifier)

            template = jinja_env().get_template(
                "add_resource_to_service.json.j2")
            data = template.render(resource=resource,
                                   resource_type=resource.origin_type)
            result = self.send_message("POST",
                                       "Add {} to service".format(
                                           resource.origin_type),
                                       url,
                                       data=data)
            if result:
                self._logger.info("Resource %s %s has been added on serice %s",
                                  resource.origin_type, resource.name,
                                  self.name)
                return result
            self._logger.error(("an error occured during adding resource %s %s"
                                " on service %s in SDC"),
                               resource.origin_type, resource.name,
                               self.name)
            return None
        self._logger.error("Service is not in Draft mode")
        return None

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
            msg = f"No distributions found for {self.name} of {self.__class__}."
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

    def associate_vf_modules(self) -> None:
        """Associate vf modules to vnfs.

        This is experimental! To be honest we are not sure if it works
            correctly, it should be clarified with ONAP community.

        Sometimes vnf has one vf module, but it can have assosicated
            more than one. There can be also more than one vnf in
            TOSCA template and it't difficult to determine which
            vnf should be associated with which vf module. Usually
            their name are similar, but not always.

        """
        if len(self.vnfs) == 0:
            return
        if len(self.vnfs) == 1:
            self.vnfs[0].vf_modules = self.vf_modules[:]
        else:
            for vnf in self.vnfs:
                vnf.vf_modules = list(filter(\
                    lambda vf_module: vf_module.name.startswith(
                        vnf.tosca_groups_parsed_name),  # pylint: disable=cell-var-from-loop
                    self.vf_modules))

    def get_category_for_new_resource(self) -> ServiceCategory:
        """Get category for service not created in SDC yet.

        If no category values are provided default category is going to be used.

        Returns:
            ServiceCategory: Category of the new service

        """
        if not self._category_name:
            return ServiceCategory.get(name="Network Service")
        return ServiceCategory.get(name=self._category_name)
