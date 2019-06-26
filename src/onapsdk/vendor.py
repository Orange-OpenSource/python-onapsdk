#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vendor module."""
from typing import Any
from typing import Dict
from typing import List

import logging

from onapsdk.sdc_element import SdcElement
import onapsdk.constants as const
from onapsdk.utils.headers_creator import headers_sdc_creator

class Vendor(SdcElement):
    """
    ONAP Vendor Object used for SDC operations.

    Attributes:
        name (str): the name of the vendor. Defaults to "Generic-Vendor".
        identifier (str): the unique ID of the vendor from SDC.
        status (str): the status of the vendor from SDC.
        version (str): the version ID of the vendor from SDC.

    """

    PATH = "vendor-license-models"
    _logger: logging.Logger = logging.getLogger(__name__)
    headers = headers_sdc_creator(SdcElement.headers)

    def __init__(self, name: str = None):
        """
        Initialize vendor object.

        Args:
            name (optional): the name of the vendor
        """
        super().__init__()
        self.name: str = name or "Generic-Vendor"

    @property
    def status(self) -> str:
        """Return and lazy load the status."""
        if self.created() and not self._status:
            self.load()
        return self._status

    @classmethod
    def get_all(cls) -> List['Vendor']:
        """
        Get the vendors list created in SDC.

        Returns:
            the list of the vendors

        """
        return cls._get_all(Vendor)

    def exists(self) -> bool:
        """
        Check if vendor already exists in SDC and update infos.

        Returns:
            True if exists, False either

        """
        return self._exists(Vendor)

    def create(self) -> None:
        """Create the vendor in SDC if not already existing."""
        self._create(Vendor, "vendor_create.json.j2", name=self.name)

    def submit(self) -> None:
        """Submit the SDC vendor in order to enable it."""
        self._logger.info("attempting to certify/sumbit vendor %s in SDC",
                          self.name)
        if self.status != const.CERTIFIED and self.created():
            result = self._action_to_sdc(Vendor, const.SUBMIT)
            if result:
                self._status = const.CERTIFIED
        elif self.status == const.CERTIFIED:
            self._logger.warning(
                "vendor %s in SDC is already submitted/certified",
                self.name)
        elif not self.created():
            self._logger.warning("vendor %s in SDC is not created", self.name)

    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details (Dict[str, Any]): dict from SDC

        """
        self._status = details['results'][-1]['status']

    @staticmethod
    def import_from_sdc(values: Dict[str, Any]) -> 'Vendor':
        """
        Import Vendor from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Returns:
            a Vsp instance with right values

        """
        vendor = Vendor(values['name'])
        vendor.identifier = values['id']
        return vendor
