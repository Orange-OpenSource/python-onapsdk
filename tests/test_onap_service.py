#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test OnapService module."""
from unittest import mock
from unittest.mock import ANY

import pytest
from jinja2 import Environment
from requests import Response, Session
import simplejson.errors

from requests import (
    Timeout, ConnectionError, RequestException
)

from onapsdk.exceptions import (
    SDKException, RequestError, APIError, ResourceNotFound, InvalidResponse,
    ConnectionFailed
)

from onapsdk.onap_service import OnapService
from onapsdk.sdc.vendor import Vendor

def http_codes():
    return [
        400,  # Bad Request
        401,  # Unauthorized
        403,  # Forbidden
        405,  # Method Not Allowed
        408,  # Request Timeout
        415,  # Unsupported Media Type
        429,  # Too Many Requests
        500,  # Internal Server Error
        501,  # Not Implemented
        502,  # Bad Gateway
        503,  # Service Unavailable
        504   # Gateway Timeout
        ]

class TestException(Exception):
    """Test exception."""

def test_init():
    """Test initialization."""
    svc = OnapService()

def test_class_variables():
    """Test class variables."""
    assert OnapService.server == None
    assert OnapService.headers == {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    assert OnapService.proxy == None

def test_set_proxy():
    """Test set_proxy()."""
    assert OnapService.proxy == None
    Vendor.set_proxy({'the', 'proxy'})
    assert OnapService.proxy == {'the', 'proxy'}
    Vendor.set_proxy(None)
    assert OnapService.proxy == None

# ------------------

@mock.patch.object(Session, 'request')
def test_send_message_OK(mock_request):
    """Returns response if OK."""
    svc = OnapService()
    mocked_response = Response()
    mocked_response.status_code = 200
    mock_request.return_value = mocked_response
    expect_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = svc.send_message("GET", 'test get', 'http://my.url/')
    mock_request.assert_called_once_with('GET', 'http://my.url/',
                                         headers=expect_headers, verify=False,
                                         proxies=None)
    assert response == mocked_response

@mock.patch.object(Session, 'request')
def test_send_message_custom_header_OK(mock_request):
    """Returns response if returns OK with a custom header."""
    svc = OnapService()
    mocked_response = Response()
    mocked_response.status_code = 200
    mock_request.return_value = mocked_response
    expect_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Custom": "Header"
    }
    response = svc.send_message("GET", 'test get', 'http://my.url/',
                                headers=expect_headers)
    mock_request.assert_called_once_with('GET', 'http://my.url/',
                                         headers=expect_headers, verify=False,
                                         proxies=None)
    assert response == mocked_response

@mock.patch.object(OnapService, '_set_basic_auth_if_needed')
@mock.patch.object(Session, 'request')
def test_send_message_with_basic_auth(mock_request, mock_set_basic_auth_if_needed):
    """Should give response of request if OK."""
    svc = OnapService()
    mocked_response = Response()
    mocked_response.status_code = 200
    basic_auth = {'username': 'user1', "password": "password1"}
    mock_request.return_value = mocked_response
    expect_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Once": "Upon a time"
    }
    response = svc.send_message("GET", 'test get', 'http://my.url/',
                                headers=expect_headers, basic_auth=basic_auth)
    mock_set_basic_auth_if_needed.assert_called_once_with(basic_auth, ANY)
    mock_request.assert_called_once_with('GET', 'http://my.url/',
                                         headers=expect_headers, verify=False,
                                         proxies=None)
    assert response == mocked_response

@mock.patch.object(Session, 'request')
def test_send_message_resource_not_found(mock_request):
    """Should raise ResourceNotFound if status code 404."""
    svc = OnapService()

    mocked_response = Response()
    mocked_response.status_code = 404

    mock_request.return_value = mocked_response

    with pytest.raises(ResourceNotFound) as exc:
        svc.send_message("GET", 'test get', 'http://my.url/')
    assert exc.type is ResourceNotFound

    mock_request.assert_called_once()

@mock.patch.object(Session, 'request')
@pytest.mark.parametrize("code", http_codes())
def test_send_message_api_error(mock_request, code):
    """Raise APIError if status code is between 400 and 599, and not 404."""
    svc = OnapService()
    mocked_response = Response()
    mocked_response.status_code = code
    mock_request.return_value = mocked_response

    with pytest.raises(APIError) as exc:
        svc.send_message("GET", 'test get', 'http://my.url/')
    assert exc.type is APIError

    mock_request.assert_called_once()

