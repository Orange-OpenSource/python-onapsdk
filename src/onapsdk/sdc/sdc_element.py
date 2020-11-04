#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
from typing import Any, Dict, List
from abc import ABC, abstractmethod

from onapsdk.sdc import SdcOnboardable
import onapsdk.constants as const


class SdcElement(SdcOnboardable, ABC):
    """Mother Class of all SDC elements."""

    ACTION_TEMPLATE = 'sdc_element_action.json.j2'
    ACTION_METHOD = 'PUT'

    def load(self) -> None:
        """Load Object information from SDC."""
        vsp_details = self._get_item_details()
        if vsp_details:
            self._logger.debug("details found, updating")
            self.version = vsp_details['results'][-1]['id']
            self.update_informations_from_sdc(vsp_details)
        else:
            # exists() method check if exists AND update identifier
            self.exists()

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
    @classmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/onboarding-api/v1.0".format(cls.base_front_url)

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/onboarding-api/v1.0".format(cls.base_front_url)

    def _generate_action_subpath(self, action: str) -> str:
        """

        Generate subpath part of SDC action url.

        Args:
            action (str): the action that will be done

        Returns:
            str: the subpath part

        """
        subpath = self._sdc_path()
        if action == const.COMMIT:
            subpath = "items"
        return subpath

    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Returns:
            str: the end of the path

        """
        return "{}/versions/{}".format(self.identifier, self.version)

    @staticmethod
    def _action_url(base: str,
                    subpath: str,
                    version_path: str,
                    action_type: str = None) -> str:
        """
        Generate action URL for SDC.

        Args:
            base (str): base part of url
            subpath (str): subpath of url
            version_path (str): version path of the url
            action_type (str, optional): the type of action. UNUSED here

        Returns:
            str: the URL to use

        """
        return "{}/{}/{}/actions".format(base, subpath, version_path)

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
        return result['results']

    @classmethod
    def _get_all_url(cls) -> str:
        """
        Get URL for all elements in SDC.

        Returns:
            str: the url

        """
        return "{}/{}".format(cls._base_url(), cls._sdc_path())

    def _copy_object(self, obj: 'SdcElement') -> None:
        """
        Copy relevant properties from object.

        Args:
            obj (SdcElement): the object to "copy"

        """
        self.identifier = obj.identifier

    def _get_version_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get version from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the version

        """
        return sdc_infos['version']['id']

    def _get_identifier_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get identifier from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the identifier

        """
        return sdc_infos['itemId']

    @classmethod
    @abstractmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'SdcElement':
        """
        Import SdcElement from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """
        raise NotImplementedError("SdcElement is an abstract class")
