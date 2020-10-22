#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SO Element module."""
import json
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Dict

from onapsdk.configuration import settings
from onapsdk.sdc.service import Service
from onapsdk.sdc.vf import Vf
from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_so_creator
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.mixins import WaitForFinishMixin
from onapsdk.utils.tosca_file_handler import get_modules_list_from_tosca_file


@dataclass
class SoElement(OnapService):
    """Mother Class of all SO elements."""

    name: str = None
    _server: str = "SO"
    base_url = settings.SO_URL
    api_version = settings.SO_API_VERSION
    _status: str = None

    @property
    def headers(self):
        """Create headers for SO request.

        It is used as a property because x-transactionid header should be unique for each request.
        """
        return headers_so_creator(OnapService.headers)

    @classmethod
    def get_subscription_service_type(cls, vf_name):
        """Retrieve the model info of the VFs."""
        vf_object = Vf(name=vf_name)
        return vf_object.name

    @classmethod
    def get_service_model_info(cls, service_name):
        """Retrieve Service Model info."""
        service = Service(name=service_name)
        template_service = jinja_env().get_template("service_instance_model_info.json.j2")
        # Get service instance model
        parsed = json.loads(
            template_service.render(
                model_invariant_id=service.unique_uuid,
                model_name_version_id=service.identifier,
                model_name=service.name,
                model_version=service.version,
            )
        )
        return json.dumps(parsed, indent=4)

    @classmethod
    def get_vnf_model_info(cls, vf_name):
        """Retrieve the model info of the VFs."""
        vf_object = Vf(name=vf_name)
        template_service = jinja_env().get_template("vnf_model_info.json.j2")
        parsed = json.loads(
            template_service.render(
                vnf_model_invariant_uuid=vf_object.unique_uuid,
                vnf_model_customization_id="????",
                vnf_model_version_id=vf_object.identifier,
                vnf_model_name=vf_object.name,
                vnf_model_version=vf_object.version,
                vnf_model_instance_name=(vf_object.name + " 0"),
            )
        )
        # we need also a vnf instance Name
        # Usually it is found like that
        # name: toto
        # instance name: toto 0
        # it can be retrieved from the tosca
        return json.dumps(parsed, indent=4)

    @classmethod
    def get_vf_model_info(cls, vf_model: str) -> str:
        """Retrieve the VF model info From Tosca?."""
        modules: Dict = get_modules_list_from_tosca_file(vf_model)
        template_service = jinja_env().get_template("vf_model_info.json.j2")
        parsed = json.loads(template_service.render(modules=modules))
        return json.dumps(parsed, indent=4)

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of SO.

        Returns:
            str: the base url

        """
        return "{}/onap/so/infra/serviceInstantiation/{}/serviceInstances".format(
            cls.base_url, cls.api_version
        )


class OrchestrationRequest(SoElement, WaitForFinishMixin, ABC):
    """Base SO orchestration request class."""

    WAIT_FOR_SLEEP_TIME = 10

    def __init__(self,
                 request_id: str) -> None:
        """Instantiate object initialization.

        Initializator used by classes inherited from this abstract class.

        Args:
            request_id (str): request ID
        """
        super().__init__()
        self.request_id: str = request_id

    class StatusEnum(Enum):
        """Status enum.

        Store possible statuses for instantiation:
            - IN_PROGRESS,
            - FAILED,
            - COMPLETE.
        If instantiation has status which is not covered by these values
            UNKNOWN value is used.

        """

        IN_PROGRESS = "IN_PROGRESS"
        FAILED = "FAILED"
        COMPLETED = "COMPLETE"
        UNKNOWN = "UNKNOWN"

    @property
    def status(self) -> "StatusEnum":
        """Object instantiation status.

        It's populated by call SO orchestation request endpoint.

        Returns:
            StatusEnum: Instantiation status.

        """
        response: dict = self.send_message_json(
            "GET",
            f"Check {self.request_id} orchestration request status",
            (f"{self.base_url}/onap/so/infra/"
             f"orchestrationRequests/{self.api_version}/{self.request_id}"),
            headers=headers_so_creator(OnapService.headers)
        )
        try:
            return self.StatusEnum(response["request"]["requestStatus"]["requestState"])
        except (KeyError, ValueError):
            self._logger.exception("Invalid status")
            return self.StatusEnum.UNKNOWN

    @property
    def finished(self) -> bool:
        """Store an information if instantion is finished or not.

        Instantiation is finished if it's status is COMPLETED or FAILED.

        Returns:
            bool: True if instantiation is finished, False otherwise.

        """
        return self.status in [self.StatusEnum.COMPLETED, self.StatusEnum.FAILED]

    @property
    def completed(self) -> bool:
        """Store an information if instantion is completed or not.

        Instantiation is completed if it's status is COMPLETED.

        Returns:
            bool: True if instantiation is completed, False otherwise.

        """
        return self.finished and self.status == self.StatusEnum.COMPLETED

    @property
    def failed(self) -> bool:
        """Store an information if instantion is failed or not.

        Instantiation is failed if it's status is FAILED.

        Returns:
            bool: True if instantiation is failed, False otherwise.

        """
        return self.finished and self.status == self.StatusEnum.FAILED
