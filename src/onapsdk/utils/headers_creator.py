#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Header creator package."""
from typing import Dict


def headers_sdc_creator(base_header: Dict[str, str],
                        user: str = "cs0008",
                        authorization: str = None):
    """
    Create the right headers for SDC creator type.

    Args:
        base_header (Dict[str, str]): the base header to use
        user (str, optional): the user to use. Default to cs0008
        authorization (str, optional): the basic auth to use.
                                       Default to "classic" one

    Returns:
        Dict[str, str]: the needed headers

    """
    return headers_sdc_generic(base_header, user, authorization=authorization)


def headers_sdc_tester(base_header: Dict[str, str],
                       user: str = "jm0007",
                       authorization: str = None):
    """
    Create the right headers for SDC tester type.

    Args:
        base_header (Dict[str, str]): the base header to use
        user (str, optional): the user to use. Default to jm0007
        authorization (str, optional): the basic auth to use.
                                       Default to "classic" one

    Returns:
        Dict[str, str]: the needed headers

    """
    return headers_sdc_generic(base_header, user, authorization=authorization)


def headers_sdc_governor(base_header: Dict[str, str],
                         user: str = "gv0001",
                         authorization: str = None):
    """
    Create the right headers for SDC governor type.

    Args:
        base_header (Dict[str, str]): the base header to use
        user (str, optional): the user to use. Default to gv0001
        authorization (str, optional): the basic auth to use.
                                       Default to "classic" one

    Returns:
        Dict[str, str]: the needed headers

    """
    return headers_sdc_generic(base_header, user, authorization=authorization)


def headers_sdc_operator(base_header: Dict[str, str],
                         user: str = "op0001",
                         authorization: str = None):
    """
    Create the right headers for SDC operator type.

    Args:
        base_header (Dict[str, str]): the base header to use
        user (str, optional): the user to use. Default to op0001
        authorization (str, optional): the basic auth to use.
                                       Default to "classic" one

    Returns:
        Dict[str, str]: the needed headers

    """
    return headers_sdc_generic(base_header, user, authorization=authorization)


def headers_sdc_generic(base_header: Dict[str, str],
                        user: str,
                        authorization: str = None):
    """
    Create the right headers for SDC generic type.

    Args:
        base_header (Dict[str, str]): the base header to use
        user (str): the user to use.
        authorization (str, optional): the basic auth to use.
                                       Default to "classic" one

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["USER_ID"] = user
    headers["Authorization"] = authorization or ("Basic YWFpOktwOGJKNFNYc3pNMF"
                                                 "dYbGhhazNlSGxjc2UyZ0F3ODR2YW"
                                                 "9HR21KdlV5MlU=")
    headers["X-ECOMP-InstanceID"] = "onapsdk"
    return headers
