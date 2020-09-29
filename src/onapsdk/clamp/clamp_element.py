#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Clamp module."""
from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService as Onap
from onapsdk.sdc.service import Service


class Clamp(Onap):
    """Mother Class of all CLAMP elements."""

    #class variable
    _base_url = settings.CLAMP_URL

    @classmethod
    def __init__(cls, cert: tuple = None):
        """
        Initialize CLAMP object.

        Args:
            cert (tuple): certificate required for CLAMP authentification

        """
        super().__init__(cls)
        cls.cert = cert

    @classmethod
    def base_url(cls) -> str:
        """Give back the base url of Clamp."""
        return f"{cls._base_url}/restservices/clds/v2"

    @classmethod
    def check_loop_template(cls, service: Service) -> str:
        """
        Return loop template name if exists.

        Args:
            service (Service): the distributed sdc service with tca blueprint artifact

        Raises:
            ValueError : Template not found

        Returns:
            if required template exists in CLAMP or not

        """
        url = f"{cls.base_url()}/templates/"
        for template in cls.send_message_json('GET',
                                              'Get Loop Templates',
                                              url,
                                              cert=cls.cert):
            if template["modelService"]["serviceDetails"]["name"] == service.name:
                return template["name"]
        raise ValueError("Template not found")

    @classmethod
    def check_policies(cls, policy_name: str, req_policies: int = 30) -> bool:
        """
        Ensure that a policy is stored in CLAMP.

        Args:
            policy_name (str): policy acronym
            req_policies (int): number of required policies in CLAMP

        Returns:
            if required policy exists in CLAMP or not

        """
        url = f"{cls.base_url()}/policyToscaModels/"
        policies = cls.send_message_json('GET',
                                         'Get stocked policies',
                                         url,
                                         cert=cls.cert)
        exist_policy = False
        for policy in policies:
            if policy["policyAcronym"] == policy_name:
                exist_policy = True
        return (len(policies) >= req_policies) and exist_policy
