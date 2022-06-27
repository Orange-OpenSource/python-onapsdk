from unittest import mock

import pytest

from onapsdk.aai.business import OwningEntity
from onapsdk.exceptions import ResourceNotFound


OWNING_ENTITIES = {
    "owning-entity":[
        {
            "owning-entity-id":"ff6c945f-89ab-4f14-bafd-0cdd6eac791a",
            "owning-entity-name":"OE-Generic",
            "resource-version":"1588244348931",
        },
        {
            "owning-entity-id":"OE-generic",
            "owning-entity-name":"OE-generic",
            "resource-version":"1587388597761"
        },
        {
            "owning-entity-id":"b3dcdbb0-edae-4384-b91e-2f114472520c"
            ,"owning-entity-name":"test",
            "resource-version":"1588145971158"
        }
    ]
}


OWNING_ENTITY = {
    "owning-entity-id":"OE-generic",
    "owning-entity-name":"OE-generic",
    "resource-version":"1587388597761"
}


@mock.patch.object(OwningEntity, "send_message_json")
def test_owning_entity_get_all(mock_send):
    mock_send.return_value = OWNING_ENTITIES
    owning_entities = list(OwningEntity.get_all())
    assert len(owning_entities) == 3
    owning_entity = owning_entities[0]
    assert owning_entity.owning_entity_id == "ff6c945f-89ab-4f14-bafd-0cdd6eac791a"
    assert owning_entity.name == "OE-Generic"
    assert owning_entity.url == (f"{owning_entity.base_url}{owning_entity.api_version}/"
                                 "business/owning-entities/owning-entity/"
                                 f"{owning_entity.owning_entity_id}")


@mock.patch.object(OwningEntity, "send_message_json")
def test_owning_entity_get_by_name(mock_send):
    mock_send.return_value = OWNING_ENTITIES
    with pytest.raises(ResourceNotFound) as exc:
        OwningEntity.get_by_owning_entity_name("invalid name")
    assert exc.type == ResourceNotFound
    owning_entity = OwningEntity.get_by_owning_entity_name("OE-Generic")
    assert owning_entity.owning_entity_id == "ff6c945f-89ab-4f14-bafd-0cdd6eac791a"
    assert owning_entity.name == "OE-Generic"


@mock.patch.object(OwningEntity, "send_message")
@mock.patch.object(OwningEntity, "send_message_json")
def test_owning_entity_create(mock_send_json, mock_send):
    mock_send_json.return_value = OWNING_ENTITY
    OwningEntity.create(
        name="OE-generic",
    )

    owning_entity = OwningEntity.create(
        name="OE-generic",
        owning_entity_id="OE-generic"
    )
    assert owning_entity.owning_entity_id == "OE-generic"
    assert owning_entity.name == "OE-generic"
