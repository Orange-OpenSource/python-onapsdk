#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Header creator package."""
from typing import Dict


def headers_sdc_creator(base_header: Dict[str, str], user: str = None,
                        authorization: str = None):
    """
    Create the right headers for SDC creator type.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["USER_ID"] = user or "cs0008"
    headers["Authorization"] = authorization or ("Basic YWFpOktwOGJKNFNYc3pNMF"
                                                 "dYbGhhazNlSGxjc2UyZ0F3ODR2YW"
                                                 "9HR21KdlV5MlU=")
    headers["X-ECOMP-InstanceID"] = "onapsdk"
    return headers
