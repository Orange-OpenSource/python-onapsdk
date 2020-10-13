"""Microsevice bus module."""
from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_msb_creator


class MSB(OnapService):
    """Microservice Bus base class."""

    base_url = settings.MSB_URL
    headers = headers_msb_creator(OnapService.headers)
