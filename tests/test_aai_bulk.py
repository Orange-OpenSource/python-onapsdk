
from unittest import mock

from onapsdk.aai.bulk import AaiBulk, AaiBulkRequest, AaiBulkResponse


BULK_RESPONSES = {
    "operation-responses": [
        {
            "action": "put",
            "uri": "test-uri",
            "response-status-code": 400,
            "response-body": None
        },
        {
            "action": "post",
            "uri": "test-uri",
            "response-status-code": 201,
            "response-body": "blabla"
        }
    ]
}


@mock.patch("onapsdk.aai.bulk.AaiBulk.send_message_json")
def test_aai_bulk(mock_send_message_json):
    mock_send_message_json.return_value = BULK_RESPONSES
    responses = list(AaiBulk.single_transaction(
        [
            AaiBulkRequest(
                action="post",
                uri="test-uri",
                body={"blabla: blabla"}
            ),
            AaiBulkRequest(
                action="get",
                uri="test-uri",
                body={}
            )
        ]
    ))
    assert len(responses) == 2
    resp_1, resp_2 = responses
    assert resp_1.action == "put"
    assert resp_1.uri == "test-uri"
    assert resp_1.status_code == 400
    assert resp_1.body is None
    assert resp_2.action == "post"
    assert resp_2.uri == "test-uri"
    assert resp_2.status_code == 201
    assert resp_2.body == "blabla"
