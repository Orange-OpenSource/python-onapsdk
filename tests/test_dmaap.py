# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
import os
from unittest.mock import patch
import json

from onapsdk.dmaap.dmaap import Dmaap, ACTION, GET_HTTP_METHOD

TOPIC = "fault"

DMAAP_EVENTS_URL = f"http://dmaap.api.simpledemo.onap.org:3904/events"
DMAAP_EVENTS_FROM_TOPIC_URL = f"http://dmaap.api.simpledemo.onap.org:3904/events/{TOPIC}/CG1/C1"
DMAAP_RESET_EVENTS = f"http://dmaap.api.simpledemo.onap.org:3904/reset"


@patch.object(Dmaap, "send_message_json")
def test_should_get_all_events(send_message_mock):
    # given

    # when
    Dmaap.get_all_events()

    # then
    verify_that_event_was_send_to_ves(send_message_mock, DMAAP_EVENTS_URL)


@patch.object(Dmaap, "send_message_json")
def test_should_get_events_from_topic(send_message_mock):
    # given

    # when
    Dmaap.get_events_for_topic(TOPIC)

    # then
    verify_that_event_was_send_to_ves(send_message_mock, DMAAP_EVENTS_FROM_TOPIC_URL)


@patch.object(Dmaap, "send_message_json")
def test_should_remove_all_events(send_message_mock):
    # given

    # when
    Dmaap.reset_events()

    # then
    verify_that_event_was_send_to_ves(send_message_mock, DMAAP_RESET_EVENTS)


def verify_that_event_was_send_to_ves(send_message_mock, dmaap_url):
    send_message_mock.assert_called_once_with(
        GET_HTTP_METHOD, ACTION, dmaap_url,
        exception=ValueError
    )
    send_message_mock.return_value = None
