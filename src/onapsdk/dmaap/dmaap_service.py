# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
"""Base VES module."""

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService


class DmaapService(OnapService):
    """Base DMAAP class.

    Stores url to DMAAP API (edit if you want to use other).
    """

    _url: str = settings.DMAAP_URL
