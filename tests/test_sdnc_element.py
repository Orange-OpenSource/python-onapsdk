#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI Element."""
import pytest
from unittest import mock

from onapsdk.sdnc.sdnc_element import SdncElement
from onapsdk.utils.gui import GuiItem, GuiList

@mock.patch.object(SdncElement, "send_message")
def test_get_guis(send_message_mock):
    component = SdncElement()
    gui_results = component.get_guis()
    assert type(gui_results) == GuiList
    assert len(gui_results.guilist) == 2
    # assert gui_results.guilist[0].status == send_message_mock.return_value.status_code
