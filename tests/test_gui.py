#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI Element."""
import logging
import pytest
import unittest

from onapsdk.nbi.nbi import Nbi
from onapsdk.utils.gui import GuiItem, GuiList

class GuiTestingBase(unittest.TestCase):

    """The super class which testing classes could inherit."""
    logging.disable(logging.CRITICAL)

    def test_get_guis_request_error(self):
        nbi_element = Nbi()
        with self.assertRaises(NotImplementedError):
            nbi_element.get_guis()

    def test_create_bad_gui_item(self):
        with self.assertRaises(TypeError):
            gui1 = GuiItem(184)

    def test_create_bad_gui_list(self):
        with self.assertRaises(TypeError):
            list = GuiList(1, 2, 3)

    def test_add_gui_item(self):
        gui1 = GuiItem('url1', 184)
        gui2 = GuiItem('url2', 200)
        test = GuiList([])
        test.add(gui1)
        test.add(gui2)
        assert len(test.guilist) == 2
        assert test.guilist[0].status == 184
        assert test.guilist[1].url == 'url2'

    def test_add_bad_gui_item(self):
        with self.assertRaises(AttributeError):
            test = GuiList([])
            test.add('not a gui item object')


