#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
from typing import Any, Dict, List
from operator import attrgetter
from abc import ABC, abstractmethod

from requests import Response

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
import onapsdk.constants as const
from onapsdk.utils.jinja import jinja_env


class SDC(OnapService, ABC):
    """Mother Class of all SDC elements."""

    server: str = "SDC"
    base_front_url = settings.SDC_FE_URL
    base_back_url = settings.SDC_BE_URL

    def __init__(self, name: str = None) -> None:
        """Initialize SDC."""
        super().__init__()
        self.name: str = name

    def __eq__(self, other: Any) -> bool:
        """
        Check equality for SDC and children.

        Args:
            other: another object

        Returns:
            bool: True if same object, False if not

        """
        if isinstance(other, type(self)):
            return self.name == other.name
        return False

    @classmethod
    @abstractmethod
    def _get_all_url(cls) -> str:
        """
        Get URL for all elements in SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @classmethod
    @abstractmethod
    def _get_objects_list(cls,
                          result: List[Dict[str, Any]]) -> List['SdcResource']:
        """
        Import objects created in SDC.

        Args:
            result (Dict[str, Any]): the result returned by SDC in a Dict

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @classmethod
    @abstractmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @classmethod
    @abstractmethod
    def _base_create_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @abstractmethod
    def _copy_object(self, obj: 'SDC') -> None:
        """
        Copy relevant properties from object.

        Args:
            obj (Sdc): the object to "copy"

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @classmethod
    @abstractmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'SDC':
        """
        Import Sdc object from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @classmethod
    def get_all(cls, **kwargs) -> List['SDC']:
        """
        Get the objects list created in SDC.

        Returns:
            the list of the objects

        """
        cls._logger.info("retrieving all objects of type %s from SDC",
                         cls.__name__)
        url = cls._get_all_url()
        result = cls.send_message_json('GET', "get {}s".format(cls.__name__),
                                       url, **kwargs)
        objects = []
        if result:
            for obj_info in cls._get_objects_list(result):
                objects.append(cls.import_from_sdc(obj_info))
        cls._logger.debug("number of %s returned: %s", cls.__name__,
                          len(objects))
        return objects

    def exists(self) -> bool:
        """
        Check if object already exists in SDC and update infos.

        Returns:
            True if exists, False either

        """
        self._logger.debug("check if %s %s exists in SDC", type(self).__name__, self.name)
        objects = self.get_all()

        self._logger.debug("filtering objects of all versions to be %s", self.name)
        relevant_objects = list(filter(lambda obj: obj == self, objects))

        if not relevant_objects:

            self._logger.info("%s %s doesn't exist in SDC", type(self).__name__, self.name)
            return False

        if hasattr(self, 'version_filter') and self.version_filter is not None: # pylint: disable=no-member

            self._logger.debug("filtering %s objects by version %s", self.name, self.version_filter) # pylint: disable=no-member
            all_versioned = filter(lambda obj: obj.version == self.version_filter,  # pylint: disable=no-member
                                   relevant_objects)

            try:
                versioned_object = next(all_versioned)
            except StopIteration:
                self._logger.info("Version %s of %s %s, doesn't exist in SDC",
                                  self.version_filter, type(self).__name__, self.name) # pylint: disable=no-member
                return False

        else:
            versioned_object = max(relevant_objects, key=attrgetter('version'))

        self._logger.info("%s found, updating information", type(self).__name__)
        self._copy_object(versioned_object)
        return True


