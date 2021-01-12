#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test CdsBlueprintModel module."""
import os.path

from unittest import mock
from tempfile import TemporaryDirectory

import pytest
import requests
import io

from onapsdk.exceptions import ResourceNotFound
from onapsdk.cds.blueprint_model import BlueprintModel
from onapsdk.cds.cds_element import CdsElement
from onapsdk.cds.blueprint import Blueprint
from onapsdk.onap_service import OnapService


# pylint: disable=C0301
BLUEPRINT_MODEL = {
    "blueprintModel": {
        "id": "11111111-2222-3333-4444-555555555555",
        "artifactUUId": None,
        "artifactType": "SDNC_MODEL",
        "artifactVersion": "1.0.0",
        "artifactDescription": "",
        "internalVersion": None,
        "createdDate": "2020-12-14T19:33:57.000Z",
        "artifactName": "test_blueprint",
        "published": "Y",
        "updatedBy": "Carlos Santana <carlos.santana@onap.com>",
        "tags": "Carlos Santana, test, blueprint"
    }
}

BLUEPRINT_MODEL_LIST = [
    BLUEPRINT_MODEL
]
# pylint: enable=C0301


def test_init():
    """Test the initialization."""
    element = CdsElement()
    assert isinstance(element, OnapService)


def test_class_variables():
    """Test the class variables."""
    assert CdsElement._url == "http://portal.api.simpledemo.onap.org:30449"
    assert CdsElement.auth == ("ccsdkapps", "ccsdkapps")
    assert CdsElement.headers == {
        "Content-Type": "application/json",
        "Accept": "application/json"}


@mock.patch.object(CdsElement, 'send_message_json')
def test_blueprint_model_all(mock_send):
    """Test get_all function of BlueprintModel."""
    mock_send.return_value = BLUEPRINT_MODEL_LIST
    assert len(list(BlueprintModel.get_all())) == 1

    blueprint_model_1 = next(BlueprintModel.get_all())
    assert blueprint_model_1.blueprint_model_id == "11111111-2222-3333-4444-555555555555"
    assert blueprint_model_1.artifact_uuid is None
    assert blueprint_model_1.artifact_type == "SDNC_MODEL"
    assert blueprint_model_1.artifact_version == "1.0.0"
    assert blueprint_model_1.internal_version is None
    assert blueprint_model_1.created_date == "2020-12-14T19:33:57.000Z"
    assert blueprint_model_1.artifact_name == "test_blueprint"
    assert blueprint_model_1.published == "Y"
    assert blueprint_model_1.updated_by == "Carlos Santana <carlos.santana@onap.com>"
    assert blueprint_model_1.tags == "Carlos Santana, test, blueprint"


@mock.patch.object(CdsElement, 'send_message_json')
def test_blueprint_model_all_empty(mock_send):
    """Test get_all function of BlueprintModel with no BlueprintModels."""
    mock_send.return_value = ""
    assert len(list(BlueprintModel.get_all())) == 0


@mock.patch.object(CdsElement, 'send_message_json')
def test_blueprint_model_by_id(mock_send):
    """Test get_by_id function of BlueprintModel."""
    mock_send.return_value = BLUEPRINT_MODEL

    blueprint_model_2 = BlueprintModel.get_by_id(
        blueprint_model_id="11111111-2222-3333-4444-555555555555")
    assert blueprint_model_2.blueprint_model_id == "11111111-2222-3333-4444-555555555555"
    assert blueprint_model_2.artifact_uuid is None
    assert blueprint_model_2.artifact_type == "SDNC_MODEL"
    assert blueprint_model_2.artifact_version == "1.0.0"
    assert blueprint_model_2.internal_version is None
    assert blueprint_model_2.created_date == "2020-12-14T19:33:57.000Z"
    assert blueprint_model_2.artifact_name == "test_blueprint"
    assert blueprint_model_2.published == "Y"
    assert blueprint_model_2.updated_by == "Carlos Santana <carlos.santana@onap.com>"
    assert blueprint_model_2.tags == "Carlos Santana, test, blueprint"


