#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service module."""
from os import makedirs
import logging
from typing import Dict, List
from zipfile import ZipFile, BadZipFile

import onapsdk.constants as const
from onapsdk.sdc_resource import SdcResource
from onapsdk.utils.configuration import (components_needing_distribution,
                                         tosca_path)
from onapsdk.utils.headers_creator import (headers_sdc_creator,
                                           headers_sdc_governor,
                                           headers_sdc_operator,
                                           headers_sdc_tester)
from onapsdk.utils.jinja import jinja_env


class Service(SdcResource):
    """
    ONAP Service Object used for SDC operations.

    Attributes:
        name (str): the name of the vendor. Defaults to "Generic-Vendor".
        identifier (str): the unique ID of the vendor from SDC.
        status (str): the status of the vendor from SDC.
        version (str): the version ID of the vendor from SDC.
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
    _logger: logging.Logger = logging.getLogger(__name__)
    headers = headers_sdc_creator(SdcResource.headers)

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None,
                 resources: List[SdcResource] = None):
        """
        Initialize vendor object.

        Args:
            name (optional): the name of the vendor

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

    def onboard(self) -> None:
        """Onboard the Service in SDC."""
        # first Lines are equivalent for all onboard functions but it's more readable
        if not self.status: # # pylint: disable=R0801
            self.create()
            self.onboard()
        elif self.status == const.DRAFT:
            if not self.resources:
                raise ValueError("No resources were given")
            for resource in self.resources:
                self.add_resource(resource)
            self.checkin()
            self.onboard()
        elif self.status == const.CHECKED_IN:
            self.submit()
            self.onboard()
        elif self.status == const.SUBMITTED:
            self.start_certification()
            self.onboard()
        elif self.status == const.UNDER_CERTIFICATION:
            self.certify()
            self.onboard()
        elif self.status == const.CERTIFIED:
            self.approve()
            self.onboard()
        elif self.status == const.APPROVED:
            self.distribute()

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
        headers = headers_sdc_tester(SdcResource.headers)
        self._verify_lcm_to_sdc(const.SUBMITTED,
                                const.START_CERTIFICATION,
                                headers=headers)

    def certify(self) -> None:
        """Certify Service in SDC."""
        headers = headers_sdc_tester(SdcResource.headers)
        self._verify_lcm_to_sdc(const.UNDER_CERTIFICATION,
                                const.CERTIFY,
                                headers=headers)

    def approve(self) -> None:
        """Approve Service in SDC."""
        headers = headers_sdc_governor(SdcResource.headers)
        self._verify_approve_to_sdc(const.CERTIFIED,
                                    const.APPROVE,
                                    headers=headers)

    def distribute(self) -> None:
        """Apptove Service in SDC."""
        headers = headers_sdc_operator(SdcResource.headers)
        self._verify_distribute_to_sdc(const.APPROVED,
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
            csar_filename = "service-{}-csar.csar".format(self.name)
            makedirs(tosca_path(), exist_ok=True)
            with open((tosca_path() + csar_filename), 'wb') as csar_file:
                for chunk in result.iter_content(chunk_size=128):
                    csar_file.write(chunk)
            try:
                with ZipFile(tosca_path() + csar_filename) as myzip:
                    for name in myzip.namelist():
                        if (name[-13:] == "-template.yml"
                                and name[:20] == "Definitions/service-"):
                            service_template = name
                    with myzip.open(service_template) as file1:
                        with open(tosca_path() + service_template[12:],
                                  'wb') as file2:
                            file2.write(file1.read())
            except BadZipFile as exc:
                self._logger.exception(exc)

    def _check_distributed(self) -> bool:
        """Check if service is distributed and update status accordingly."""
        url = "{}/services/distribution/{}".format(self._base_create_url(),
                                                   self.distribution_id)
        headers = headers_sdc_operator(SdcResource.headers)
        result = self.send_message_json("GET",
                                        "Check distribution for {}".format(
                                            self.name),
                                        url,
                                        headers=headers)
        status = {}
        for component in components_needing_distribution():
            status[component] = False
        if result:
            distrib_list = result['distributionStatusList']
            self._logger.debug("[SDC][Get Distribution] distrib_list = %s",
                               distrib_list)
            for elt in distrib_list:
                for key in status:
                    if ((key in elt['omfComponentID'])
                            and (const.DOWNLOAD_OK in elt['status'])):
                        status[key] = True
                        self._logger.info(("[SDC][Get Distribution] Service "
                                           "distributed in %s"), key)
        for state in status.values():
            if not state:
                self._distributed = False
                return
        self._distributed = True

    def load_metadata(self) -> None:
        """Load Metada of Service and retrieve informations."""
        url = "{}/services/{}/distribution".format(self._base_create_url(),
                                                   self.identifier)
        headers = headers_sdc_operator(SdcResource.headers)
        result = self.send_message_json("GET",
                                        "Get Metadata for {}".format(
                                            self.name),
                                        url,
                                        headers=headers)
        if (result and 'distributionStatusOfServiceList' in result
                and len(result['distributionStatusOfServiceList']) > 0):
            dist_status = result['distributionStatusOfServiceList'][-1]
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

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.SERVICE_PATH
