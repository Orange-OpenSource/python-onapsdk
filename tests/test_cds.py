# SPDX-License-Identifier: Apache-2.0
import os.path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from pytest import raises

from onapsdk.cds.blueprint import Blueprint


@patch.object(Blueprint, "send_message")
def test_blueprint_enrichment(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.enrich()
    send_message_mock.assert_called_once()
    send_message_mock.reset_mock()
    send_message_mock.return_value = None
    with raises(AttributeError):
        blueprint.enrich()


@patch.object(Blueprint, "send_message")
def test_blueprint_publish(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.publish()
    send_message_mock.assert_called_once()


@patch.object(Blueprint, "send_message")
def test_blueprint_deploy(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.deploy()
    send_message_mock.assert_called_once()


def test_blueprint_save():
    blueprint = Blueprint(b"test cba - it will never work")
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test.zip")
        blueprint.save(path)
        with open(path, "rb") as f:
            assert f.read() == b"test cba - it will never work"
