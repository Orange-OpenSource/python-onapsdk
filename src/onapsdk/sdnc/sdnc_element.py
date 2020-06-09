#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDNC base module."""
from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService


class SdncElement(OnapService):
    """SDNC base class."""

    base_url = settings.SDNC_URL
