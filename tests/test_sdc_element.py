#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcElement module."""
import pytest

from onapsdk.sdc_element import SdcElement
from onapsdk.onap_service import OnapService

def test_init():
    """Test the initialization."""
    element = SdcElement()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert SdcElement.server == "SDC"
    assert SdcElement.base_front_url == "http://sdc.api.fe.simpledemo.onap.org:30206"
    assert SdcElement.base_back_url == "http://sdc.api.be.simpledemo.onap.org:30205"
    assert SdcElement.header == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
