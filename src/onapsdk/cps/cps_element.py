# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK CPS element module."""

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService


class CpsElement(OnapService):
    """Mother Class of all CPS elements."""

    _url: str = settings.CPS_URL
    auth: tuple = settings.CPS_AUTH
