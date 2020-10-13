#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ESR module."""
from onapsdk.utils.jinja import jinja_env
from .msb_service import MSB


class ESR(MSB):
    """External system EST module."""

    base_url = f"{MSB.base_url}/api/aai-esr-server/v1/vims"

    @classmethod
    def register_vim(cls,  # pylint: disable=too-many-arguments
                     cloud_owner: str,
                     cloud_region_id: str,
                     cloud_type: str,
                     cloud_region_version: str,
                     auth_info_cloud_domain: str,
                     auth_info_username: str,
                     auth_info_password: str,
                     auth_info_url: str,
                     owner_defined_type: str = None,
                     cloud_zone: str = None,
                     physical_location_id: str = None,
                     cloud_extra_info: str = None,
                     auth_info_ssl_cacert: str = None,
                     auth_info_ssl_insecure: bool = None) -> None:
        """Register VIM.

        Args:
            cloud_owner (str): cloud owner name, can be customized, e.g. att-aic
            cloud_region_id (str): 	cloud region info based on deployment, e.g. RegionOne
            cloud_type (str): type of the cloud, decides which multicloud plugin to use,
                openstack or vio
            cloud_region_version (str): cloud version, ocata, mitaka or other
            auth_info_cloud_domain (str): domain info for keystone v3
            auth_info_username (str): user name
            auth_info_password (str): password
            auth_info_url (str): authentication url of the cloud, e.g. keystone url
            owner_defined_type (str, optional): cloud-owner defined type indicator (e.g., dcp, lcp).
                Defaults to None.
            cloud_zone (str, optional): zone where the cloud is homed.. Defaults to None.
            physical_location_id (str, optional): complex physical location id for
                cloud-region instance. Defaults to None.
            cloud_extra_info (str, optional): extra info for Cloud. Defaults to None.
            auth_info_ssl_cacert (str, optional): ca file content if enabled ssl on auth-url.
                Defaults to None.
            auth_info_ssl_insecure (bool, optional): whether to verify VIM's certificate.
                Defaults to None.
        """
        cls.send_message(
            "POST",
            "Register VIM instance to ONAP",
            cls.base_url,
            data=jinja_env()
            .get_template("msb_esr_vim_registration.json.j2")
            .render(
                cloud_owner=cloud_owner,
                cloud_region_id=cloud_region_id,
                cloud_type=cloud_type,
                cloud_region_version=cloud_region_version,
                auth_info_cloud_domain=auth_info_cloud_domain,
                auth_info_username=auth_info_username,
                auth_info_password=auth_info_password,
                auth_info_url=auth_info_url,
                owner_defined_type=owner_defined_type,
                cloud_zone=cloud_zone,
                physical_location_id=physical_location_id,
                cloud_extra_info=cloud_extra_info,
                auth_info_ssl_cacert=auth_info_ssl_cacert,
                auth_info_ssl_insecure=auth_info_ssl_insecure,
            ),
        )
