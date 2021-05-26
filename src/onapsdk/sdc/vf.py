#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vf module."""
import json
from typing import Any, Dict, List, Union
from onapsdk.exceptions import ParameterError, ValidationError

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

    def __init__(self, name: str = None, version: str = None, sdc_values: Dict[str, str] = None,  # pylint: disable=too-many-arguments
                 vsp: Vsp = None, properties: List[Property] = None,
                 inputs: Union[Property, NestedInput] = None,
                 category: str = None, subcategory: str = None):
        """
        Initialize vf object.

        Args:
            name (optional): the name of the vf
            version (str, optional): the version of the vf

        """
        super().__init__(sdc_values=sdc_values, version=version, properties=properties,
                         inputs=inputs, category=category, subcategory=subcategory)
        self.name: str = name or "ONAP-test-VF"
        self.vsp: Vsp = vsp or None

    def create(self) -> None:
        """Create the Vf in SDC if not already existing.

        Raises:
            ParameterError: VSP is not provided during VF object initalization

        """
        if not self.vsp:
            raise ParameterError("No Vsp was given")
        self._create("vf_create.json.j2", name=self.name, vsp=self.vsp, category=self.category)

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        self._action_to_sdc(const.CERTIFY, "lifecycleState")
        self.load()

    def update_vsp(self, vsp: Vsp) -> None:
        """Update Vsp.

        Update VSP UUID and version for Vf object.

        Args:
            vsp (Vsp): Object to be used in Vf

        Raises:
            ValidationError: Vf object request has invalid structure.

        """
        resource_data: Dict[str, Any] = self.send_message_json(
            "GET",
            "Get VF data to update VSP",
            self.resource_inputs_url
        )
        if not all([key_name in resource_data for key_name in ["csarUUID", "csarVersion"]]):
            raise ValidationError(
                "Resource has no csarUUID and csarVersion properties - couldn't update VSP")
        resource_data.update({
            "csarUUID": vsp.csar_uuid,
            "csarVersion": vsp.version
        })
        self.send_message_json(
            "PUT",
            "Update vsp data",
            self.resource_inputs_url,
            data=json.dumps(resource_data)
        )
