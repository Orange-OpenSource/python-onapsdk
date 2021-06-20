
from unittest import mock

from onapsdk.aai.business.line_of_business import LineOfBusiness


LINES_OF_BUSINESS = {
    "line-of-business": [
        {
            "line-of-business-name": "test-name",
            "resource-version": "1234"
        },
        {
            "line-of-business-name": "test-name2",
            "resource-version": "4321"
        }
    ]
}


@mock.patch("onapsdk.aai.business.line_of_business.LineOfBusiness.send_message_json")
def test_line_of_business_get_all(mock_send_message_json):
    mock_send_message_json.return_value = {}
    assert len(list(LineOfBusiness.get_all())) == 0

    mock_send_message_json.return_value = LINES_OF_BUSINESS
    lines_of_business = list(LineOfBusiness.get_all())
    assert len(lines_of_business) == 2
    lob1, lob2 = lines_of_business
    assert lob1.name == "test-name"
    assert lob1.resource_version == "1234"
    assert lob2.name == "test-name2"
    assert lob2.resource_version == "4321"


@mock.patch("onapsdk.aai.business.line_of_business.LineOfBusiness.send_message_json")
def test_line_of_business_get_by_name(mock_send):
    LineOfBusiness.get_by_name(name="test-name")
    mock_send.assert_called_once_with("GET",
                                      "Get test-name line of business",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v20/business/lines-of-business/line-of-business/test-name")


@mock.patch("onapsdk.aai.business.line_of_business.LineOfBusiness.send_message")
@mock.patch("onapsdk.aai.business.line_of_business.LineOfBusiness.get_by_name")
def test_line_of_business_create(_, mock_send):
    LineOfBusiness.create(name="test-name")
    mock_send.assert_called_once_with("PUT",
                                      "Declare A&AI line of business",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v20/business/lines-of-business/line-of-business/test-name",
                                      data='{\n    "line-of-business-name": "test-name"\n}')
