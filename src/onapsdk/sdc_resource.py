#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
import logging
from typing import Any, Dict, List

from onapsdk.constants import CERTIFIED, DRAFT
from onapsdk.sdc import SDC


class SdcResource(SDC):
    """Mother Class of all SDC resources."""

    _logger: logging.Logger = logging.getLogger(__name__)
    PATH = "resources"
    ACTION_TEMPLATE = 'sdc_resource_action.json.j2'
    ACTION_METHOD = 'POST'

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None):
        """Initialize the object."""
        super().__init__()
        self.name: str = name
        self._unique_uuid: str = None
        if sdc_values:
            self.identifier = sdc_values['uuid']
            self.version = sdc_values['version']
            self.unique_uuid = sdc_values['invariantUUID']
            self.status = self._parse_sdc_status(sdc_values['lifecycleState'])

    @property
    def unique_uuid(self) -> str:
        """Return and lazy load the unique_uuid."""
        if not self._unique_uuid:
            self.load()
        return self._unique_uuid

    @unique_uuid.setter
    def unique_uuid(self, value: str) -> None:
        """Set value for unique_uuid."""
        self._unique_uuid = value

    def load(self) -> None:
        """Load Object information from SDC."""
        self.exists()

    def _generate_action_subpath(self, action: str) -> str:
        """

        Generate subpath part of SDC action url.

        Args:
            action (str): the action that will be done

        Returns:
            str: the subpath part

        """
        return action.lower()

    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Returns:
            str: the end of the path

        """
        return self.identifier

    @staticmethod
    def _action_url(base: str, subpath: str, version_path: str) -> str:
        """
        Generate action URL for SDC.

        Args:
            base (str): base part of url
            subpath (str): subpath of url
            version_path (str): version path of the url

        Returns:
            str: the URL to use

        """
        return "{}/resources/{}/lifecycleState/{}".format(base, version_path,
                                                          subpath)

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
        return "{}/{}?resourceType={}".format(cls._base_url(), cls.PATH,
                                              cls.__name__.upper())

    @classmethod
    def _get_objects_list(
            cls, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        return cls(values['name'], sdc_values=values)

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

    def update_informations_from_sdc_creation(self,
                                              details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC after creation.

        Args:
            details ([type]): the details from SDC
        """
        self.unique_uuid = details['invariantUUID']
        self.status = self._parse_sdc_status(details['lifecycleState'])
        self.version = details['version']

    @staticmethod
    def _parse_sdc_status(sdc_status: str) -> str:
        """
        Parse  SDC status in order to normalize it.

        Args:
            sdc_status (str): the status found in SDC

        Returns:
            str: the normalized status

        """
        if sdc_status.capitalize() == CERTIFIED:
            return CERTIFIED
        if sdc_status == "NOT_CERTIFIED_CHECKOUT":
            return DRAFT
        return None

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        raise NotImplementedError("SDC is an abstract class")