@mock.patch.object(CdsElement, 'send_message_json')
def test_blueprint_model_by_id_non_existing(mock_send):
    """Test get_by_id exception for non existing BlueprintModel."""

    mock_send.side_effect = ResourceNotFound
    with pytest.raises(ResourceNotFound) as exc:
        BlueprintModel.get_by_id(
            blueprint_model_id="11111111-2222-3333-4444-555555555555")

    assert exc.type == ResourceNotFound


@mock.patch.object(CdsElement, 'send_message_json')
def test_blueprint_model_by_name_and_version(mock_send):
    """Test get_by_name_and_version function of BlueprintModel."""
    mock_send.return_value = BLUEPRINT_MODEL

    blueprint_model_3 = BlueprintModel.get_by_name_and_version(
        blueprint_name="test_blueprint",
        blueprint_version="1.0.0")
    assert blueprint_model_3.blueprint_model_id == "11111111-2222-3333-4444-555555555555"
    assert blueprint_model_3.artifact_uuid is None
    assert blueprint_model_3.artifact_type == "SDNC_MODEL"
    assert blueprint_model_3.artifact_version == "1.0.0"
    assert blueprint_model_3.internal_version is None
    assert blueprint_model_3.created_date == "2020-12-14T19:33:57.000Z"
    assert blueprint_model_3.artifact_name == "test_blueprint"
    assert blueprint_model_3.published == "Y"
    assert blueprint_model_3.updated_by == "Carlos Santana <carlos.santana@onap.com>"
    assert blueprint_model_3.tags == "Carlos Santana, test, blueprint"


@mock.patch.object(CdsElement, 'send_message_json')
def test_blueprint_model_by_name_and_version_non_existing(mock_send):
    """Test get_by_name_and_version exception for non existing BlueprintModel."""

    mock_send.side_effect = ResourceNotFound
    with pytest.raises(ResourceNotFound) as exc:
        BlueprintModel.get_by_name_and_version(
            blueprint_name="test_blueprint_wrong",
            blueprint_version="1.0.0")

    assert exc.type == ResourceNotFound


@mock.patch.object(CdsElement, 'send_message')
def test_get_blueprint_object(mock_send):
    """Test retrieve Blueprint object for selected BlueprintModel."""
    mock_send.return_value.content = b"test cba - it will never work"

    blueprint_model_4 = BlueprintModel(
        blueprint_model_id="11111111-2222-3333-4444-555555555555")

    blueprint4_object = blueprint_model_4.get_blueprint()
    assert isinstance(blueprint4_object, Blueprint)


@mock.patch.object(CdsElement, 'send_message')
def test_save_blueprint(mock_send):
    """Test download BlueprintModel from onap cds."""
    r = requests.Response()
    r.raw = io.BytesIO(b'test cba - it will never work')
    mock_send.return_value = r

    blueprint_model_5 = BlueprintModel(
        blueprint_model_id="11111111-2222-3333-4444-555555555555")

    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test.zip")
        blueprint_model_5.save(dst_file_path=path)

        with open(path, "rb") as f:
            assert f.read() == b"test cba - it will never work"


@mock.patch.object(CdsElement, 'send_message')
def test_delete_blueprint(mock_send):
    """Test delete BlueprintModel in onap cds. """

    blueprint_model_6 = BlueprintModel(
        blueprint_model_id="11111111-2222-3333-4444-555555555555")
    blueprint_model_6.delete()
    mock_send.assert_called_once()

    method, description, url = mock_send.call_args[0]
    assert method == "DELETE"
    assert description == f"Delete blueprint"
    assert url == f"{CdsElement._url}/api/v1/blueprint-model/{blueprint_model_6.blueprint_model_id}"
