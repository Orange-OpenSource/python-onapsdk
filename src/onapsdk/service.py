#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service module."""
from collections import namedtuple
from dataclasses import dataclass
from difflib import SequenceMatcher
from io import BytesIO, TextIOWrapper
from os import makedirs
import time
import re
from typing import Dict, Iterable, List, Callable, Union, Any
from zipfile import ZipFile, BadZipFile
from requests import Response

import oyaml as yaml

import onapsdk.constants as const
from onapsdk.sdc_resource import SdcResource
from onapsdk.utils.configuration import (components_needing_distribution,
                                         tosca_path)
from onapsdk.utils.headers_creator import headers_sdc_creator
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

    Base class for Vnf and Network classes.
    """

    name: str
    node_template_type: str
    metadata: dict
    properties: dict
    capabilities: dict


@dataclass
class Vnf(NodeTemplate):
    """Vnf dataclass."""

    vf_module: VfModule = None

    def associate_vf_module(self, vf_modules: Iterable[VfModule]) -> None:
        """Iterate through Service vf modules and found the valid one.

        This is experimental! To be honest we are not sure if it works
            correctly, it should be clarified with ONAP community.

        Args:
            vf_modules (Iterable[VfModule]): Service vf modules

        """
        AssociateMatch = namedtuple("AssociateMatch", ["ratio", "object"])
        best_match: AssociateMatch = AssociateMatch(0.0, None)
        for vf_module in vf_modules:  # type: VfModule
            current_ratio: float = SequenceMatcher(None,
                                                   self.name.lower(),
                                                   vf_module.name.lower()).ratio()
            if current_ratio > best_match.ratio:
                best_match = AssociateMatch(current_ratio, vf_module)
        self.vf_module = best_match.object


class Network(NodeTemplate):  # pylint: disable=too-few-public-methods
    """Network dataclass."""


class Service(SdcResource):  # pylint: disable=too-many-instance-attributes
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
    headers = headers_sdc_creator(SdcResource.headers)

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None,
                 resources: List[SdcResource] = None):
        """
        Initialize service object.

        Args:
            name (str, optional): the name of the service
            sdc_values (Dict[str, str], optional): dictionary of values
                returned by SDC
            resources (List[SdcResource], optional): list of SDC resources

        """
        super().__init__(sdc_values=sdc_values)
        self.name: str = name or "ONAP-test-Service"
        self.distribution_status = None
        if sdc_values:
            self.distribution_status = sdc_values['distributionStatus']
        self.resources = resources or []
        self._distribution_id: str = None
        self._distributed: bool = False
        self._resource_type: str = "services"
        self._tosca_model: bytes = None
        self._tosca_template: str = None
        self._vnfs: list = None
        self._networks: list = None
        self._vf_modules: list = None
        self._time_wait: int = 10

    def onboard(self) -> None:
        """Onboard the Service in SDC."""
        # first Lines are equivalent for all onboard functions but it's more
        # readable
        if not self.status:
            self.create()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.DRAFT:
            if not self.resources:
                raise ValueError("No resources were given")
            for resource in self.resources:
                self.add_resource(resource)
            self.checkin()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.CHECKED_IN:
            self.certify()
            time.sleep(self._time_wait)
            self.onboard()
            time.sleep(self._time_wait)
        elif self.status == const.CERTIFIED:
            self.distribute()
        elif self.status == const.DISTRIBUTED:
            self._logger.info("Service %s onboarded", self.name)
            return
        self._logger.error("Service has invalid status")

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

        Raises:
            AttributeError: Tosca model can't be downloaded using HTTP API

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

        Raises:
            AttributeError: Tosca model can't be downloaded using HTTP API

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
                headers=headers,
                exception=AttributeError).content
        return self._tosca_model

    @property
    def vnfs(self) -> List[Vnf]:
        """Service Vnfs.

        Load VNFs from service's tosca file

        Raises:
            AttributeError: Service has no TOSCA template

        Returns:
            List[Vnf]: Vnf objects list

        """
        if not self.tosca_template:
            raise AttributeError("Service has no TOSCA template")
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
                    vnf.associate_vf_module(self.vf_modules)
                    self._vnfs.append(vnf)
        return self._vnfs

    @property
    def networks(self) -> List[Network]:
        """Service networks.

        Load networks from service's tosca file

        Raises:
            AttributeError: Service has no TOSCA template

        Returns:
            List[Network]: Network objects list

        """
        if not self.tosca_template:
            raise AttributeError("Service has no TOSCA template")
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
                        capabilities=values["capabilities"]
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

    def create(self) -> None:
        """Create the Service in SDC if not already existing."""
        self._create("service_create.json.j2", name=self.name)

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
                                   resource_type=type(resource).__name__)
            result = self.send_message("POST",
                                       "Add {} to service".format(
                                           type(resource).__name__),
                                       url,
                                       data=data)
            if result:
                self._logger.info("Resource %s %s has been added on serice %s",
                                  type(resource).__name__, resource.name,
                                  self.name)
                return result
            self._logger.error(("an error occured during adding resource %s %s"
                                " on service %s in SDC"),
                               type(resource).__name__, resource.name,
                               self.name)
            return None
        self._logger.error("Service is not in Draft mode")
        return None

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
        result = self.send_message_json("GET",
                                        "Check distribution for {}".format(
                                            self.name),
                                        url,
                                        headers=headers)
        status = {}
        for component in components_needing_distribution():
            status[component] = False

        if result:
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
        if (result and 'distributionStatusOfServiceList' in result
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
            result = self._action_to_sdc(desired_action,
                                         action_type=action_type,
                                         **kwargs)
            if result:
                self.load()
        elif not self.created():
            self._logger.warning("Service %s in SDC is not created", self.name)
        elif self.status != desired_status:
            self._logger.warning(("Service %s in SDC is in status %s and it "
                                  "should be in  status %s"), self.name,
                                 self.status, desired_status)

    @staticmethod
    def _unzip_csar_file(zip_file: Union[str, BytesIO],
                         function: Callable[[str,
                                             TextIOWrapper], None]) -> None:
        """
        Unzip Csar File and perform an action on the file.

        Raises:
            AttributeError: CSAR file has no service template

        """
        with ZipFile(zip_file) as myzip:
            service_template = None
            for name in myzip.namelist():
                if (name[-13:] == "-template.yml"
                        and name[:20] == "Definitions/service-"):
                    service_template = name

            if not service_template:
                raise AttributeError("CSAR file has no service template")

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
