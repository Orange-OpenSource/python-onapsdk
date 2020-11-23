# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
"""Base Dmaap event store."""

from onapsdk.dmaap.dmaap_service import DmaapService

ACTION = "Get events from Dmaap"
GET_HTTP_METHOD = "GET"


class Dmaap(DmaapService):
    """Dmaap library provides functions for getting events from Dmaap."""

    dmaap_url = DmaapService._url
    get_all_events_url = f"{dmaap_url}/events"
    get_events_from_topic_url = "{}/events/{}/CG1/C1"
    reset_events_url = f"{dmaap_url}/reset"

    @classmethod
    def get_all_events(cls) -> dict:
        """
        Get all events stored in Dmaap.

        Returns:
            (dict) Events from Dmaap

        """
        return Dmaap.__get_events(cls.get_all_events_url)

    @classmethod
    def get_events_for_topic(cls,
                             topic: str) -> dict:
        """
        Get all events stored specific topic in Dmaap.

        Args:
            topic: (str) topic of events stored in Dmaap

        Returns:
          (dict) Events from Dmaap

        """
        url = cls.get_events_from_topic_url.format(cls.dmaap_url, topic)
        return Dmaap.__get_events(url)

    @classmethod
    def reset_events(cls) -> dict:
        """Remove all events from Dmaap."""
        return Dmaap.__get_events(cls.reset_events_url)

    @classmethod
    def __get_events(cls,
                     url: str) -> dict:
        return cls.send_message_json(
            GET_HTTP_METHOD,
            ACTION,
            url,
            exception=ValueError
        )
