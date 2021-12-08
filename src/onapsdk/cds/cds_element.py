# SPDX-License-Identifier: Apache-2.0
"""Base CDS module."""
from abc import ABC

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
from onapsdk.utils.gui import GuiItem, GuiList

class CdsElement(OnapService, ABC):
    """Base CDS class.

    Stores url to CDS API (edit if you want to use other) and authentication tuple
    (username, password).
    """

    # These should be stored in configuration. There is even a task in Orange repo.
    _url: str = settings.CDS_URL
    auth: tuple = settings.CDS_AUTH

    @classmethod
    def get_guis(cls) -> GuiItem:
        """Retrieve the status of the CDS GUIs.

        Only one GUI is referenced for CDS: CDS UI

        Return the list of GUIs
        """
        gui_url = settings.CDS_GUI_SERVICE
        cds_gui_response = cls.send_message(
            "GET", "Get CDS GUI Status", gui_url)
        guilist = GuiList([])
        guilist.add(GuiItem(
            gui_url,
            cds_gui_response.status_code))
        return guilist
