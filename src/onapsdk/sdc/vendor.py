#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vendor module."""
from typing import Any
from typing import Dict

from onapsdk.sdc.sdc_element import SdcElement
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

    VENDOR_PATH = "vendor-license-models"
    headers = headers_sdc_creator(SdcElement.headers)

    def __init__(self, name: str = None):
        """
        Initialize vendor object.

        Args:
            name (optional): the name of the vendor

        """
        super().__init__()
        self.name: str = name or "Generic-Vendor"

    def onboard(self) -> None:
        """Onboard the vendor in SDC."""
        if not self.status:
            self.create()
            self.onboard()
        elif self.status == const.DRAFT:
            self.submit()

    def create(self) -> None:
        """Create the vendor in SDC if not already existing."""
        self._create("vendor_create.json.j2", name=self.name)

    def submit(self) -> None:
        """Submit the SDC vendor in order to enable it."""
        self._logger.info("attempting to certify/sumbit vendor %s in SDC",
                          self.name)
        if self.status != const.CERTIFIED and self.created():
            self._really_submit()
        elif self.status == const.CERTIFIED:
            self._logger.warning(
                "vendor %s in SDC is already submitted/certified", self.name)
        elif not self.created():
            self._logger.warning("vendor %s in SDC is not created", self.name)

    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details (Dict[str, Any]): dict from SDC

        """
        self._status = details['results'][-1]['status']

    @classmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'Vendor':
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

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        self._action_to_sdc(const.SUBMIT)
        self._status = const.CERTIFIED

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.VENDOR_PATH
