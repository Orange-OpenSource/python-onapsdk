
from unittest import mock

from onapsdk.aai.business.platform import Platform


PLATFORMS = {
    "platform": [
        {
            "platform-name": "test-name",
            "resource-version": "1234"
        },
        {
            "platform-name": "test-name2",
            "resource-version": "4321"
        }
    ]
}


COUNT = {
    "results":[
        {
            "platform":1
        }
    ]
}


@mock.patch("onapsdk.aai.business.platform.Platform.send_message_json")
def test_platform_get_all(mock_send_message_json):
    mock_send_message_json.return_value = {}
    assert len(list(Platform.get_all())) == 0

    mock_send_message_json.return_value = PLATFORMS
    platforms = list(Platform.get_all())
    assert len(platforms) == 2
    lob1, lob2 = platforms
    assert lob1.name == "test-name"
    assert lob1.resource_version == "1234"
    assert lob2.name == "test-name2"
    assert lob2.resource_version == "4321"


@mock.patch("onapsdk.aai.business.platform.Platform.send_message_json")
def test_platform_get_by_name(mock_send):
    Platform.get_by_name(name="test-name")
    mock_send.assert_called_once_with("GET",
                                      "Get test-name platform",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v23/business/platforms/platform/test-name")


@mock.patch("onapsdk.aai.business.platform.Platform.send_message")
@mock.patch("onapsdk.aai.business.platform.Platform.get_by_name")
def test_platform_create(_, mock_send):
    Platform.create(name="test-name")
    mock_send.assert_called_once_with("PUT",
                                      "Declare A&AI platform",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v23/business/platforms/platform/test-name",
                                      data='{\n    "platform-name": "test-name"\n}')


@mock.patch("onapsdk.aai.business.platform.Platform.send_message_json")
def test_line_of_business_count(mock_send_message_json):
    mock_send_message_json.return_value = COUNT
    assert Platform.count() == 1
