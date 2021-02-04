# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
"""Base Dmaap event store."""
from typing import Dict

from onapsdk.dmaap.dmaap_service import DmaapService

ACTION = "Get events from Dmaap"
GET_HTTP_METHOD = "GET"


class Dmaap(DmaapService):
    """Dmaap library provides functions for getting events from Dmaap."""

    dmaap_url = DmaapService._url
    get_all_events_url = f"{dmaap_url}/events"
    get_all_topics_url = f"{dmaap_url}/topics"
    get_events_from_topic_url = "{}/events/{}/CG1/C1"

    @classmethod
    def get_all_events(cls,
                       basic_auth: Dict[str, str]) -> dict:
        """
        Get all events stored in Dmaap.

        Args:
           basic_auth: (Dict[str, str]) for example:{ 'username': 'bob', 'password': 'secret' }
        Returns:
            (dict) Events from Dmaap

        """
        return Dmaap.__get_events(cls.get_all_events_url, basic_auth)

    @classmethod
    def get_events_for_topic(cls,
                             topic: str,
                             basic_auth: Dict[str, str]) -> dict:
        """
        Get all events stored specific topic in Dmaap.

        Args:
            topic: (str) topic of events stored in Dmaap
            basic_auth: (Dict[str, str]) for example:{ 'username': 'bob', 'password': 'secret' }

        Returns:
          (dict) Events from Dmaap

        """
        url = cls.get_events_from_topic_url.format(cls.dmaap_url, topic)
        return Dmaap.__get_events(url, basic_auth)

    @classmethod
    def get_all_topics(cls,
                       basic_auth: Dict[str, str]) -> dict:
        """
        Get all topics stored in Dmaap.

        Args:
           basic_auth: (Dict[str, str]) for example:{ 'username': 'bob', 'password': 'secret' }

        Returns:
            (dict) Topics from Dmaap

        """
        return Dmaap.__get_events(cls.get_all_topics_url, basic_auth)['topics']

    @classmethod
    def __get_events(cls,
                     url: str,
                     basic_auth: Dict[str, str]) -> dict:
        return cls.send_message_json(
            GET_HTTP_METHOD,
            ACTION,
            url,
            basic_auth=basic_auth
        )
