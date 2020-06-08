#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDNC base module."""
from onapsdk.onap_service import OnapService


class SdncElement(OnapService):
    """SDNC base class."""

    base_url = "https://sdnc.api.simpledemo.onap.org:30267"