@mock.patch.object(Session, 'request')
def test_send_message_connection_failed(mock_request):
    """Should raise ResourceNotFound if status code 404."""
    svc = OnapService()

    mock_request.side_effect = ConnectionError

    with pytest.raises(ConnectionFailed) as exc:
        svc.send_message("GET", 'test get', 'http://my.url/')
    assert exc.type is ConnectionFailed

    mock_request.assert_called_once()

@mock.patch.object(Session, 'request')
def test_send_message_request_error(mock_request):
    """Should raise RequestError for an amiguous request exception."""
    svc = OnapService()

    mock_request.side_effect = RequestException

    with pytest.raises(RequestError) as exc:
        svc.send_message("GET", 'test get', 'http://my.url/')
    assert exc.type is RequestError

    mock_request.assert_called_once()


@mock.patch.object(Session, 'request')
def test_send_message_custom_error(mock_request):
    """Should raise RequestError for an amiguous request exception."""
    svc = OnapService()

    mock_request.side_effect = RequestException

    with pytest.raises(TestException) as exc:
        svc.send_message("GET", 'test get', 'http://my.url/',
                         exception=TestException)
    assert exc.type is TestException

    mock_request.assert_called_once()

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_OK(mock_send):
    """JSON is received and successfully decoded."""
    svc = OnapService()

    mocked_response = Response()
    mocked_response._content = b'{"yolo": "yala"}'
    mocked_response.encoding = "UTF-8"
    mocked_response.status_code = 200

    mock_send.return_value = mocked_response

    response = svc.send_message_json("GET", 'test get', 'http://my.url/')

    mock_send.assert_called_once_with("GET", 'test get', 'http://my.url/')
    assert response['yolo'] == 'yala'

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_invalid_response(mock_send):
    """Raises InvalidResponse if response is not JSON."""
    svc = OnapService()

    mocked_response = Response()
    mocked_response._content = b'{yolo}'
    mocked_response.encoding = "UTF-8"
    mocked_response.status_code = 200

    mock_send.return_value = mocked_response

    with pytest.raises(InvalidResponse) as exc:
        svc.send_message_json("GET", 'test get', 'http://my.url/')
    assert exc.type is InvalidResponse

    mock_send.assert_called_once()

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_connection_failed(mock_send):
    """ConnectionFailed from send_message is handled."""
    svc = OnapService()

    mock_send.side_effect = ConnectionFailed

    with pytest.raises(ConnectionFailed) as exc:
        svc.send_message_json("GET", 'test get', 'http://my.url/')
    assert exc.type is ConnectionFailed

    mock_send.assert_called_once()

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_api_error(mock_send):
    """APIError (error codes) from send_message is handled."""
    svc = OnapService()

    mock_send.side_effect = APIError

    with pytest.raises(APIError) as exc:
        svc.send_message_json("GET", 'test get', 'http://my.url/')
    assert exc.type is APIError

    mock_send.assert_called_once()

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_resource_not_found(mock_send):
    """ResourceNotFound exception from send_message is handled."""
    svc = OnapService()

    mock_send.side_effect = ResourceNotFound

    with pytest.raises(ResourceNotFound) as exc:
        svc.send_message_json("GET", 'test get', 'http://my.url/')
    assert exc.type is ResourceNotFound

    mock_send.assert_called_once()

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_request_error(mock_send):
    """RequestError exception from send_message is handled."""
    svc = OnapService()

    mock_send.side_effect = RequestError

    with pytest.raises(RequestError) as exc:
        svc.send_message_json("GET", 'test get', 'http://my.url/')
    assert exc.type is RequestError

    mock_send.assert_called_once()


@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_custom_error(mock_send):
    """RequestError exception from send_message is handled."""
    svc = OnapService()

    mock_send.side_effect = RequestError

    with pytest.raises(TestException) as exc:
        svc.send_message_json("GET", 'test get', 'http://my.url/',
                              exception=TestException)
    assert exc.type is TestException

    mock_send.assert_called_once()
