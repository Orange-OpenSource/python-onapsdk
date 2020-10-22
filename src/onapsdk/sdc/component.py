#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Component module."""
from dataclasses import dataclass
from typing import Any, Dict, Iterator

from onapsdk.sdc.properties import ComponentProperty
from onapsdk.utils.jinja import jinja_env


@dataclass
class Component:  # pylint: disable=too-many-instance-attributes
    """Component dataclass."""

    created_from_csar: bool
    actual_component_uid: str
    unique_id: str
    normalized_name: str
    name: str
    origin_type: str
    customization_uuid: str
    component_uid: str
    component_version: str
    tosca_component_name: str
    component_name: str
    sdc_resource: "SdcResource"
    parent_sdc_resource: "SdcResource"

    @classmethod
    def create_from_api_response(cls,
                                 api_response: Dict[str, Any],
                                 sdc_resource: "SdcResource",
                                 parent_sdc_resource: "SdcResource") -> "Component":
        """Create component from api response.

        Args:
            api_response (Dict[str, Any]): component API response
            sdc_resource (SdcResource): component's SDC resource
            parent_sdc_resource (SdcResource): component's parent SDC resource

        Returns:
            Component: Component created using api_response and SDC resource

        """
        return cls(created_from_csar=api_response["createdFromCsar"],
                   actual_component_uid=api_response["actualComponentUid"],
                   unique_id=api_response["uniqueId"],
                   normalized_name=api_response["normalizedName"],
                   name=api_response["name"],
                   origin_type=api_response["originType"],
                   customization_uuid=api_response["customizationUUID"],
                   component_uid=api_response["componentUid"],
                   component_version=api_response["componentVersion"],
                   tosca_component_name=api_response["toscaComponentName"],
                   component_name=api_response["componentName"],
                   sdc_resource=sdc_resource,
                   parent_sdc_resource=parent_sdc_resource)

    @property
    def properties_url(self) -> str:
        """Url to get component's properties.

        Returns:
            str: Compoent's properties url

        """
        return self.parent_sdc_resource.get_component_properties_url(self)

    @property
    def properties_value_url(self) -> str:
        """Url to set component property value.

        Returns:
            str: Url to set component property value

        """
        return self.parent_sdc_resource.get_component_properties_value_set_url(self)

    @property
    def properties(self) -> Iterator["ComponentProperty"]:
        """Component properties.

        In SDC it's named as properties, but we uses "inputs" endpoint to fetch them.
            Structure is also input's like, but it's a property.

        Yields:
            ComponentProperty: Component property object

        """
        for component_property in self.sdc_resource.send_message_json(\
                "GET",
                f"Get {self.name} component properties",
                self.properties_url,
                exception=ValueError):
            yield ComponentProperty(unique_id=component_property["uniqueId"],
                                    name=component_property["name"],
                                    property_type=component_property["type"],
                                    _value=component_property.get("value"),
                                    component=self)

    def get_property(self, property_name: str) -> "ComponentProperty":
        """Get component property by it's name.

        Args:
            property_name (str): property name

        Raises:
            AttributeError: Component has no property with given name

        Returns:
            ComponentProperty: Component's property object

        """
        for property_obj in self.properties:
            if property_obj.name == property_name:
                return property_obj
        raise AttributeError("Component has no property with %s name" % property_name)

    def set_property_value(self, property_obj: "ComponentProperty", value: Any) -> None:
        """Set property value.

        Set given value to component property

        Args:
            property_obj (ComponentProperty): Component property object
            value (Any): Property value to set

        """
        self.sdc_resource.send_message_json(
            "POST",
            f"Set {self.name} component property {property_obj.name} value",
            self.properties_value_url,
            data=jinja_env().get_template(\
                "sdc_resource_component_set_property_value.json.j2").\
                render(
                    component=self,
                    value=value,
                    property=property_obj
                ),
            exception=ValueError
        )
