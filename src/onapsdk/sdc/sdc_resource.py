#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
import logging
from abc import ABC
from typing import Any, Dict, Iterator, List, Union
import base64
import time

import onapsdk.constants as const
from onapsdk.exceptions import ParameterError, ResourceNotFound, StatusError
from onapsdk.sdc import SdcOnboardable
from onapsdk.sdc.category_management import ResourceCategory, ServiceCategory
from onapsdk.sdc.component import Component
from onapsdk.sdc.properties import Input, NestedInput, Property
from onapsdk.utils.headers_creator import (headers_sdc_creator,
                                           headers_sdc_tester,
                                           headers_sdc_artifact_upload)
from onapsdk.utils.jinja import jinja_env


# For an unknown reason, pylint keeps seeing _unique_uuid and
# _unique_identifier as attributes along with unique_uuid and unique_identifier
class SdcResource(SdcOnboardable, ABC):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """Mother Class of all SDC resources."""

    RESOURCE_PATH = 'resources'
    ACTION_TEMPLATE = 'sdc_resource_action.json.j2'
    ACTION_METHOD = 'POST'
    headers = headers_sdc_creator(SdcOnboardable.headers)

    def __init__(self, name: str = None, version: str = None, # pylint: disable=too-many-arguments
                 sdc_values: Dict[str, str] = None, properties: List[Property] = None,
                 inputs: Union[Property, NestedInput] = None,
                 category: str = None, subcategory: str = None):
        """Initialize the object."""
        super().__init__(name)
        self.version_filter: str = version
        self._unique_uuid: str = None
        self._unique_identifier: str = None
        self._resource_type: str = "resources"
        self._properties_to_add: List[Property] = properties or []
        self._inputs_to_add: Union[Property, NestedInput] = inputs or []
        self._time_wait: int = 10
        self._category_name: str = category
        self._subcategory_name: str = subcategory
        if sdc_values:
            self._logger.debug("SDC values given, using them")
            self.identifier = sdc_values['uuid']
            self.version = sdc_values['version']
            self.unique_uuid = sdc_values['invariantUUID']
            distribitution_state = None
            if 'distributionStatus' in sdc_values:
                distribitution_state = sdc_values['distributionStatus']
            self.status = self._parse_sdc_status(sdc_values['lifecycleState'],
                                                 distribitution_state,
                                                 self._logger)
            self._logger.debug("SDC resource %s status: %s", self.name,
                               self.status)

    def __repr__(self) -> str:
        """SDC resource description.

        Returns:
            str: SDC resource object description

        """
        return f"{self.__class__.__name__.upper()}(name={self.name})"

    @property
    def unique_uuid(self) -> str:
        """Return and lazy load the unique_uuid."""
        if not self._unique_uuid:
            self.load()
        return self._unique_uuid

    @property
    def unique_identifier(self) -> str:
        """Return and lazy load the unique_identifier."""
        if not self._unique_identifier:
            self.deep_load()
        return self._unique_identifier

    @unique_uuid.setter
    def unique_uuid(self, value: str) -> None:
        """Set value for unique_uuid."""
        self._unique_uuid = value

    @unique_identifier.setter
    def unique_identifier(self, value: str) -> None:
        """Set value for unique_identifier."""
        self._unique_identifier = value

    def load(self) -> None:
        """Load Object information from SDC."""
        self.exists()

    def deep_load(self) -> None:
        """Deep load Object informations from SDC."""
        url = (
            f"{self.base_front_url}/sdc1/feProxy/rest/v1/"
            "screen?excludeTypes=VFCMT&excludeTypes=Configuration"
        )
        headers = headers_sdc_creator(SdcResource.headers)
        if self.status == const.UNDER_CERTIFICATION:
            headers = headers_sdc_tester(SdcResource.headers)

        response = self.send_message_json("GET",
                                          "Deep Load {}".format(
                                              type(self).__name__),
                                          url,
                                          headers=headers)

        for resource in response[self._sdc_path()]:
            if resource["uuid"] == self.identifier:
                self._logger.debug("Resource %s found in %s list",
                                   resource["name"], self._sdc_path())
                self.unique_identifier = resource["uniqueId"]
                self._category_name = resource["categories"][0]["name"]
                subcategories = resource["categories"][0].get("subcategories", [{}])
                self._subcategory_name = None if subcategories is None else \
                    subcategories[0].get("name")

    def _generate_action_subpath(self, action: str) -> str:
        """

        Generate subpath part of SDC action url.

        Args:
            action (str): the action that will be done

        Returns:
            str: the subpath part

        """
        return action

    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Returns:
            str: the end of the path

        """
        return self.unique_identifier

    def _action_url(self,
                    base: str,
                    subpath: str,
                    version_path: str,
                    action_type: str = None) -> str:
        """
        Generate action URL for SDC.

        Args:
            base (str): base part of url
            subpath (str): subpath of url
            version_path (str): version path of the url
            action_type (str, optional): the type of action
                                         ('distribution', 'distribution-state'
                                         or 'lifecycleState'). Default to
                                         'lifecycleState').

        Returns:
            str: the URL to use

        """
        if not action_type:
            action_type = "lifecycleState"
        return "{}/{}/{}/{}/{}".format(base, self._resource_type, version_path,
                                       action_type, subpath)

    @classmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/rest/v1/catalog".format(cls.base_front_url)

    @classmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc/v1/catalog".format(cls.base_back_url)

    @classmethod
    def _get_all_url(cls) -> str:
        """
        Get URL for all elements in SDC.

        Returns:
            str: the url

        """
        return "{}/{}?resourceType={}".format(cls._base_url(), cls._sdc_path(),
                                              cls.__name__.upper())

    @classmethod
    def _get_objects_list(cls, result: List[Dict[str, Any]]
                          ) -> List[Dict[str, Any]]:
        """
        Import objects created in SDC.

        Args:
            result (Dict[str, Any]): the result returned by SDC in a Dict

        Return:
            List[Dict[str, Any]]: the list of objects

        """
        return result

    def _get_version_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get version from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the version

        """
        return sdc_infos['version']

    def _get_identifier_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get identifier from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Returns:
            str: the identifier

        """
        return sdc_infos['uuid']

    @classmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'SdcResource':
        """
        Import SdcResource from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Return:
            SdcResource: the created resource

        """
        cls._logger.debug("importing SDC Resource %s from SDC", values['name'])
        return cls(name=values['name'], sdc_values=values)

    def _copy_object(self, obj: 'SdcResource') -> None:
        """
        Copy relevant properties from object.

        Args:
            obj (SdcResource): the object to "copy"

        """
        self.identifier = obj.identifier
        self.unique_uuid = obj.unique_uuid
        self.status = obj.status
        self.version = obj.version
        self.unique_identifier = obj.unique_identifier
        self._specific_copy(obj)

    def _specific_copy(self, obj: 'SdcResource') -> None:
        """
        Copy specific properties from object.

        Args:
            obj (SdcResource): the object to "copy"

        """

    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details ([type]): [description]

        """
    def update_informations_from_sdc_creation(self,
                                              details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC after creation.

        Args:
            details ([type]): the details from SDC

        """
        self.unique_uuid = details['invariantUUID']
        distribution_state = None

        if 'distributionStatus' in details:
            distribution_state = details['distributionStatus']
        self.status = self._parse_sdc_status(details['lifecycleState'],
                                             distribution_state, self._logger)
        self.version = details['version']
        self.unique_identifier = details['uniqueId']

    # Not my fault if SDC has so many states...
    # pylint: disable=too-many-return-statements
    @staticmethod
    def _parse_sdc_status(sdc_status: str, distribution_state: str,
                          logger: logging.Logger) -> str:
        """
        Parse SDC status in order to normalize it.

        Args:
            sdc_status (str): the status found in SDC
            distribution_state (str): the distribution status found in SDC.
                                        Can be None.

        Returns:
            str: the normalized status

        """
        logger.debug("Parse status for SDC Resource")
        if sdc_status.capitalize() == const.CERTIFIED:
            if distribution_state and distribution_state == const.SDC_DISTRIBUTED:
                return const.DISTRIBUTED
            return const.CERTIFIED
        if sdc_status == const.NOT_CERTIFIED_CHECKOUT:
            return const.DRAFT
        if sdc_status == const.NOT_CERTIFIED_CHECKIN:
            return const.CHECKED_IN
        if sdc_status == const.READY_FOR_CERTIFICATION:
            return const.SUBMITTED
        if sdc_status == const.CERTIFICATION_IN_PROGRESS:
            return const.UNDER_CERTIFICATION
        if sdc_status != "":
            return sdc_status
        return None

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        raise NotImplementedError("SDC is an abstract class")

    def onboard(self) -> None:
        """Onboard resource in SDC."""
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

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.RESOURCE_PATH

    @property
    def deployment_artifacts_url(self) -> str:
        """Deployment artifacts url.

        Returns:
            str: SdcResource Deployment artifacts url

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}/filteredDataByParams?include=deploymentArtifacts")

    @property
    def add_deployment_artifacts_url(self) -> str:
        """Add deployment artifacts url.

        Returns:
            str: Url used to add deployment artifacts

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}/artifacts")

    @property
    def properties_url(self) -> str:
        """Properties url.

        Returns:
            str: SdcResource properties url

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}/filteredDataByParams?include=properties")

    @property
    def add_property_url(self) -> str:
        """Add property url.

        Returns:
            str: Url used to add property

        """
        return (f"{self._base_create_url()}/services/"
                f"{self.unique_identifier}/properties")

    @property
    def set_input_default_value_url(self) -> str:
        """Url to set input default value.

        Returns:
            str: SDC API url used to set input default value

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}/update/inputs")

    @property
    def origin_type(self) -> str:
        """Resource origin type.

        Value needed for composition. It's used for adding SDC resource
            as an another SDC resource component.

        Returns:
            str: SDC resource origin type

        """
        return type(self).__name__.upper()

    @property
    def properties(self) -> Iterator[Property]:
        """SDC resource properties.

        Iterate resource properties.

        Yields:
            Property: Resource property

        """
        for property_data in self.send_message_json(\
                "GET",
                f"Get {self.name} resource properties",
                self.properties_url).get("properties", []):
            yield Property(
                sdc_resource=self,
                unique_id=property_data["uniqueId"],
                name=property_data["name"],
                property_type=property_data["type"],
                parent_unique_id=property_data["parentUniqueId"],
                value=property_data.get("value"),
                description=property_data.get("description"),
                get_input_values=property_data.get("getInputValues"),
            )

    def get_property(self, property_name: str) -> Property:
        """Get resource property by it's name.

        Args:
            property_name (str): property name

        Raises:
            ResourceNotFound: Resource has no property with given name

        Returns:
            Property: Resource's property object

        """
        for property_obj in self.properties:
            if property_obj.name == property_name:
                return property_obj

        msg = f"Resource has no property with {property_name} name"
        raise ResourceNotFound(msg)

    @property
    def resource_inputs_url(self) -> str:
        """Resource inputs url.

        Method which returns url which point to resource inputs.

        Returns:
            str: Resource inputs url

        """
        return (f"{self._base_create_url()}/resources/"
                f"{self.unique_identifier}")


    def create(self) -> None:
        """Create resource.

        Abstract method which should be implemented by subclasses and creates resource in SDC.

        Raises:
            NotImplementedError: Method not implemented by subclasses.

        """
        raise NotImplementedError

    @property
    def inputs(self) -> Iterator[Input]:
        """SDC resource inputs.

        Iterate resource inputs.

        Yields:
            Iterator[Input]: Resource input

        """
        url = f"{self.resource_inputs_url}/filteredDataByParams?include=inputs"
        for input_data in self.send_message_json(\
                "GET", f"Get {self.name} resource inputs",
                url).get("inputs", []):

            yield Input(
                unique_id=input_data["uniqueId"],
                input_type=input_data["type"],
                name=input_data["name"],
                sdc_resource=self,
                _default_value=input_data.get("defaultValue")
            )

    def get_input(self, input_name: str) -> Input:
        """Get input by it's name.

        Args:
            input_name (str): Input name

        Raises:
            ResourceNotFound: Resource doesn't have input with given name

        Returns:
            Input: Found input object

        """
        for input_obj in self.inputs:
            if input_obj.name == input_name:
                return input_obj
        raise ResourceNotFound(f"SDC resource has no {input_name} input")

    def add_deployment_artifact(self, artifact_type: str, artifact_label: str,
                                artifact_name: str, artifact: str):
        """
        Add deployment artifact to resource.

        Add deployment artifact to resource using payload data.

        Args:
            artifact_type (str): all SDC artifact types are supported (DCAE_*, HEAT_*, ...)
            artifact_name (str): the artifact file name including its extension
            artifact (str): artifact file to upload
            artifact_label (str): Unique Identifier of the artifact within the VF / Service.

        Raises:
            StatusError: Resource has not DRAFT status

        """
        data = open(artifact, 'rb').read()
        artifact_string = base64.b64encode(data).decode('utf-8')
        if self.status != const.DRAFT:
            msg = "Can't add artifact to resource which is not in DRAFT status"
            raise StatusError(msg)
        self._logger.debug("Add deployment artifact to sdc resource")
        my_data = jinja_env().get_template(
            "sdc_resource_add_deployment_artifact.json.j2").\
                render(artifact_name=artifact_name,
                       artifact_label=artifact_label,
                       artifact_type=artifact_type,
                       b64_artifact=artifact_string)
        my_header = headers_sdc_artifact_upload(base_header=self.headers, data=my_data)

        self.send_message_json("POST",
                               f"Add deployment artifact for {self.name} sdc resource",
                               self.add_deployment_artifacts_url,
                               data=my_data,
                               headers=my_header)

    @property
    def components(self) -> Iterator[Component]:
        """Resource components.

        Iterate resource components.

        Yields:
            Component: Resource component object

        """
        for component_instance in self.send_message_json(\
                "GET",
                f"Get {self.name} resource inputs",
                f"{self.resource_inputs_url}/filteredDataByParams?include=componentInstances"
                ).get("componentInstances", []):
            sdc_resource: "SdcResource" = SdcResource.import_from_sdc(self.send_message_json(\
                "GET",
                f"Get {self.name} component's SDC resource metadata",
                (f"{self.base_front_url}/sdc1/feProxy/rest/v1/catalog/resources/"
                 f"{component_instance['actualComponentUid']}/"
                 "filteredDataByParams?include=metadata"))["metadata"])
            yield Component.create_from_api_response(api_response=component_instance,
                                                     sdc_resource=sdc_resource,
                                                     parent_sdc_resource=self)

    @property
    def category(self) -> Union[ResourceCategory, ServiceCategory]:
        """Sdc resource category.

        Depends on the resource type returns ResourceCategory or ServiceCategory.

        Returns:
            Uniton[ResourceCategory, ServiceCategory]: resource category

        """
        if self.created():
            if not any([self._category_name, self._subcategory_name]):
                self.deep_load()
            if all([self._category_name, self._subcategory_name]):
                return ResourceCategory.get(name=self._category_name,
                                            subcategory=self._subcategory_name)
            return ServiceCategory.get(name=self._category_name)
        return self.get_category_for_new_resource()

    def get_category_for_new_resource(self) -> ResourceCategory:
        """Get category for resource not created in SDC yet.

        If no category values are provided default category is going to be used.

        Returns:
            ResourceCategory: Category of the new resource

        """
        if not all([self._category_name, self._subcategory_name]):
            return ResourceCategory.get(name="Generic", subcategory="Abstract")
        return ResourceCategory.get(name=self._category_name, subcategory=self._subcategory_name)

    def get_component_properties_url(self, component: "Component") -> str:
        """Url to get component's properties.

        This method is here because component can have different url when
            it's a component of another SDC resource type, eg. for service and
            for VF components have different urls.

        Args:
            component (Component): Component object to prepare url for

        Returns:
            str: Component's properties url

        """
        return (f"{self.resource_inputs_url}/"
                f"componentInstances/{component.unique_id}/properties")

    def get_component_properties_value_set_url(self, component: "Component") -> str:
        """Url to set component property value.

        This method is here because component can have different url when
            it's a component of another SDC resource type, eg. for service and
            for VF components have different urls.

        Args:
            component (Component): Component object to prepare url for

        Returns:
            str: Component's properties url

        """
        return (f"{self.resource_inputs_url}/"
                f"resourceInstance/{component.unique_id}/properties")

    def is_own_property(self, property_to_check: Property) -> bool:
        """Check if given property is one of the resource's properties.

        Args:
            property_to_check (Property): Property to check

        Returns:
            bool: True if resource has given property, False otherwise

        """
        return any((
            prop == property_to_check for prop in self.properties
        ))

    def get_component(self, sdc_resource: "SdcResource") -> Component:
        """Get resource's component.

        Get component by SdcResource object.

        Args:
            sdc_resource (SdcResource): Component's SdcResource

        Raises:
            ResourceNotFound: Component with given SdcResource does not exist

        Returns:
            Component: Component object

        """
        for component in self.components:
            if component.sdc_resource.name == sdc_resource.name:
                return component
        msg = f"SDC resource {sdc_resource.name} is not a component"
        raise ResourceNotFound(msg)

    def declare_input_for_own_property(self, property_obj: Property) -> None:
        """Declare input for resource's property.

        For each property input can be declared.

        Args:
            property_obj (Property): Property to declare input

        """
        self._logger.debug("Declare input for SDC resource property")
        self.send_message_json("POST",
                               f"Declare new input for {property_obj.name} property",
                               f"{self.resource_inputs_url}/create/inputs",
                               data=jinja_env().get_template(\
                                   "sdc_resource_add_input.json.j2").\
                                       render(\
                                           sdc_resource=self,
                                           property=property_obj))

    def declare_nested_input(self,
                             nested_input: NestedInput) -> None:
        """Declare nested input for SDC resource.

        Nested input is an input of one of the components.

        Args:
            nested_input (NestedInput): Nested input object

        """
        self._logger.debug("Declare input for SDC resource's component property")
        component: Component = self.get_component(nested_input.sdc_resource)
        self.send_message_json("POST",
                               f"Declare new input for {nested_input.input_obj.name} input",
                               f"{self.resource_inputs_url}/create/inputs",
                               data=jinja_env().get_template(\
                                   "sdc_resource_add_nested_input.json.j2").\
                                       render(\
                                           sdc_resource=self,
                                           component=component,
                                           input=nested_input.input_obj))

    def declare_input(self, input_to_declare: Union[Property, NestedInput]) -> None:
        """Declare input for given property or nested input object.

        Call SDC FE API to declare input for given property.

        Args:
            input_declaration (Union[Property, NestedInput]): Property to declare input
                or NestedInput object

        Raises:
            ParameterError: if the given property is not SDC resource property

        """
        self._logger.debug("Declare input")
        if isinstance(input_to_declare, Property):
            if self.is_own_property(input_to_declare):
                self.declare_input_for_own_property(input_to_declare)
            else:
                msg = "Given property is not SDC resource property"
                raise ParameterError(msg)
        else:
            self.declare_nested_input(input_to_declare)

    def add_property(self, property_to_add: Property) -> None:
        """Add property to resource.

        Call SDC FE API to add property to resource.

        Args:
            property_to_add (Property): Property object to add to resource.

        Raises:
            StatusError: Resource has not DRAFT status

        """
        if self.status != const.DRAFT:
            msg = "Can't add property to resource which is not in DRAFT status"
            raise StatusError(msg)
        self._logger.debug("Add property to sdc resource")
        self.send_message_json("POST",
                               f"Declare new property for {self.name} sdc resource",
                               self.add_property_url,
                               data=jinja_env().get_template(
                                   "sdc_resource_add_property.json.j2").\
                                    render(
                                        property=property_to_add
                                    ))

    def set_property_value(self, property_obj: Property, value: Any) -> None:
        """Set property value.

        Set given value to resource property

        Args:
            property_obj (Property): Property object
            value (Any): Property value to set

        Raises:
            ParameterError: if the given property is not the resource's property

        """
        if not self.is_own_property(property_obj):
            raise ParameterError("Given property is not a resource's property")
        self._logger.debug("Set %s property value", property_obj.name)
        self.send_message_json("PUT",
                               f"Set {property_obj.name} value to {value}",
                               self.add_property_url,
                               data=jinja_env().get_template(
                                   "sdc_resource_set_property_value.json.j2").\
                                    render(
                                        sdc_resource=self,
                                        property=property_obj,
                                        value=value
                                    )
                               )

    def set_input_default_value(self, input_obj: Input, default_value: Any) -> None:
        """Set input default value.

        Set given value as input default value

        Args:
            input_obj (Input): Input object
            value (Any): Default value to set

        """
        self._logger.debug("Set %s input default value", input_obj.name)
        self.send_message_json("POST",
                               f"Set {input_obj.name} default value to {default_value}",
                               self.set_input_default_value_url,
                               data=jinja_env().get_template(
                                   "sdc_resource_set_input_default_value.json.j2").\
                                    render(
                                        sdc_resource=self,
                                        input=input_obj,
                                        default_value=default_value
                                    )
                               )

    def checkout(self) -> None:
        """Checkout SDC resource."""
        self._logger.debug("Checkout %s SDC resource", self.name)
        result = self._action_to_sdc(const.CHECKOUT, "lifecycleState")
        if result:
            self.load()
