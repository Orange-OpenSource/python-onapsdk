
from unittest import mock

import pytest

import onapsdk.constants as const
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc.vl import Vl


VLS = [
    {
        "uuid":"e12cedf4-fd3f-4d76-ae2a-0368eaee40dc",
        "invariantUUID":"4084c513-5149-456d-9be0-efc503058799",
        "name":"NeutronNet",
        "version":"1.0",
        "toscaModelURL":"/sdc/v1/catalog/resources/e12cedf4-fd3f-4d76-ae2a-0368eaee40dc/toscaModel",
        "category":"Generic",
        "subCategory":"Network Elements",
        "resourceType":"VL",
        "lifecycleState":"CERTIFIED",
        "lastUpdaterUserId":"jh0003"
    },
    {
        "uuid":"3b9f3a0d-f9d1-4d95-80ce-7f7812a2b7b5",
        "invariantUUID":"c4aa9ad7-1c68-4fde-884e-b9d693b5f725",
        "name":"Network",
        "version":"1.0",
        "toscaModelURL":"/sdc/v1/catalog/resources/3b9f3a0d-f9d1-4d95-80ce-7f7812a2b7b5/toscaModel",
        "category":"Generic",
        "subCategory":"Infrastructure",
        "resourceType":"VL",
        "lifecycleState":"CERTIFIED",
        "lastUpdaterUserId":"jh0003"
    }
]


@mock.patch.object(Vl, 'send_message_json')
def test_get_all_no_vl(mock_send):
    """Returns empty array if no vls."""
    mock_send.return_value = {}
    assert Vl.get_all() == []
    mock_send.assert_called_once_with("GET", 'get Vls', 'https://sdc.api.be.simpledemo.onap.org:30204/sdc/v1/catalog/resources?resourceType=VL')


@mock.patch.object(Vl, 'send_message_json')
def test_get_all_vl(mock_send):
    mock_send.return_value = VLS
    vls = Vl.get_all()
    assert len(vls) == 2
    vl = vls[0]
    assert vl.name == "NeutronNet"
    assert vl.identifier == "e12cedf4-fd3f-4d76-ae2a-0368eaee40dc"
    assert vl.unique_uuid == "4084c513-5149-456d-9be0-efc503058799"
    assert vl.version == "1.0"
    assert vl.status == const.CERTIFIED
    vl = vls[1]
    assert vl.name == "Network"
    assert vl.identifier == "3b9f3a0d-f9d1-4d95-80ce-7f7812a2b7b5"
    assert vl.unique_uuid == "c4aa9ad7-1c68-4fde-884e-b9d693b5f725"
    assert vl.version == "1.0"
    assert vl.status == const.CERTIFIED


@mock.patch.object(Vl, 'send_message_json')
def test_create_vl_not_exists(mock_send):
    mock_send.return_value = VLS
    with pytest.raises(ResourceNotFound):
        Vl("not_exists")
