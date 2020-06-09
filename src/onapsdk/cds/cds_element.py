# SPDX-License-Identifier: Apache-2.0
"""Base CDS module."""
from abc import ABC

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService


class CdsElement(OnapService, ABC):
    """Base CDS class.

    Stores url to CDS API (edit if you want to use other).
    """

    # These should be stored in configuration. There is even a task in Orange repo.
    _url: str = settings.CDS_URL
