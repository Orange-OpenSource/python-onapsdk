from unittest import mock

import pytest

from onapsdk.so.so_element import OrchestrationRequest


IN_PROGRESS = {
    "request": {
        "requestStatus": {
            "requestState": "IN_PROGRESS"
        }
    }
}
FAILED = {
    "request": {
        "requestStatus": {
            "requestState": "FAILED"
        }
    }
}
COMPLETE = {
    "request": {
        "requestStatus": {
            "requestState": "COMPLETE"
        }
    }
}
UNKNOWN = {
    "request": {
        "requestStatus": {
            "requestState": "INVALID"
        }
    }
}
BAD_RESPONSE = {}


@mock.patch.object(OrchestrationRequest, "send_message_json")
def test_orchestration_request_status(mock_send_message):
    orchestration_req = OrchestrationRequest(request_id="test")

    mock_send_message.return_value = BAD_RESPONSE
    assert orchestration_req.status == OrchestrationRequest.StatusEnum.UNKNOWN

    mock_send_message.return_value = UNKNOWN
    assert orchestration_req.status == OrchestrationRequest.StatusEnum.UNKNOWN

    mock_send_message.return_value = FAILED
    assert orchestration_req.status == OrchestrationRequest.StatusEnum.FAILED

    mock_send_message.return_value = COMPLETE
    assert orchestration_req.status == OrchestrationRequest.StatusEnum.COMPLETED

    mock_send_message.return_value = IN_PROGRESS
    assert orchestration_req.status == OrchestrationRequest.StatusEnum.IN_PROGRESS
    assert not orchestration_req.finished
    assert not orchestration_req.completed
    assert not orchestration_req.failed

    mock_send_message.return_value = COMPLETE
    assert orchestration_req.finished
    assert orchestration_req.completed
    assert not orchestration_req.failed

    mock_send_message.return_value = FAILED
    assert orchestration_req.finished
    assert not orchestration_req.completed
    assert orchestration_req.failed


