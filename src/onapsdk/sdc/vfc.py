#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""VFC module."""
from typing import Dict

from onapsdk.exceptions import ResourceNotFound

from .sdc_resource import SdcResource


class Vfc(SdcResource):
    """ONAP VFC Object used for SDC operations."""

    def __init__(self, name: str, version: str = None, sdc_values: Dict[str, str] = None):
        """Initialize VFC object.

        Vfc has to exist in SDC.

        Args:
            name (str): Vfc name
            version (str): Vfc version
            sdc_values (Dict[str, str], optional): Sdc values of existing Vfc. Defaults to None.

        Raises:
            ResourceNotFound: Vfc doesn't exist in SDC

        """
        super().__init__(name=name, version=version, sdc_values=sdc_values)
        if not sdc_values and not self.exists():
            raise ResourceNotFound(
                "This Vfc has to exist prior to object initialization.")

    def _really_submit(self) -> None:
        """Really submit the SDC in order to enable it."""
        raise NotImplementedError("Vfc doesn't need _really_submit")
