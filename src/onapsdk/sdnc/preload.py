#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDNC preload module."""
from typing import Dict, Iterable

from onapsdk.utils.headers_creator import headers_sdnc_creator
from onapsdk.utils.jinja import jinja_env

from .sdnc_element import SdncElement


class VfModulePreload(SdncElement):
    """Class to upload vf module preload."""

    headers: Dict[str, str] = headers_sdnc_creator(SdncElement.headers)

    @classmethod
    def upload_vf_module_preload(cls,  # pylint: disable=too-many-arguments
                                 vnf_instance: "VnfInstance",
                                 vf_module_instance_name: str,
                                 vf_module: "VfModule",
                                 vnf_parameters: Iterable["VnfParameter"] = None,
                                 use_vnf_api=False) -> None:
        """Upload vf module preload.

        Args:
            vnf_instance: VnfInstance object
            vf_module_instance_name (str): VF module instance name
            vf_module (VfModule): VF module
            vnf_parameters (Iterable[VnfParameter], optional): Iterable object of VnfParameters.
                Defaults to None.
            use_vnf_api (bool, optional): Flague which determines if VNF_API should be used.
                Set to False to use GR_API. Defaults to False.

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
        if use_vnf_api:
            url: str = (f"{cls.base_url}/restconf/operations/"
                        "VNF-API:preload-vnf-topology-operation")
            description: str = "Upload VF module preload using VNF-API"
            template: str = "instantiate_vf_module_ala_carte_upload_preload_vnf_api.json.j2"
        else:
            url: str = (f"{cls.base_url}/restconf/operations/"
                        "GENERIC-RESOURCE-API:preload-vf-module-topology-operation")
            description: str = "Upload VF module preload using GENERIC-RESOURCE-API"
            template: str = "instantiate_vf_module_ala_carte_upload_preload_gr_api.json.j2"
        cls.send_message_json(
            "POST",
            description,
            url,
            data=jinja_env().get_template(
                template).
            render(
                vnf_instance=vnf_instance,
                vf_module_instance_name=vf_module_instance_name,
                vf_module=vf_module,
                vnf_parameters=vnf_para
            ),
            exception=ValueError
        )
