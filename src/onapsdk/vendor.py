#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Vendor module."""
from typing import List

import logging

from onapsdk.sdc_element import SdcElement
import onapsdk.constants as const

class Vendor(SdcElement):
    """
    ONAP Vendor Object used for SDC operations.

    Attributes:
        name (str): the name of the vendor. Defaults to "Generic-Vendor".
        identifier (str): the unique ID of the vendor from SDC.
        status (str): the status of the vendor from SDC.
        version (str): the version ID of the vendor from SDC.
        created (bool): allows to know if the vendor is already created in SDC.

    """

    __logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, name: str = None):
        """
        Initialize vendor object.

        Args:
            name (optional): the name of the vendor
        """
        super().__init__()
        self.identifier: str = None
        self._version: str = None
        self._status: str = None
        self.created: bool = False
        self.name: str = name or "Generic-Vendor"
        self.header = SdcElement.header.copy()
        self.header["USER_ID"] = "cs0008"
        self.header["Authorization"] = ("Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazN"
                                        "lSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=")
        self._loaded = False

    @property
    def version(self):
        """Return and lazy load the version."""
        if self.created and not self._version:
            self.load()
        return self._version

    @property
    def status(self):
        """Return and lazy load the status."""
        if self.created and not self._status:
            self.load()
        return self._status

    @classmethod
    def get_all(cls) -> List['Vendor']:
        """
        Get the vendors list created in SDC.

        Returns:
            the list of the vendors

        """
        cls.__logger.info("retrieving all vendors from SDC")
        url = "{}/vendor-license-models".format(cls._base_url())
        vendor_lists = cls.send_message_json('GET', 'get vendors', url)
        vendors = []
        if vendor_lists:
            for vendor_info in vendor_lists['results']:
                vendor = Vendor(vendor_info['name'])
                vendor.identifier = vendor_info['id']
                vendor.created = True
                vendors.append(vendor)
        cls.__logger.debug("number of vendors returned: %s", len(vendors))
        return vendors

    def exists(self) -> bool:
        """
        Check if vendor already exists in SDC and update infos.

        Returns:
            True if exists, False either

        """
        self.__logger.debug("check if vendor %s exists in SDC", self.name)
        vendors = self.get_all()
        for vendor in vendors:
            self.__logger.debug("checking if %s is the same", vendor.name)
            if vendor == self:
                self.__logger.info("Vendor found, updating information")
                self.identifier = vendor.identifier
                self.created = True
                return True
        self.__logger.info("vendor %s doesn't exist in SDC", self.name)
        return False

    def create(self) -> None:
        """Create the vendor in SDC if not already existing."""
        self.__logger.info("attempting to create vendor %s in SDC", self.name)
        if not self.exists():
            url = "{}/vendor-license-models".format(self._base_url())
            template = self._jinja_env.get_template('vendor_create.json.j2')
            data = template.render(name=self.name)
            create_result = self.send_message_json('POST', 'create vendor',
                                                   url, data=data)
            if create_result:
                self.__logger.info("vendor %s is created in SDC", self.name)
                self.created = True
                self._status = create_result['version']['status']
                self.identifier = create_result['itemId']
                self._version = create_result['version']['id']
            else:
                self.__logger.error(
                    "an error occured during creation of vendor %s in SDC",
                    self.name)
        else:
            self.__logger.warning("vendor %s is already created in SDC", self.name)

    def submit(self) -> None:
        """Submit the SDC vendor in order to enable it."""
        self.__logger.info("attempting to certify/sumbit vendor %s in SDC",
                           self.name)
        if self.status != const.CERTIFIED and self.created:
            self._submit_to_sdc()
        elif self.status == const.CERTIFIED:
            self.__logger.warning(
                "vendor %s in SDC is already submitted/certified",
                self.name)
        elif not self.created:
            self.__logger.warning("vendor %s in SDC is not created", self.name)

    def _submit_to_sdc(self) -> None:
        """Really submit the SDC vendor in order to enable it."""
        url = "{}/vendor-license-models/{}/versions/{}/actions".format(
            self._base_url(), self.identifier, self.version)
        template = self._jinja_env.get_template('vendor_submit.json')
        data = template.render()
        submitted = self.send_message('PUT', 'submit vendor', url,
                                      data=data)
        if submitted:
            self.__logger.info("vendor %s is submitted/certified in SDC",
                               self.name)
            self._status = const.CERTIFIED
        else:
            self.__logger.error((
                "an error occured during submission/creation of vendor"
                " %s in SDC"), self.name)

    def __eq__(self, other: 'Vendor') -> bool:
        """
        Check equality for Vendor.

        Args:
            other: another object

        Returns:
            bool: True if same object, False if not

        """
        if isinstance(other, Vendor):
            return self.name == other.name
        return False

    @classmethod
    def _base_url(cls) -> str:
        """
        Give back the base url of vendor.

        Returns:
            str: the base url

        """
        return "{}/sdc1/feProxy/onboarding-api/v1.0".format(cls.base_front_url)

    def load(self) -> None:
        """Load vendor information from SDC."""
        if self.created:
            url = "{}/items/{}/versions".format(self._base_url(),
                                                self.identifier)
            vendor_details = self.send_message_json('GET', 'get vendors', url)
            if vendor_details:
                self.__logger.debug("details found, updating")
                self._status = vendor_details['results'][-1]['status']
                self._version = vendor_details['results'][-1]['id']
