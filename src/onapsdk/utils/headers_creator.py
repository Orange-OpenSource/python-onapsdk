#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Header creator package."""
from typing import Dict
from uuid import uuid4
import base64
import hashlib


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


def headers_aai_creator(base_header: Dict[str, str]):
    """
    Create the right headers for AAI creator type.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["x-fromappid"] = "AAI"
    headers["x-transactionid"] = "0a3f6713-ba96-4971-a6f8-c2da85a3176e"
    headers["authorization"] = "Basic QUFJOkFBSQ=="
    return headers


def headers_so_creator(base_header: Dict[str, str]):
    """
    Create the right headers for SO creator type.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["x-fromappid"] = "AAI"
    headers["x-transactionid"] = str(uuid4())
    headers["authorization"] = "Basic SW5mcmFQb3J0YWxDbGllbnQ6cGFzc3dvcmQxJA=="
    headers["cache-control"] = "no-cache"
    return headers


def headers_msb_creator(base_header: Dict[str, str]):
    """
    Create the right headers for MSB.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["cache-control"] = "no-cache"
    return headers


def headers_sdnc_creator(base_header: Dict[str, str]):
    """
    Create the right headers for SDNC.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["authorization"] = \
        "Basic YWRtaW46S3A4Yko0U1hzek0wV1hsaGFrM2VIbGNzZTJnQXc4NHZhb0dHbUp2VXkyVQ=="
    headers["x-transactionid"] = str(uuid4())
    headers["x-fromappid"] = "API client"
    return headers


def headers_sdc_artifact_upload(base_header: Dict[str, str], data: str):
    """
    Create the right headers for sdc artifact upload.

    Args:
        base_header (Dict[str, str]): the base header to use
        data (str): payload data used to create an md5 content header

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["Accept"] = "application/json, text/plain, */*"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Content-Type"] = "application/json; charset=UTF-8"
    md5_content = hashlib.md5(data.encode('UTF-8')).hexdigest()
    content = base64.b64encode(md5_content.encode('ascii')).decode('UTF-8')
    headers["Content-MD5"] = content
    return headers
