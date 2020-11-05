#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Pnf module."""
from typing import Dict, List, Union

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
        vsp (optional): the vsp related to the PNF

    """

    def __init__(self, name: str = None, version: str = None, vendor: Vendor = None, # pylint: disable=too-many-arguments
                 sdc_values: Dict[str, str] = None, vsp: Vsp = None,
                 properties: List[Property] = None, inputs: Union[Property, NestedInput] = None,
                 category: str = None, subcategory: str = None):
        """
        Initialize pnf object.

        Args:
            name (optional): the name of the pnf
            version (str, optional): the version of a PNF object

        """
        super().__init__(sdc_values=sdc_values, version=version, properties=properties,
                         inputs=inputs, category=category, subcategory=subcategory)
        self.name: str = name or "ONAP-test-PNF"
        self.vendor: Vendor = vendor
        self.vsp: Vsp = vsp

    def create(self) -> None:
        """Create the PNF in SDC if not already existing."""
        if not self.vsp and not self.vendor:
            raise ValueError("Neither Vsp nor vendor was given")
        self._create("pnf_create.json.j2",
                     name=self.name,
                     vsp=self.vsp,
                     vendor=self.vendor,
                     category=self.category)

    def _really_submit(self) -> None:
        """Really submit the SDC PNF in order to enable it."""
        result = self._action_to_sdc(const.CERTIFY, "lifecycleState")
        if result:
            self.load()