class SdcOnboardable(SDC, ABC):
    """Base class for onboardable SDC resources (Vendors, Services, ...)."""

    ACTION_TEMPLATE: str
    ACTION_METHOD: str

    def __init__(self, name: str = None) -> None:
        """Initialize the object."""
        super().__init__(name)
        self._identifier: str = None
        self._status: str = None
        self._version: str = None

    @property
    def identifier(self) -> str:
        """Return and lazy load the identifier."""
        if not self._identifier:
            self.load()
        return self._identifier

    @property
    def status(self) -> str:
        """Return and lazy load the status."""
        if self.created() and not self._status:
            self.load()
        return self._status

    @property
    def version(self) -> str:
        """Return and lazy load the version."""
        if self.created() and not self._version:
            self.load()
        return self._version

    @identifier.setter
    def identifier(self, value: str) -> None:
        """Set value for identifier."""
        self._identifier = value

    @status.setter
    def status(self, status: str) -> None:
        """Return and lazy load the status."""
        self._status = status

    @version.setter
    def version(self, version: str) -> None:
        """Return and lazy load the status."""
        self._version = version

    def created(self) -> bool:
        """Determine if SDC is created."""
        if self.name and not self._identifier:
            return self.exists()
        return bool(self._identifier)

    def submit(self) -> None:
        """Submit the SDC object in order to enable it."""
        self._logger.info("attempting to certify/sumbit %s %s in SDC",
                          type(self).__name__, self.name)
        if self.status != const.CERTIFIED and self.created():
            self._really_submit()
        elif self.status == const.CERTIFIED:
            self._logger.warning("%s %s in SDC is already submitted/certified",
                                 type(self).__name__, self.name)
        elif not self.created():
            self._logger.warning("%s %s in SDC is not created",
                                 type(self).__name__, self.name)

    def _create(self, template_name: str, **kwargs) -> None:
        """Create the object in SDC if not already existing."""
        self._logger.info("attempting to create %s %s in SDC",
                          type(self).__name__, self.name)
        if not self.exists():
            url = "{}/{}".format(self._base_create_url(), self._sdc_path())
            template = jinja_env().get_template(template_name)
            data = template.render(**kwargs)
            create_result = self.send_message_json('POST',
                                                   "create {}".format(
                                                       type(self).__name__),
                                                   url,
                                                   data=data)
            if create_result:
                self._logger.info("%s %s is created in SDC",
                                  type(self).__name__, self.name)
                self._status = const.DRAFT
                self.identifier = self._get_identifier_from_sdc(create_result)
                self._version = self._get_version_from_sdc(create_result)
                self.update_informations_from_sdc_creation(create_result)
            else:
                self._logger.error(
                    "an error occured during creation of %s %s in SDC",
                    type(self).__name__, self.name)
        else:
            self._logger.warning("%s %s is already created in SDC",
                                 type(self).__name__, self.name)

    def _action_to_sdc(self, action: str, action_type: str = None,
                       **kwargs) -> Response:
        """
        Really do an action in the SDC.

        Args:
            action (str): the action to perform
            action_type (str, optional): the type of action
            headers (Dict[str, str], optional): headers to use if any

        Returns:
            Response: the response if any

        """
        subpath = self._generate_action_subpath(action)
        url = self._action_url(self._base_create_url(),
                               subpath,
                               self._version_path(),
                               action_type=action_type)
        template = jinja_env().get_template(self.ACTION_TEMPLATE)
        data = template.render(action=action, const=const)
        result = self.send_message(self.ACTION_METHOD,
                                   "{} {}".format(action,
                                                  type(self).__name__),
                                   url,
                                   data=data,
                                   **kwargs)
        if result:
            self._logger.info("action %s has been performed on %s %s", action,
                              type(self).__name__, self.name)
            return result
        self._logger.error("an error occured during action %s on %s %s in SDC",
                           action,
                           type(self).__name__, self.name)
        return None

    def _get_item_details(self) -> Dict[str, Any]:
        """
        Get item details.

        Returns:
            Dict[str, Any]: the description of the item

        """
        if self.created():
            url = "{}/items/{}/versions".format(self._base_url(),
                                                self.identifier)
            return self.send_message_json('GET', 'get item', url)
        return {}

    def _get_item_version_details(self) -> Dict[Any, Any]:
        """Get vsp item details."""
        if self.created() and self.version:
            url = "{}/items/{}/versions/{}".format(self._base_url(),
                                                   self.identifier,
                                                   self.version)
            return self.send_message_json('GET', 'get item version', url)
        return {}

    @abstractmethod
    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details ([type]): [description]

        """
    @abstractmethod
    def update_informations_from_sdc_creation(self,
                                              details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC after creation.

        Args:
            details ([type]): the details from SDC

        """

    @abstractmethod
    def load(self) -> None:
        """
        Load Object information from SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """

    @abstractmethod
    def _get_version_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get version from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Raises:
            NotImplementedError: this is an abstract method.

        """
    @abstractmethod
    def _get_identifier_from_sdc(self, sdc_infos: Dict[str, Any]) -> str:
        """
        Get identifier from SDC results.

        Args:
            sdc_infos (Dict[str, Any]): the result dict from SDC

        Raises:
            NotImplementedError: this is an abstract method.

        """
    @abstractmethod
    def _generate_action_subpath(self, action: str) -> str:
        """

        Generate subpath part of SDC action url.

        Args:
            action (str): the action that will be done

        Raises:
            NotImplementedError: this is an abstract method.

        """
    @abstractmethod
    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Raises:
            NotImplementedError: this is an abstract method.

        """
    @abstractmethod
    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
    @staticmethod
    @abstractmethod
    def _action_url(base: str,
                    subpath: str,
                    version_path: str,
                    action_type: str = None) -> str:
        """
        Generate action URL for SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """
    @classmethod
    @abstractmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""

    @abstractmethod
    def onboard(self) -> None:
        """Onboard resource.

        Onboarding is a full stack of actions which needs to be done to
            make SDC resource ready to use. It depends on the type of object
            but most of them needs to be created and submitted.
        """
