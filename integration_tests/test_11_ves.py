# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
import pytest
import logging
import os
import requests

from onapsdk.configuration import settings
from onapsdk.utils.jinja import jinja_env
from onapsdk.ves.ves import Ves
from onapsdk.dmaap.dmaap import Dmaap

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

requests.post("{}/set_dmaap_address".format(settings.VES_URL), json={"DMAAP_MOCK": settings.DMAAP_URL})

@pytest.mark.integration
def test_should_send_event_to_ves():
    # given
    event: str = jinja_env().get_template("ves_stnd_event.json.j2").render()

    # when
    response = Ves.send_event(
        basic_auth={'username': 'sample1', 'password': 'sample1'},
        json_event=event,
        version="v7"
    )

    # then
    assert response.status_code == 202


@pytest.mark.integration
def test_should_send_batch_event_to_ves():
    # given
    event: str = jinja_env().get_template("ves7_batch_with_stndDefined_valid.json.j2").render()

    # when
    response = Ves.send_batch_event(
        basic_auth={'username': 'sample1', 'password': 'sample1'},
        json_event=event,
        version="v7"
    )

    # then
    assert response.status_code == 202


@pytest.mark.integration
def test_should_send_event_to_ves_and_dmaap():
    # given
    event: str = jinja_env().get_template("ves_stnd_event.json.j2").render()

    # when
    Dmaap.reset_events()
    response = Ves.send_event(
        basic_auth={'username': 'sample1', 'password': 'sample1'},
        json_event=event,

        version="v7"
    )

    # then
    assert response.status_code == 202
    assert len(Dmaap.get_events_for_topic("fault")) == 1


@pytest.mark.integration
def test_should_send_batch_event_to_ves_and_dmaap():
    # given
    event: str = jinja_env().get_template("ves7_batch_with_stndDefined_valid.json.j2").render()

    # when
    Dmaap.reset_events()
    response = Ves.send_batch_event(
        basic_auth={'username': 'sample1', 'password': 'sample1'},
        json_event=event,
        version="v7"
    )

    # then
    assert response.status_code == 202
    topic = Dmaap.get_events_for_topic("fault")
    assert len(topic) == 2
