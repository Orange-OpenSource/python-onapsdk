#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Pnf module."""
from typing import Dict, List, Union

import time
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.properties import NestedInput, Property
import onapsdk.constants as const
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp


class Pnf(SdcResource):
    """
    ONAP PNF Object used for SDC operations.

    Attributes:
        name (str): the name of the pnf. Defaults to "ONAP-test-PNF".
        identifier (str): the unique ID of the pnf from SDC.
        status (str): the status of the pnf from SDC.
        version (str): the version ID of the vendor from SDC.
        uuid (str): the UUID of the PNF (which is different from identifier,
                    don't ask why...)
        unique_identifier (str): Yet Another ID, just to puzzle us...
        vendor (optional): the vendor of the PNF
        vsp (option): the vsp related to the PNF

    """

    def __init__(self, name: str = None, vendor: Vendor = None, sdc_values: Dict[str, str] = None,  # pylint: disable=too-many-arguments
                 vsp: Vsp = None, properties: List[Property] = None,
                 inputs: Union[Property, NestedInput] = None):
        """
        Initialize pnf object.

        Args:
            name (optional): the name of the pnf

        """
        super().__init__(sdc_values=sdc_values, properties=properties, inputs=inputs)
        self.name: str = name or "ONAP-test-PNF"
        self.vendor: Vendor = vendor or None
        self.vsp: Vsp = vsp or None
        self._time_wait: int = 10

    @property
    def resource_inputs_url(self) -> str:
        """PNF inputs url.

        Returns:
            str: PNF inputs url

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}")

    def onboard(self) -> None:
        """Onboard the PNF in SDC."""
        if not self.status:
            self.create()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.DRAFT:
            for property_to_add in self._properties_to_add:
                self.add_property(property_to_add)
            for input_to_add in self._inputs_to_add:
                self.declare_input(input_to_add)
            self.submit()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.CERTIFIED:
            self.load()

    def create(self) -> None:
        """Create the PNF in SDC if not already existing."""
        if self.vsp:
            # Create PNF based on given vsp
            self._create("pnf_create_vsp.json.j2", name=self.name, vsp=self.vsp)
        else:
            # Create PNF without vsp
            self._create("pnf_create.json.j2", name=self.name, vendor=self.vendor)

    def _really_submit(self) -> None:
        """Really submit the SDC PNF in order to enable it."""
        result = self._action_to_sdc(const.CERTIFY, "lifecycleState")
        if result:
            self.load()
