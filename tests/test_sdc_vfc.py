
from unittest import mock

import pytest

import onapsdk.constants as const
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc.vfc import Vfc


VFCS = [
    {
        "uuid":"18167a36-5f7d-4e10-809f-b73ce7268b00",
        "invariantUUID":"a5852d77-c364-4eec-97c6-8630b8f138ac",
        "name":"Allotted Resource",
        "version":"1.0",
        "toscaModelURL":"/sdc/v1/catalog/resources/18167a36-5f7d-4e10-809f-b73ce7268b00/toscaModel",
        "category":"Allotted Resource",
        "subCategory":"Allotted Resource",
        "resourceType":"VFC",
        "lifecycleState":"CERTIFIED",
        "lastUpdaterUserId":"jh0003"
    },
    {
        "uuid":"3b9f3a0d-f9d1-4d95-80ce-7f7812a2b7b5",
        "invariantUUID":"c4aa9ad7-1c68-4fde-884e-b9d693b5f725",
        "name":"Controller",
        "version":"1.0",
        "toscaModelURL":"/sdc/v1/catalog/resources/3b9f3a0d-f9d1-4d95-80ce-7f7812a2b7b5/toscaModel",
        "category":"Generic",
        "subCategory":"Infrastructure",
        "resourceType":"VFC",
        "lifecycleState":"CERTIFIED",
        "lastUpdaterUserId":"jh0003"
    }
]


@mock.patch.object(Vfc, 'send_message_json')
def test_get_all_no_vfc(mock_send):
    """Returns empty array if no vfcs."""
    mock_send.return_value = {}
    assert Vfc.get_all() == []
    mock_send.assert_called_once_with("GET", 'get Vfcs', 'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/resources?resourceType=VFC')


@mock.patch.object(Vfc, 'send_message_json')
def test_get_all_vfc(mock_send):
    mock_send.return_value = VFCS
    vfcs = Vfc.get_all()
    assert len(vfcs) == 2
    vfc = vfcs[0]
    assert vfc.name == "Allotted Resource"
    assert vfc.identifier == "18167a36-5f7d-4e10-809f-b73ce7268b00"
    assert vfc.unique_uuid == "a5852d77-c364-4eec-97c6-8630b8f138ac"
    assert vfc.version == "1.0"
    assert vfc.status == const.CERTIFIED
    vfc = vfcs[1]
    assert vfc.name == "Controller"
    assert vfc.identifier == "3b9f3a0d-f9d1-4d95-80ce-7f7812a2b7b5"
    assert vfc.unique_uuid == "c4aa9ad7-1c68-4fde-884e-b9d693b5f725"
    assert vfc.version == "1.0"
    assert vfc.status == const.CERTIFIED


@mock.patch.object(Vfc, 'send_message_json')
def test_create_vfc_not_exists(mock_send):
    mock_send.return_value = VFCS
    with pytest.raises(ResourceNotFound):
        Vfc("not_exists")
