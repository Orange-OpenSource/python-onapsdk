#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI Element."""
import pytest
from unittest import mock

from onapsdk.so.so_element import SoElement
from onapsdk.utils.gui import GuiList

@mock.patch.object(SoElement, "send_message")
def test_get_guis(send_message_mock):
    component = SoElement()
    send_message_mock.return_value.status_code = 200
    send_message_mock.return_value.url = "http://so.api.simpledemo.onap.org:30277/"
    gui_results = component.get_guis()
    assert type(gui_results) == GuiList
    assert gui_results.guilist[0].url == send_message_mock.return_value.url
    assert gui_results.guilist[0].status == send_message_mock.return_value.status_code
