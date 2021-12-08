#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test A&AI Element."""
import pytest
from unittest import mock

from onapsdk.aai.aai_element import AaiElement, Relationship
from onapsdk.exceptions import RequestError, ResourceNotFound, RelationshipNotFound
from onapsdk.utils.gui import GuiList

@mock.patch.object(AaiElement, "send_message_json")
@mock.patch.object(AaiElement, "url")
def test_relationship_not_found(mock_send, mock_url):

    aai_element = AaiElement()
    mock_url.return_value = "http://my.url/"

    mock_send.side_effect = ResourceNotFound

    aai_element.send_message_json = mock_send

    with pytest.raises(ResourceNotFound) as exc:
        list(aai_element.relationships)
    assert exc.type == RelationshipNotFound

    mock_send.assert_called_once()


def test_relationship_get_relationship_data():
    r = Relationship(
        related_to="test",
        related_link="test",
        relationship_data=[{
            "relationship-key": "test",
            "relationship-value": "test"
        }]
    )
    assert r.get_relationship_data("invalid key") is None
    assert r.get_relationship_data("test") == "test"

@mock.patch.object(AaiElement, "send_message")
def test_get_guis(send_message_mock):
    component = AaiElement()
    send_message_mock.return_value.status_code = 200
    send_message_mock.return_value.url = "https://aai.api.sparky.simpledemo.onap.org:30220/services/aai/webapp/index.html#/browse"
    gui_results = component.get_guis()
    assert type(gui_results) == GuiList
    assert gui_results.guilist[0].url == send_message_mock.return_value.url
    assert gui_results.guilist[0].status == send_message_mock.return_value.status_code
