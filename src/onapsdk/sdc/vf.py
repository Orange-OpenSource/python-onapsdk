#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vf module."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from onapsdk.exceptions import ParameterError
from onapsdk.sdc.properties import ComponentProperty, NestedInput, Property
from onapsdk.sdc.sdc_resource import SdcResource
from onapsdk.sdc.vendor import Vendor
from onapsdk.utils.jinja import jinja_env
import onapsdk.constants as const

if TYPE_CHECKING:
    from onapsdk.sdc.vsp import Vsp


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
                 category: str = None, subcategory: str = None,
                 vendor: Vendor = None):
        """
        Initialize vf object.

        Args:
            name (optional): the name of the vf
            version (str, optional): the version of the vf
            vsp (Vsp, optional): VSP object related with the Vf object.
                Defaults to None.
            vendor (Vendor, optional): Vendor object used if VSP was not provided.
                Defaults to None.

        """
        super().__init__(sdc_values=sdc_values, version=version, properties=properties,
                         inputs=inputs, category=category, subcategory=subcategory)
        self.name: str = name or "ONAP-test-VF"
        self.vsp: Vsp = vsp
        self._vendor: Vendor = vendor

    @property
    def vendor(self) -> Optional[Vendor]:
        """Vendor related wth Vf.

        If Vf is created vendor is get from it's resource metadata.
        Otherwise it's vendor provided by the user or the vendor from vsp.
        It's possible that method returns None, but it won't be possible then
            to create that Vf resource.

        Returns:
            Optional[Vendor]: Vendor object related with Vf

        """
        if self._vendor:
            return self._vendor
        if self.created():
            resource_data: Dict[str, Any] = self.send_message_json(
                "GET",
                "Get VF data to update VSP",
                self.resource_inputs_url
            )
            self._vendor = Vendor(name=resource_data.get("vendorName"))
        elif self.vsp:
            self._vendor = self.vsp.vendor
        return self._vendor


    def create(self) -> None:
        """Create the Vf in SDC if not already existing.

        Raises:
            ParameterError: VSP is not provided during VF object initalization

        """
        if not any([self.vsp, self.vendor]):
            raise ParameterError("At least vsp or vendor needs to be given")
        self._create("vf_create.json.j2", name=self.name, vsp=self.vsp,
                     category=self.category, vendor=self.vendor)

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
        self.send_message_json(
            "PUT",
            "Update vsp data",
            self.resource_inputs_url,
            data=jinja_env()
            .get_template("vf_vsp_update.json.j2")
            .render(resource_data=resource_data,
                    csarUUID=vsp.csar_uuid,
                    csarVersion=vsp.human_readable_version)
        )

    def declare_input(self,
                      input_to_declare: Union[Property, NestedInput, ComponentProperty]) -> None:
        """Declare input for given property, nested input or component property object.

        Call SDC FE API to declare input for given property.

        Args:
            input_declaration (Union[Property, NestedInput]): Property or ComponentProperty
                to declare input or NestedInput object

        Raises:
            ParameterError: if the given property is not SDC resource property

        """
        if not isinstance(input_to_declare, ComponentProperty):
            super().declare_input(input_to_declare)
        else:
            self.send_message("POST",
                              f"Declare new input for {input_to_declare.name} property",
                              f"{self.resource_inputs_url}/create/inputs",
                              data=jinja_env().get_template(\
                                  "component_declare_input.json.j2").\
                                      render(\
                                          component=input_to_declare.component,
                                          property=input_to_declare))
