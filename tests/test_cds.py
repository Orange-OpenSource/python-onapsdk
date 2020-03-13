# SPDX-License-Identifier: Apache-2.0
import os.path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch, PropertyMock

from pytest import raises

from onapsdk.cds.blueprint import Blueprint
from onapsdk.cds.cds_element import CdsElement
from onapsdk.cds.data_dictionary import DataDictionary, DataDictionarySet


DD_1 = {
    "name": "vf-module-name",
    "tags": "vf-module-name",
    "data_type": "string",
    "description": "vf-module-name",
    "entry_schema": "string",
    "updatedBy": "Singal, Kapil <ks220y@att.com>",
    "definition": {
        "tags": "vf-module-name",
        "name": "vf-module-name",
        "property": {
            "description": "vf-module-name",
            "type": "string"
        },
        "updated-by": "Singal, Kapil <ks220y@att.com>",
        "sources": {
            "input": {
                "type": "source-input"
            },
            "default": {
                "type": "source-default",
                "properties": {}
            }
        }
    }
}


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


@patch.object(CdsElement, "_url", new_callable=PropertyMock)
def test_data_dictionary(cds_element_url_property_mock):
    cds_element_url_property_mock.return_value = "http://127.0.0.1"
    dd = DataDictionary({})
    assert dd.url == "http://127.0.0.1/dictionary"
    assert dd.data_dictionary_json == {}

    dd = DataDictionary(DD_1)
    dd.name == DD_1["name"]


@patch.object(DataDictionary, "send_message")
def test_data_dictionary_upload(send_message_mock):
    dd = DataDictionary(DD_1)
    dd.upload()
    send_message_mock.assert_called_once()


@patch.object(DataDictionary, "send_message")
def test_data_dictionary_set(send_message_mock):
    dd_set = DataDictionarySet()

    dd_set.add(DataDictionary(DD_1))
    assert dd_set.length == 1

    dd_set.add(DataDictionary(DD_1))
    assert dd_set.length == 1

    dd_set.add(DataDictionary({"name": "test"}))
    assert dd_set.length == 2

    dd_set.upload()
    assert send_message_mock.call_count == 2
