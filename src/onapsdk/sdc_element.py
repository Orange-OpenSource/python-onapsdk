#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
from typing import Any
from typing import Dict
from typing import List
from typing import Type

import logging

from onapsdk.onap_service import OnapService
import onapsdk.constants as const
from onapsdk.utils.jinja import jinja_env

class SdcElement(OnapService):
    """Mother Class of all SDC elements."""

    server: str = "SDC"
    base_front_url = "http://sdc.api.fe.simpledemo.onap.org:30206"
    base_back_url = "http://sdc.api.be.simpledemo.onap.org:30205"
    _logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize the object."""
        super().__init__()
        self.name: str
        self._status: str = None
        self._identifier: str = None
        self._version: str = None

    @property
    def identifier(self) -> str:
        """Return and lazy load the identifier."""
        if not self._identifier:
            self.load()
        return self._identifier

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

    def created(self) -> bool:
        """Determine if SdcElement is created."""
        return bool(self._identifier)


    @classmethod
    def _get_all(cls, klass: Type) -> List['SdcElement']:
        """
        Get the objects list created in SDC.

        Args:
            path_chunk (str): the url to use
            klass (Type): the object type

        Returns:
            the list of the objects

        """
        cls._logger.info("retrieving all objects of type %s from SDC",
                         klass.__name__)
        url = "{}/{}".format(cls._base_url(), klass.PATH)
        object_lists = cls.send_message_json('GET', "get {}s".format(
            klass.__name__), url)
        objects = []
        if object_lists:
            for obj_info in object_lists['results']:
                objects.append(klass.import_from_sdc(obj_info))
        cls._logger.debug("number of vendors returned: %s", len(objects))
        return objects

    def _exists(self, klass) -> bool:
        """
        Check if object already exists in SDC and update infos.

        Returns:
            True if exists, False either

        """
        self._logger.debug("check if %s %s exists in SDC", klass.__name__,
                           self.name)
        objects = self.get_all()
        for obj in objects:
            self._logger.debug("checking if %s is the same", obj.name)
            if obj == self:
                self._logger.info("%s found, updating information",
                                  klass.__name__)
                self.identifier = obj.identifier
                return True
        self._logger.info("%s %s doesn't exist in SDC", klass.__name__,
                          self.name)
        return False

    def _create(self, klass: type, template_name: str, **kwargs) -> None:
        """Create the Klass in SDC if not already existing."""
        self._logger.info("attempting to create %s %s in SDC", klass.__name__,
                          self.name)
        if not self.exists():
            url = "{}/{}".format(self._base_url(), klass.PATH)
            template = jinja_env().get_template(template_name)
            data = template.render(**kwargs)
            create_result = self.send_message_json('POST',
                                                   "create {}".format(
                                                       klass.__name__),
                                                   url, data=data)
            if create_result:
                self._logger.info("%s %s is created in SDC", klass.__name__,
                                  self.name)
                self._status = const.DRAFT
                self.identifier = create_result['itemId']
                self._version = create_result['version']['id']
            else:
                self._logger.error(
                    "an error occured during creation of %s %s in SDC",
                    klass.__name__, self.name)
        else:
            self._logger.warning("%s %s is already created in SDC",
                                 klass.__name__, self.name)

    def _action_to_sdc(self, klass: type, action: str) -> Dict[Any, Any]:
        """
        Really do an action in the SDC.

        Args:
            action (str): the action to perform

        """
        subpath = klass.PATH
        if action == const.COMMIT:
            subpath = "items"
        url = "{}/{}/{}/actions".format(self._base_url(), subpath,
                                        self._version_path())
        template = jinja_env().get_template('sdc_element_action.json.j2')
        data = template.render(action=action, const=const)
        result = self.send_message('PUT', "{} {}".format(
            action, klass.__name__), url, data=data)
        if result:
            self._logger.info("action %s has been performed on %s %s",
                              action, klass.__name__, self.name)
            return result
        self._logger.error(
            "an error occured during action %s on %s %s in SDC", action,
            klass.__name__, self.name)
        return {}

    def load(self) -> None:
        """Load Object information from SDC."""
        vsp_details = self._get_item_details()
        if vsp_details:
            self._logger.debug("details found, updating")
            self._version = vsp_details['results'][-1]['id']
            self.update_informations_from_sdc(vsp_details)
        else:
            # exists() method check if exists AND update indentifier
            self.exists()

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

    def __eq__(self, other: Any) -> bool:
        """
        Check equality for SdcElement and children.

        Args:
            other: another object

        Returns:
            bool: True if same object, False if not

        """
        if isinstance(other, type(self)):
            return self.name == other.name
        return False

    def update_informations_from_sdc(self, details: Dict[str, Any]) -> None:
        """

        Update instance with details from SDC.

        Args:
            details ([type]): [description]
        """

    @classmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of Sdc.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/onboarding-api/v1.0".format(cls.base_front_url)

    def exists(self):
        """
        Check existence of an object in SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """
        raise NotImplementedError("SdcElement is an abstract class")

    def _version_path(self) -> str:
        """
        Give the end of the path for a version.

        Returns:
            str: the end of the path

        """
        return "{}/versions/{}".format(self.identifier, self.version)

    @classmethod
    def get_all(cls) -> List['SdcElement']:
        """
        Get the Vsp list created in SDC.

        Raises:
            NotImplementedError: this is an abstract method.

        """
        raise NotImplementedError("SdcElement is an abstract class")
