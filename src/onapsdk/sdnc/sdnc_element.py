#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDNC base module."""
from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
from onapsdk.utils.gui import GuiItem, GuiList


class SdncElement(OnapService):
    """SDNC base class."""

    base_url = settings.SDNC_URL

    @classmethod
    def get_guis(cls) -> GuiItem:
        """Retrieve the status of the SDNC GUIs.

        There are 2 GUIS
        - SDNC DG Builder
        - SDNC ODL

        Return the list of GUIs
        """
        guilist = GuiList([])
        url = settings.SDNC_DG_GUI_SERVICE
        response = cls.send_message(
            "GET", "Get SDNC GUI DG Status", url)
        guilist.add(GuiItem(
            url,
            response.status_code))
        url = settings.SDNC_ODL_GUI_SERVICE
        response = cls.send_message(
            "GET", "Get SDNC ODL GUI Status", url)
        guilist.add(GuiItem(
            url,
            response.status_code))
        return guilist
