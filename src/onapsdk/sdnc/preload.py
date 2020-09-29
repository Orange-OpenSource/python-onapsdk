#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDNC preload module."""
from typing import Any, Dict, Iterable

from onapsdk.utils.headers_creator import headers_sdnc_creator
from onapsdk.utils.jinja import jinja_env

from .sdnc_element import SdncElement


class Preload(SdncElement):
    """Preload base class."""

    headers: Dict[str, str] = headers_sdnc_creator(SdncElement.headers)


class PreloadInformation(Preload):
    """Preload information."""

    def __init__(self, preload_id: str, preload_type: str, preload_data: Dict[str, Any]) -> None:
        """Preload information initialization.

        Args:
            preload_id (str): Preload id
            preload_type (str): Preload type
            preload_data (Dict[str, Any]): Preload data
        """
        super().__init__()
        self.preload_id: str = preload_id
        self.preload_type: str = preload_type
        self.preload_data: Dict[str, Any] = preload_data

    def __repr__(self) -> str:  # noqa
        """Preload information human readble string.

        Returns:
            str: Preload information description

        """
        return (f"PreloadInformation(preload_id={self.preload_id}, "
                f"preload_type={self.preload_type}, "
                f"preload_data={self.preload_data})")

    @classmethod
    def get_all(cls) -> Iterable["PreloadInformation"]:
        """Get all preload informations.

        Get all uploaded preloads.

        Yields:
            PreloadInformation: Preload information object

        """
        for preload_information in \
            cls.send_message_json(\
                "GET",\
                "Get SDNC preload information",\
                f"{cls.base_url}/restconf/operational/GENERIC-RESOURCE-API:preload-information",\
                exception=ValueError).get('preload-information', {}).get('preload-list', []):
            yield PreloadInformation(preload_id=preload_information["preload-id"],
                                     preload_type=preload_information["preload-type"],
                                     preload_data=preload_information["preload-data"])


class NetworkPreload(Preload):
    """Class to upload network module preload."""

    @classmethod
    def upload_network_preload(cls,
                               network: "Network",
                               network_instance_name: str,
                               subnets: Iterable["Subnet"] = None) -> None:
        """Upload network preload.

        Args:
            network: Network object
            network_instance_name (str): network instance name
            subnets (Iterable[Subnet], optional): Iterable object of Subnet.
                Defaults to None.

        Raises:
            ValueError: Preload request returns HTTP response with error code

        """
        cls.send_message_json(
            "POST",
            "Upload Network preload using GENERIC-RESOURCE-API",
            (f"{cls.base_url}/restconf/operations/"
             "GENERIC-RESOURCE-API:preload-network-topology-operation"),
            data=jinja_env().get_template(
                "instantiate_network_ala_carte_upload_preload_gr_api.json.j2").
            render(
                network=network,
                network_instance_name=network_instance_name,
                subnets=subnets if subnets else []
            ),
            exception=ValueError
        )


class VfModulePreload(Preload):
    """Class to upload vf module preload."""

    @classmethod
    def upload_vf_module_preload(cls,  # pylint: disable=too-many-arguments
                                 vnf_instance: "VnfInstance",
                                 vf_module_instance_name: str,
                                 vf_module: "VfModule",
                                 vnf_parameters: Iterable["InstantiationParameter"] = None) -> None:
        """Upload vf module preload.

        Args:
            vnf_instance: VnfInstance object
            vf_module_instance_name (str): VF module instance name
            vf_module (VfModule): VF module
            vnf_parameters (Iterable[InstantiationParameter], optional): Iterable object
                of InstantiationParameter. Defaults to None.

        Raises:
            ValueError: Preload request returns HTTP response with error code

        """
        vnf_para = []
        if vnf_parameters:
            for vnf_parameter in vnf_parameters:
                vnf_para.append({
                    "name": vnf_parameter.name,
                    "value": vnf_parameter.value
                    })
        cls.send_message_json(
            "POST",
            "Upload VF module preload using GENERIC-RESOURCE-API",
            (f"{cls.base_url}/restconf/operations/"
             "GENERIC-RESOURCE-API:preload-vf-module-topology-operation"),
            data=jinja_env().get_template(
                "instantiate_vf_module_ala_carte_upload_preload_gr_api.json.j2").
            render(
                vnf_instance=vnf_instance,
                vf_module_instance_name=vf_module_instance_name,
                vf_module=vf_module,
                vnf_parameters=vnf_para
            ),
            exception=ValueError
        )
