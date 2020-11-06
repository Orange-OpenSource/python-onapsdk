#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test OnapService module."""
from unittest import mock
from unittest.mock import ANY

import pytest
from jinja2 import Environment
from requests import Response, Timeout, Session

from onapsdk.onap_service import OnapService
from onapsdk.sdc.vendor import Vendor

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
def test_send_message_error_400_no_exception(mock_request):
    """Should give back None if issues on request."""
    svc = OnapService()
    mocked_response = Response()
    mocked_response.status_code = 400
    mock_request.return_value = mocked_response
    response = svc.send_message("GET", 'test get', 'http://my.url/')
    expect_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    mock_request.assert_called_once_with('GET', 'http://my.url/',
                                         headers=expect_headers, verify=False,
                                         proxies=None)
    assert response == None

@mock.patch.object(Session, 'request')
def test_send_message_error_400_exception(mock_request):
    """Should raise Exception given if issues on request."""
    with pytest.raises(KeyError):
        svc = OnapService()
        mocked_response = Response()
        mocked_response.status_code = 400
        mock_request.return_value = mocked_response
        expect_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = svc.send_message("GET", 'test get', 'http://my.url/',
                                    exception=KeyError)
        mock_request.assert_called_once_with('GET', 'http://my.url/',
                                             headers=expect_headers,
                                             verify=False, proxies=None)

@mock.patch.object(Session, 'request')
def test_send_message_error_timeout_no_exception(mock_request):
    """Should return None given if issues on request."""
    svc = OnapService()
    mock_request.side_effect = Timeout()
    response = svc.send_message("GET", 'test get', 'http://my.url/')
    expect_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    mock_request.assert_called_once_with('GET', 'http://my.url/',
                                         headers=expect_headers, verify=False,
                                         proxies=None)
    assert response == None

@mock.patch.object(Session, 'request')
def test_send_message_error_timeout_exception(mock_request):
    """Should raise Exception given if issues on request."""
    with pytest.raises(KeyError):
        svc = OnapService()
        mock_request.side_effect = Timeout()
        response = svc.send_message("GET", 'test get', 'http://my.url/',
                                    exception=KeyError)
        expect_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        mock_request.assert_called_once_with('GET', 'http://my.url/',
                                             headers=expect_headers,
                                             verify=False, proxies=None)

@mock.patch.object(Session, 'request')
def test_send_message_OK(mock_request):
    """Should give response of request if OK."""
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
def test_send_message_specific_headers_OK(mock_request):
    """Should give response of request if OK."""
    svc = OnapService()
    mocked_response = Response()
    mocked_response.status_code = 200
    mock_request.return_value = mocked_response
    expect_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Once": "Upon a time"
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

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_bad_send_no_exception(mock_send):
    svc = OnapService()
    mock_send.return_value = None
    response = svc.send_message_json("GET", 'test get', 'http://my.url/')
    mock_send.assert_called_once_with("GET", 'test get', 'http://my.url/')
    assert response == {}

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_bad_send_exception(mock_send):
    with pytest.raises(Timeout):
        svc = OnapService()
        mock_send.side_effect = Timeout
        response = svc.send_message_json("GET", 'test get', 'http://my.url/', exception=Timeout)
        mock_send.assert_called_once_with("GET", 'test get', 'http://my.url/', exception=Timeout)

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_bad_json_no_exception(mock_send):
    svc = OnapService()
    mocked_response = Response()
    mocked_response._content = b'yolo'
    mocked_response.encoding = "UTF-8"
    mocked_response.status_code = 200
    mock_send.return_value = mocked_response
    response = svc.send_message_json("GET", 'test get', 'http://my.url/')
    mock_send.assert_called_once_with("GET", 'test get', 'http://my.url/')
    assert response == {}

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_bad_json_no_exception(mock_send):
    with pytest.raises(Timeout):
        svc = OnapService()
        mocked_response = Response()
        mocked_response._content = b'yolo'
        mocked_response.encoding = "UTF-8"
        mocked_response.status_code = 200
        mock_send.return_value = mocked_response
        response = svc.send_message_json("GET", 'test get', 'http://my.url/', exception=Timeout)
        mock_send.assert_called_once_with("GET", 'test get', 'http://my.url/', exception=Timeout)

@mock.patch.object(OnapService, 'send_message')
def test_send_message_json_OK(mock_send):
    svc = OnapService()
    mocked_response = Response()
    mocked_response._content = b'{"yolo": "yala"}'
    mocked_response.encoding = "UTF-8"
    mocked_response.status_code = 200
    mock_send.return_value = mocked_response
    response = svc.send_message_json("GET", 'test get', 'http://my.url/')
    mock_send.assert_called_once_with("GET", 'test get', 'http://my.url/')
    assert response['yolo'] == 'yala'
