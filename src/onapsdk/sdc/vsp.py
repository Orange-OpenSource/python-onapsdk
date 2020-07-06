#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""VSP module."""
from typing import Any
from typing import BinaryIO
from typing import Callable
from typing import Dict

from onapsdk.sdc.sdc_element import SdcElement
from onapsdk.sdc.vendor import Vendor
import onapsdk.constants as const
from onapsdk.utils.headers_creator import headers_sdc_creator

# Hard to do fewer attributes and still mapping SDC VSP object.
class Vsp(SdcElement): # pylint: disable=too-many-instance-attributes
    """
    ONAP VSP Object used for SDC operations.

    Attributes:
        name (str): the name of the vsp. Defaults to "ONAP-test-VSP".
        identifier (str): the unique ID of the VSP from SDC.
        status (str): the status of the VSP from SDC.
        version (str): the version ID of the VSP from SDC.
        csar_uuid (str): the CSAR ID of the VSP from SDC.
        vendor (Vendor): The VSP Vendor

    """

    VSP_PATH = "vendor-software-products"
    headers = headers_sdc_creator(SdcElement.headers)

    def __init__(self, name: str = None, package: BinaryIO = None,
                 vendor: Vendor = None):
        """
        Initialize vsp object.

        Args:
            name (optional): the name of the vsp

        """
        super().__init__()
        self._csar_uuid: str = None
        self._vendor: Vendor = vendor or None
        self.name: str = name or "ONAP-test-VSP"
        self.package = package or None

    @property
    def status(self):
        """Return and load the status."""
        self.load_status()
        return self._status

    def onboard(self) -> None:
        """Onboard the VSP in SDC."""
        if not self.status:
            if not self.vendor:
                raise ValueError("No Vendor was given")
            self.create()
            self.onboard()
        elif self.status == const.DRAFT:
            if not self.package:
                raise ValueError("No file were given for upload")
            self.upload_package(self.package)
            self.onboard()
        elif self.status == const.UPLOADED:
            self.validate()
            self.onboard()
        elif self.status == const.VALIDATED:
            self.commit()
            self.onboard()
        elif self.status == const.COMMITED:
            self.submit()
            self.onboard()
        elif self.status == const.CERTIFIED:
            self.create_csar()

    def create(self) -> None:
        """Create the Vsp in SDC if not already existing."""
        if self.vendor:
            self._create("vsp_create.json.j2",
                         name=self.name,
                         vendor=self.vendor)

    def upload_package(self, package_to_upload: BinaryIO) -> None:
        """
        Upload given zip file into SDC as artifacts for this Vsp.

        Args:
            package_to_upload (file): the zip file to upload

        """
        self._action("upload package",
                     const.DRAFT,
                     self._upload_action,
                     package_to_upload=package_to_upload)

    def validate(self) -> None:
        """Validate the artifacts uploaded."""
        self._action("validate", const.UPLOADED, self._validate_action)

    def commit(self) -> None:
        """Commit the SDC Vsp."""
        self._action("commit",
                     const.VALIDATED,
                     self._generic_action,
                     action=const.COMMIT)

    def submit(self) -> None:
        """Submit the SDC Vsp in order to enable it."""
        self._action("certify/sumbit",
                     const.COMMITED,
                     self._generic_action,
                     action=const.SUBMIT)

    def create_csar(self) -> None:
        """Create the CSAR package in the SDC Vsp."""
        self._action("create CSAR package", const.CERTIFIED,
                     self._create_csar_action)

    @property
    def vendor(self) -> Vendor:
        """Return and lazy load the vendor."""
        if self.created() and not self._vendor:
            details = self._get_vsp_details()
            if details:
                self._vendor = Vendor(name=details['vendorName'])
        return self._vendor

    @vendor.setter
    def vendor(self, vendor: Vendor) -> None:
        """Set value for Vendor."""
        self._vendor = vendor

    @property
    def csar_uuid(self) -> str:
        """Return and lazy load the CSAR UUID."""
        if self.created() and not self._csar_uuid:
            self.create_csar()
        return self._csar_uuid

    @csar_uuid.setter
    def csar_uuid(self, csar_uuid: str) -> None:
        """Set value for csar uuid."""
        self._csar_uuid = csar_uuid

    def _upload_action(self, package_to_upload: BinaryIO = None):
        """Do upload for real."""
        if package_to_upload:
            url = "{}/{}/{}/orchestration-template-candidate".format(
                self._base_url(), Vsp._sdc_path(), self._version_path())
            headers = self.headers.copy()
            headers.pop("Content-Type")
            headers["Accept-Encoding"] = "gzip, deflate"
            data = {'upload': package_to_upload}
            upload_result = self.send_message('POST',
                                              'upload ZIP for Vsp',
                                              url,
                                              headers=headers,
                                              files=data)
            if upload_result:
                self._logger.info("Files for Vsp %s have been uploaded",
                                  self.name)
            else:
                self._logger.error(
                    "an error occured during file upload for Vsp %s",
                    self.name)

    def _validate_action(self):
        """Do validate for real."""
        url = "{}/{}/{}/orchestration-template-candidate/process".format(
            self._base_url(), Vsp._sdc_path(), self._version_path())
        validate_result = self.send_message_json('PUT',
                                                 'Validate artifacts for Vsp',
                                                 url)
        if validate_result and validate_result['status'] == 'Success':
            self._logger.info("Artifacts for Vsp %s have been validated",
                              self.name)
        else:
            self._logger.error(
                "an error occured during artifacts validation for Vsp %s",
                self.name)

    def _generic_action(self, action=None):
        """Do a generic action for real."""
        if action:
            self._action_to_sdc(action, action_type="lifecycleState")

    def _create_csar_action(self):
        """Create CSAR package for real."""
        result = self._action_to_sdc(const.CREATE_PACKAGE,
                                     action_type="lifecycleState")
        if result:
            self._logger.info("result: %s", result.text)
            data = result.json()
            self.csar_uuid = data['packageId']

    def _action(self, action_name: str, right_status: str,
                action_function: Callable[['Vsp'], None], **kwargs) -> None:
        """
        Generate an action on the instance in order to send it to SDC.

        Args:
            action_name (str): The name of the action (for the logs)
            right_status (str): The status that the object must be
            action_function (function): the function to perform if OK

        """
        self._logger.info("attempting to %s for %s in SDC", action_name,
                          self.name)
        if self.status == right_status:
            action_function(**kwargs)
        else:
            self._logger.warning(
                "vsp %s in SDC is not created or not in %s status", self.name,
                right_status)

    # VSP: DRAFT --> UPLOADED --> VALIDATED --> COMMITED --> CERTIFIED
    def load_status(self) -> None:
        """
        Load Vsp status from SDC.

        rules are following:

        * DRAFT: status == DRAFT and networkPackageName not present

        * UPLOADED: status == DRAFT and networkPackageName present and
          validationData not present

        * VALIDATED: status == DRAFT and networkPackageName present and
          validationData present and state.dirty = true

        * COMMITED: status == DRAFT and networkPackageName present and
          validationData present and state.dirty = false

        * CERTIFIED: status == CERTIFIED

        status is found in sdc items
        state is found in sdc version from items
        networkPackageName and validationData is found in SDC vsp show

        """
        item_details = self._get_item_details()
        if (item_details
                and item_details['results'][-1]['status'] == const.CERTIFIED):
            self._status = const.CERTIFIED
        else:
            self._check_status_not_certified()

    def _check_status_not_certified(self) -> None:
        """Check a status when it's not certified."""
        vsp_version_details = self._get_item_version_details()
        vsp_details = self._get_vsp_details()
        if (vsp_version_details and 'state' in vsp_version_details
                and not vsp_version_details['state']['dirty'] and vsp_details
                and 'validationData' in vsp_details):
            self._status = const.COMMITED
        else:
            self._check_status_not_commited()

    def _check_status_not_commited(self) -> None:
        """Check a status when it's not certified or commited."""
        vsp_details = self._get_vsp_details()
        if (vsp_details and 'validationData' in vsp_details):
            self._status = const.VALIDATED
        elif (vsp_details and 'validationData' not in vsp_details
              and 'networkPackageName' in vsp_details):
            self._status = const.UPLOADED
        elif vsp_details:
            self._status = const.DRAFT

    def _get_vsp_details(self) -> Dict[Any, Any]:
        """Get vsp details."""
        if self.created() and self.version:
            url = "{}/vendor-software-products/{}/versions/{}".format(
                self._base_url(), self.identifier, self.version)

            return self.send_message_json('GET', 'get vsp version', url)
        return {}

    @classmethod
    def import_from_sdc(cls, values: Dict[str, Any]) -> 'Vsp':
        """
        Import Vsp from SDC.

        Args:
            values (Dict[str, Any]): dict to parse returned from SDC.

        Returns:
            a Vsp instance with right values

        """
        cls._logger.debug("importing VSP %s from SDC", values['name'])
        vsp = Vsp(values['name'])
        vsp.identifier = values['id']
        vsp.vendor = Vendor(name=values['vendorName'])
        vsp.load_status()
        cls._logger.info("status of VSP %s: %s", vsp.name, vsp.status)
        return vsp

    def _really_submit(self) -> None:
        """Really submit the SDC Vf in order to enable it."""
        raise NotImplementedError("VSP don't need _really_submit")

    @classmethod
    def _sdc_path(cls) -> None:
        """Give back the end of SDC path."""
        return cls.VSP_PATH
