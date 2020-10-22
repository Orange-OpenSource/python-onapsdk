#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service properties module."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Input:
    """Property input dataclass."""

    unique_id: str
    input_type: str
    name: str
    sdc_resource: "SdcResource"
    _default_value: Optional[Any] = field(repr=False, default=None)

    @property
    def default_value(self) -> Any:
        """Input default value.

        Returns:
            Any: Input default value

        """
        return self._default_value

    @default_value.setter
    def default_value(self, value: Any) -> None:
        """Set input default value.

        Use related sdc_resource "set_input_default_value"
            method to set default value in SDC. We use that
            because different types of SDC resources has different
            urls to call SDC API.

        Args:
            value (Any): Default value to set

        """
        self.sdc_resource.set_input_default_value(self, value)
        self._default_value = value

@dataclass
class NestedInput:
    """Dataclass used for nested input declaration."""

    sdc_resource: "SdcResource"
    input_obj: Input


class Property:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """Service property class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 property_type: str,
                 description: Optional[str] = None,
                 unique_id: Optional[str] = None,
                 parent_unique_id: Optional[str] = None,
                 sdc_resource: Optional["SdcResource"] = None,
                 value: Optional[Any] = None,
                 get_input_values: Optional[List[Dict[str, str]]] = None) -> None:
        """Property class initialization.

        Args:
            property_type (str): [description]
            description (Optional[str], optional): [description]. Defaults to None.
            unique_id (Optional[str], optional): [description]. Defaults to None.
            parent_unique_id (Optional[str], optional): [description]. Defaults to None.
            sdc_resource (Optional[, optional): [description]. Defaults to None.
            value (Optional[Any], optional): [description]. Defaults to None.
            get_input_values (Optional[List[Dict[str, str]]], optional): [description].
                Defaults to None.
        """
        self.name: str = name
        self.property_type: str = property_type
        self.description: str = description
        self.unique_id: str = unique_id
        self.parent_unique_id: str = parent_unique_id
        self.sdc_resource: "SdcResource" = sdc_resource
        self._value: Any = value
        self.get_input_values: List[Dict[str, str]] = get_input_values

    def __repr__(self) -> str:
        """Property object human readable representation.

        Returns:
            str: Property human readable representation

        """
        return f"Property(name={self.name}, property_type={self.property_type})"

    def __eq__(self, obj: "Property") -> bool:
        """Check if two Property object are equal.

        Args:
            obj (Property): Object to compare

        Returns:
            bool: True if objects are equal, False otherwise

        """
        return self.name == obj.name and self.property_type == obj.property_type

    @property
    def input(self) -> Input:
        """Property input.

        Returns property Input object.
            Returns None if property has no associated input.

        Raises:
            AttributeError: Input has no associated SdcResource

            AttributeError: Input for given property does not exits.
                It shouldn't ever happen, but it's possible if after you
                get property object someone delete input.

        Returns:
            Input: Property input object.

        """
        if not self.sdc_resource:
            raise AttributeError("Property has no associated SdcResource")
        if not self.get_input_values:
            return None
        try:
            return next(filter(lambda x: x.unique_id == self.get_input_values[0].get("inputId"),
                               self.sdc_resource.inputs))
        except StopIteration:
            raise AttributeError("Property input does not exist")

    @property
    def value(self) -> Any:
        """Value property.

        Get property value.

        Returns:
            Any: Property value

        """
        return self._value

    @value.setter
    def value(self, val: Any) -> Any:
        if self.sdc_resource:
            self.sdc_resource.set_property_value(self, val)
        self._value = val


@dataclass
class ComponentProperty:
    """Component property dataclass.

    Component properties are inputs objects in SDC, but in logic
        it's a property.

    """

    unique_id: str
    property_type: str
    name: str
    component: "Component"
    _value: Optional[Any] = field(repr=False, default=None)

    @property
    def value(self) -> Any:
        """Property value getter.

        Returns:
            Any: Property value

        """
        return self._value

    @value.setter
    def value(self, val: Any) -> None:
        """Property value setter.

        Set value both in an object and in SDC using it's HTTP API.

        Args:
            val (Any): Property value to set

        """
        self.component.set_property_value(self, val)
        self._value = val
