#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vf module."""
from typing import Dict

import time
from onapsdk.sdc_resource import SdcResource
from onapsdk.vsp import Vsp
import onapsdk.constants as const
from onapsdk.utils.headers_creator import headers_sdc_creator


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

    headers = headers_sdc_creator(SdcResource.headers)

    def __init__(self, name: str = None, sdc_values: Dict[str, str] = None,
                 vsp: Vsp = None):
        """
        Initialize vendor object.

        Args:
            name (optional): the name of the vendor

        """
        super().__init__(sdc_values=sdc_values)
        self.name: str = name or "ONAP-test-VF"
        self.vsp: Vsp = vsp or None
        self._time_wait: int = 10

    def onboard(self) -> None:
        """Onboard the VF in SDC."""
        if not self.status:
            if not self.vsp:
                raise ValueError("No Vsp was given")
            self.create()
            time.sleep(self._time_wait)
            self.onboard()
        elif self.status == const.DRAFT:
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
