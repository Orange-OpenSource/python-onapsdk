#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Vendor module."""
import pytest

import requests

from onapsdk.vendor import Vendor
import onapsdk.constants as const


@pytest.mark.integration
def test_vendor_unknown():
    """Integration tests for Vendor."""
    response = requests.post("{}/reset".format(Vendor.base_front_url))
    response.raise_for_status()
    vendor = Vendor(name="test")
    vendor.create()
    assert vendor.created
    vendor.submit()
    assert vendor.status == const.CERTIFIED
