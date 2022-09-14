from onapsdk.exceptions import APIError


def test_api_error_response_status_code():
    err = APIError()
    assert err.response_status_code == 0
    err.response_status_code = 404
    assert err.response_status_code == 404
    err = APIError(response_status_code=404)
    assert err.response_status_code == 404
