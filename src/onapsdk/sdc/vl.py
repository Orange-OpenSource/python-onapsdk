#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vl module."""
from typing import Dict

from onapsdk.utils.headers_creator import headers_sdc_creator

from .sdc_resource import SdcResource


class Vl(SdcResource):
    """ONAP Vl Object used for SDC operations."""

    headers = headers_sdc_creator(SdcResource.headers)

    def __init__(self, name: str, sdc_values: Dict[str, str] = None):
        """Initialize Vl object.

        Vl has to exists in SDC.

        Args:
            name (str): Vl name
            sdc_values (Dict[str, str], optional): Sdc values of existing Vl. Defaults to None.

        Raises:
            ValueError: Vl doesn't exist in SDC

        """
        super().__init__(name, sdc_values)
        if not sdc_values and not self.exists():
            raise ValueError("VL doesn't exist - can't be used")

    def _really_submit(self) -> None:
        """Really submit the SDC in order to enable it."""
        raise NotImplementedError("Vl don't need _really_submit")
