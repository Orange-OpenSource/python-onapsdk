#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
import logging
from typing import Any, Dict, List
from abc import ABC

import onapsdk.constants as const
from onapsdk.sdc import SDC
from onapsdk.utils.headers_creator import (headers_sdc_creator,
                                           headers_sdc_tester)


# For an unknown reason, pylint keeps seeing _unique_uuid and
# _unique_identifier as attributes along with unique_uuid and unique_identifier
class SdcResource(SDC, ABC):  # pylint: disable=too-many-instance-attributes
    """Mother Class of all SDC resources."""

    RESOURCE_PATH = 'resources'
    ACTION_TEMPLATE = 'sdc_resource_action.json.j2'
    ACTION_METHOD = 'POST'

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None):
        """Initialize the object."""
        super().__init__()
        self.name: str = name
        self._unique_uuid: str = None
        self._unique_identifier: str = None
        self._resource_type: str = "resources"
        if sdc_values:
            self._logger.debug("SDC values given, using them")
            self.identifier = sdc_values['uuid']
            self.version = sdc_values['version']
            self.unique_uuid = sdc_values['invariantUUID']
            distribitution_state = None
            if 'distributionStatus' in sdc_values:
                distribitution_state = sdc_values['distributionStatus']
            self.status = self._parse_sdc_status(sdc_values['lifecycleState'],
                                                 distribitution_state,
                                                 self._logger)
            self._logger.debug("SDC resource %s status: %s", self.name,
                               self.status)

    @property
    def unique_uuid(self) -> str:
        """Return and lazy load the unique_uuid."""
        if not self._unique_uuid:
            self.load()
        return self._unique_uuid

    @property
    def unique_identifier(self) -> str:
        """Return and lazy load the unique_identifier."""
        if not self._unique_identifier:
            self.deep_load()
        return self._unique_identifier

    @unique_uuid.setter
    def unique_uuid(self, value: str) -> None:
        """Set value for unique_uuid."""
        self._unique_uuid = value

    @unique_identifier.setter
    def unique_identifier(self, value: str) -> None:
        """Set value for unique_identifier."""
        self._unique_identifier = value

    def load(self) -> None:
        """Load Object information from SDC."""
        self.exists()

    def deep_load(self) -> None:
        """Deep load Object informations from SDC."""
        url = (
            f"{self.base_front_url}/sdc1/feProxy/rest/v1/"
            "screen?excludeTypes=VFCMT&excludeTypes=Configuration"
        )
        headers = headers_sdc_creator(SdcResource.headers)
        if self.status == const.UNDER_CERTIFICATION:
            headers = headers_sdc_tester(SdcResource.headers)
        response = self.send_message_json("GET",
                                          "Deep Load {}".format(
                                              type(self).__name__),
                                          url,
                                          headers=headers)
        if response:
            for resource in response[self._sdc_path()]:
                if resource["uuid"] == self.identifier:
                    self._logger.debug("Resource %s found in %s list",
                                       resource["name"], self._sdc_path())
                    self.unique_identifier = resource["uniqueId"]

    def _generate_action_subpath(self, action: str) -> str:
        """

        Generate subpath part of SDC action url.

        Args:
            action (str): the action that will be done

        Returns:
            str: the subpath part

        """
        return action

    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Returns:
            str: the end of the path

        """
        return self.unique_identifier

    def _action_url(self,
                    base: str,
                    subpath: str,
                    version_path: str,
                    action_type: str = None) -> str:
        """
        Generate action URL for SDC.

        Args:
            base (str): base part of url
            subpath (str): subpath of url
            version_path (str): version path of the url
            action_type (str, optional): the type of action
                                         ('distribution', 'distribution-state'
                                         or 'lifecycleState'). Default to
                                         'lifecycleState').

        Returns:
            str: the URL to use

        """
        if not action_type:
            action_type = "lifecycleState"
        return "{}/{}/{}/{}/{}".format(base, self._resource_type, version_path,
                                       action_type, subpath)

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/rest/v1/catalog".format(cls.base_front_url)

    @classmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc/v1/catalog".format(cls.base_back_url)

    @classmethod
    def _get_all_url(cls) -> str:
        """
        Get URL for all elements in SDC.

        Returns:
            str: the url

        """
        return "{}/{}?resourceType={}".format(cls._base_url(), cls._sdc_path(),
                                              cls.__name__.upper())

    @classmethod
    def _get_objects_list(cls, result: List[Dict[str, Any]]
                          ) -> List[Dict[str, Any]]:
        """
        Import objects created in SDC.

        Args:
            result (Dict[str, Any]): the result returned by SDC in a Dict

        Return:
            List[Dict[str, Any]]: the list of objects

        """
        return result

    def _get_version_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get version from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the version

        """
        return sdc_infos['version']

    def _get_identifier_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get identifier from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the identifier

        """
        return sdc_infos['uuid']

    @classmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'SdcResource':
        """
        Import SdcResource from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Return:
            SdcResource: the created resource

        """
        cls._logger.debug("importing SDC Resource %s from SDC", values['name'])
        return cls(name=values['name'], sdc_values=values)

    def _copy_object(self, obj: 'SdcResource') -> None:
        """
        Copy relevant properties from object.

        Args:
            obj (SdcResource): the object to "copy"

        """
        self.identifier = obj.identifier
        self.unique_uuid = obj.unique_uuid
        self.status = obj.status
        self.version = obj.version
        self.unique_identifier = obj.unique_identifier
        self._specific_copy(obj)

    def _specific_copy(self, obj: 'SdcResource') -> None:
        """
        Copy specific properties from object.

        Args:
            obj (SdcResource): the object to "copy"

        """
    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details ([type]): [description]

        """
    def update_informations_from_sdc_creation(self,
                                              details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC after creation.

        Args:
            details ([type]): the details from SDC

        """
        self.unique_uuid = details['invariantUUID']
        distribution_state = None

        if 'distributionStatus' in details:
            distribution_state = details['distributionStatus']
        self.status = self._parse_sdc_status(details['lifecycleState'],
                                             distribution_state, self._logger)
        self.version = details['version']
        self.unique_identifier = details['uniqueId']

    # Not my fault if SDC has so many states...
    # pylint: disable=too-many-return-statements
    @staticmethod
    def _parse_sdc_status(sdc_status: str, distribution_state: str,
                          logger: logging.Logger) -> str:
        """
        Parse  SDC status in order to normalize it.

        Args:
            sdc_status (str): the status found in SDC
            distribution_state (str): the distribution status found in SDC.
                                        Can be None.

        Returns:
            str: the normalized status

        """
        logger.debug("Parse status for SDC Resource")
        if sdc_status.capitalize() == const.CERTIFIED:
            if distribution_state and distribution_state == const.SDC_DISTRIBUTED:
                return const.DISTRIBUTED
            return const.CERTIFIED
        if sdc_status == const.NOT_CERTIFIED_CHECKOUT:
            return const.DRAFT
        if sdc_status == const.NOT_CERTIFIED_CHECKIN:
            return const.CHECKED_IN
        if sdc_status == const.READY_FOR_CERTIFICATION:
            return const.SUBMITTED
        if sdc_status == const.CERTIFICATION_IN_PROGRESS:
            return const.UNDER_CERTIFICATION
        if sdc_status != "":
            return sdc_status
        return None

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        raise NotImplementedError("SDC is an abstract class")

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.RESOURCE_PATH
