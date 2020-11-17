# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
"""Base VES event sender."""
from typing import Dict, Union

import requests

from onapsdk.ves.ves_service import VesService

ACTION = "Send event to Ves"
POST_HTTP_METHOD = "POST"


class Ves(VesService):
    """Ves library provides functions for sending events to VES."""

    event_endpoint_url: str = "{}/eventListener/{}"
    event_batch_endpoint_url: str = "{}/eventListener/{}/eventBatch"

    @classmethod
    def send_event(cls,
                   version: str,
                   json_event: str,
                   basic_auth: Dict[str, str] = None) -> Union[requests.Response, None]:
        """
        Send an event stored in a file to VES.

        Args:
            version: (str) version of VES data format
            json_event: (str) event to send
            basic_auth: Dict[str, str], for example:{ 'username': 'bob', 'password': 'secret' }
        Returns:
            (requests.Response) HTTP response status

        """
        return Ves.__send_event_message(cls.event_endpoint_url.format(VesService._url, version),
                                        json_event, basic_auth)

    @classmethod
    def send_batch_event(cls,
                         version: str,
                         json_event: str,
                         basic_auth: Dict[str, str] = None) -> Union[requests.Response, None]:
        """
        Send a batch event stored in a file to VES.

        Args:
            version: (str) version of VES data format
            json_event: (str) event to send
            basic_auth: Dict[str, str], for example:{ 'username': 'bob', 'password': 'secret' }
        Returns:
            (requests.Response) HTTP response status

        """
        return Ves.__send_event_message(cls.event_batch_endpoint_url.
                                        format(VesService._url, version),
                                        json_event, basic_auth)

    @classmethod
    def __send_event_message(cls,
                             base_url: str,
                             json_event: str,
                             basic_auth: Dict[str, str] = None
                             ) -> Union[requests.Response, None]:

        cls._logger.debug("Event to send %s", json_event)
        return cls.send_message(
            POST_HTTP_METHOD,
            ACTION,
            f"{base_url}",
            basic_auth=basic_auth,
            data=json_event
        )
