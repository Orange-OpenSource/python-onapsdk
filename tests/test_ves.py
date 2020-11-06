# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
import os
from unittest.mock import patch

from onapsdk.ves.ves import Ves, ACTION, POST_HTTP_METHOD

VERSION = "v7"

VES_URL = f"https://ves.api.simpledemo.onap.org:30417/eventListener/{VERSION}"
VES_BATCH_URL = f"https://ves.api.simpledemo.onap.org:30417/eventListener/{VERSION}/eventBatch"

TEST_EVENT = '{"event": {"test": "val"}}'

@patch.object(Ves, "send_message")
def test_should_send_event_to_ves_service(send_message_mock):
    # given

    # when
    Ves.send_event(VERSION, TEST_EVENT)

    # then
    verify_that_event_was_send_to_ves(TEST_EVENT, send_message_mock, VES_URL)


@patch.object(Ves, "send_message")
def test_should_send_event_batch_to_ves_service(send_message_mock):
    # given

    # when
    Ves.send_batch_event(VERSION, TEST_EVENT)

    # then
    verify_that_event_was_send_to_ves(TEST_EVENT, send_message_mock, VES_BATCH_URL)


def verify_that_event_was_send_to_ves(expected_event, send_message_mock, ves_url):
    send_message_mock.assert_called_once_with(
        POST_HTTP_METHOD, ACTION, ves_url,
        data=expected_event,
        basic_auth=None
    )
    send_message_mock.return_value = None
