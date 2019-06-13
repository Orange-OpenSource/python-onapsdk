#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
from onapsdk.onap_service import OnapService

class SdcElement(OnapService):
    """Mother Class of all SDC elements."""

    server: str = "SDC"
    base_front_url = "http://sdc.api.fe.simpledemo.onap.org:30206"
    base_back_url = "http://sdc.api.be.simpledemo.onap.org:30205"
