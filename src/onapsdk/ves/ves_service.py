# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
"""Base VES module."""

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService


class VesService(OnapService):
    """Base VES class.

    Stores url to VES API (edit if you want to use other) and authentication tuple
    (username, password).
    """

    _url: str = settings.VES_URL
