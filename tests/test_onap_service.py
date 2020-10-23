#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test OnapService module."""
from unittest import mock

import pytest
from jinja2 import Environment
from requests import Response, Timeout, Session
import simplejson.errors
from onapsdk.exceptions import (
    SDKException, RequestError, APIError, ResourceNotFound, InvalidResponse
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

@mock.patch.object(Session, 'request')
def test_send_message_200(mock_request):
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
def test_send_message_custom_header_200(mock_request):
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

@mock.patch.object(Session, 'request')
def test_send_message_404(mock_request):
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

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_invalid_response(mock_send):
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
def test_send_message_connection_failed(mock_send):
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
