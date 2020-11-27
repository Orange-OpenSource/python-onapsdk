# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Nokia
import pytest
import logging
import os

from onapsdk.dmaap.dmaap import Dmaap

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))


@pytest.mark.integration
def test_should_get_all_topics_from_dmaap():
    # given

    # when
    response = Dmaap.get_all_topics(basic_auth={'username': 'demo', 'password': 'demo123456!'})

    # then
    assert len(response) == 9
