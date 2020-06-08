#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Microsevice bus module."""
from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_msb_creator


class MSB(OnapService):
    """Microservice Bus base class."""

    base_url = "https://msb.api.simpledemo.onap.org:30283"
    headers = headers_msb_creator(OnapService.headers)
