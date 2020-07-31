#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vf module."""
from typing import Dict, List, Union

import time
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.properties import NestedInput, Property
from onapsdk.sdc.vsp import Vsp
import onapsdk.constants as const


class Vf(SdcResource):
    """
    ONAP Vf Object used for SDC operations.

    Attributes:
        name (str): the name of the vendor. Defaults to "Generic-Vendor".
        identifier (str): the unique ID of the vendor from SDC.
        status (str): the status of the vendor from SDC.
        version (str): the version ID of the vendor from SDC.
        vsp (Vsp): the Vsp used for VF creation
        uuid (str): the UUID of the VF (which is different from identifier,
                    don't ask why...)
        unique_identifier (str): Yet Another ID, just to puzzle us...

    """

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None,  # pylint: disable=too-many-arguments
                 vsp: Vsp = None, properties: List[Property] = None,
                 inputs: Union[Property, NestedInput] = None):
        """
        Initialize vf object.

        Args:
            name (optional): the name of the vf

        """
        super().__init__(sdc_values=sdc_values, properties=properties, inputs=inputs)
        self.name: str = name or "ONAP-test-VF"
        self.vsp: Vsp = vsp or None
        self._time_wait: int = 10

    @property
    def resource_inputs_url(self) -> str:
        """Vf inputs url.

        Returns:
            str: Vf inputs url

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}")

    def onboard(self) -> None:
        """Onboard the VF in SDC."""
        if not self.status:
            if not self.vsp:
                raise ValueError("No Vsp was given")
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
        """Create the Vf in SDC if not already existing."""
        if self.vsp:
            self._create("vf_create.json.j2", name=self.name, vsp=self.vsp)

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        result = self._action_to_sdc(const.CERTIFY, "lifecycleState")
        if result:
            self.load()
