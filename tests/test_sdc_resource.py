#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcResource module."""
import mock
import pytest
import logging

import onapsdk.constants as const
from onapsdk.onap_service import OnapService
from onapsdk.sdc_resource import SdcResource
from onapsdk.vf import Vf
from onapsdk.utils.headers_creator import headers_sdc_tester
from onapsdk.utils.headers_creator import headers_sdc_creator


def test_init():
    """Test the initialization."""
    element = SdcResource()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert SdcResource.server == "SDC"
    assert SdcResource.base_front_url == "https://sdc.api.fe.simpledemo.onap.org:30207"
    assert SdcResource.base_back_url == "https://sdc.api.be.simpledemo.onap.org:30204"
    assert SdcResource.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__get_item_details_not_created(mock_send, mock_created):
    vf = Vf()
    mock_created.return_value = False
    assert vf._get_item_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'send_message_json')
def test__get_item_details_created(mock_send):
    vf = Vf()
    vf.identifier = "1234"
    mock_send.return_value = {'return': 'value'}
    assert vf._get_item_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item', "{}/items/1234/versions".format(vf._base_url()))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details_not_created(mock_send, mock_created):
    vf = Vf()
    mock_created.return_value = False
    assert vf._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details_no_version(mock_send, mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details(mock_send):
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "4567"
    mock_send.return_value = {'return': 'value'}
    assert vf._get_item_version_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item version', "{}/items/1234/versions/4567".format(vf._base_url()))

@mock.patch.object(Vf, 'load')
def test__unique_uuid_no_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    vf._unique_uuid = "4567"
    assert vf.unique_uuid == "4567"
    mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
def test__unique_uuid_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf.unique_uuid == None
    mock_load.assert_called_once()

def test__unique_uuid_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.unique_uuid = "4567"
    assert vf._unique_uuid == "4567"

@mock.patch.object(Vf, 'deep_load')
def test__unique_identifier_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf.unique_identifier == None
    mock_load.assert_called_once()

@mock.patch.object(Vf, 'deep_load')
def test__unique_identifier_no_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    vf._unique_identifier= "toto"
    assert vf.unique_identifier == "toto"
    mock_load.assert_not_called()

def test__status_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.status = "4567"
    assert vf._status == "4567"

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_no_response(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.return_value = {}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url),
                                      headers=headers_sdc_creator(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_OK(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5689"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf.unique_identifier == "71011"
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url),
                                      headers=headers_sdc_creator(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_NOK(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5678"
    vf._version = "4567"
    vf._status = const.CHECKED_IN
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url),
                                      headers=headers_sdc_creator(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_OK_under_cert(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5689"
    vf._version = "4567"
    vf._status = const.UNDER_CERTIFICATION
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf.unique_identifier == "71011"
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url),
                                      headers=headers_sdc_tester(vf.headers))

@mock.patch.object(Vf, 'created')
@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_NOK_under_cert(mock_send, mock_created):
    mock_created.return_value = True
    vf = Vf()
    vf.identifier = "5678"
    vf._version = "4567"
    vf._status = const.UNDER_CERTIFICATION
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf',
                                      "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url),
                                      headers=headers_sdc_tester(vf.headers))

def test__parse_sdc_status_certified():
    assert SdcResource._parse_sdc_status("CERTIFIED", None, logging.getLogger()) == const.CERTIFIED

def test__parse_sdc_status_certified_not_approved():
    assert SdcResource._parse_sdc_status("CERTIFIED",
                                         const.DISTRIBUTION_NOT_APPROVED,
                                         logging.getLogger()) == const.CERTIFIED

def test__parse_sdc_status_approved():
    assert SdcResource._parse_sdc_status("CERTIFIED",
                                         const.DISTRIBUTION_APPROVED,
                                         logging.getLogger()) == const.APPROVED

def test__parse_sdc_status_distributed():
    assert SdcResource._parse_sdc_status("CERTIFIED", const.SDC_DISTRIBUTED,
                                         logging.getLogger()) == const.DISTRIBUTED

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status(const.NOT_CERTIFIED_CHECKOUT, None,
                                         logging.getLogger() ) == const.DRAFT

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status(const.NOT_CERTIFIED_CHECKIN, None,
                                         logging.getLogger() ) == const.CHECKED_IN

def test__parse_sdc_status_submitted():
    assert SdcResource._parse_sdc_status(const.READY_FOR_CERTIFICATION, None,
                                         logging.getLogger() ) == const.SUBMITTED

def test__parse_sdc_status_under_certification():
    assert SdcResource._parse_sdc_status(const.CERTIFICATION_IN_PROGRESS, None,
                                         logging.getLogger() ) == const.UNDER_CERTIFICATION

def test__parse_sdc_status_unknown():
    assert SdcResource._parse_sdc_status("UNKNOWN", None, logging.getLogger() ) == 'UNKNOWN'

def test__parse_sdc_status_empty():
    assert SdcResource._parse_sdc_status("", None, logging.getLogger() ) is None

def test__really_submit():
    sdcResource = SdcResource()
    with pytest.raises(NotImplementedError):
        sdcResource._really_submit()

def test__action_url_no_action_type():
    sdcResource = SdcResource()
    url = sdcResource._action_url("base", "subpath", "version_path")
    assert url == "base/resources/version_path/lifecycleState/subpath"

def test__action_url_action_type():
    sdcResource = SdcResource()
    url = sdcResource._action_url("base", "subpath", "version_path",
                                  action_type="distribution")
    assert url == "base/resources/version_path/distribution/subpath"

@mock.patch.object(SdcResource, '_parse_sdc_status')
def test_update_informations_from_sdc_creation_no_distribitution_state(mock_parse):
    mock_parse.return_value = "12"
    sdcResource = SdcResource()
    details = {'invariantUUID': '1234',
               'lifecycleState': 'state',
               'version': 'v12',
               'uniqueId': '5678'}

    sdcResource.update_informations_from_sdc_creation(details)
    assert sdcResource.unique_uuid == "1234"
    assert sdcResource.status == "12"
    assert sdcResource.version == "v12"
    assert sdcResource.unique_identifier == "5678"
    mock_parse.assert_called_once_with("state", None, mock.ANY)

@mock.patch.object(SdcResource, '_parse_sdc_status')
def test_update_informations_from_sdc_creation_distribitution_state(mock_parse):
    mock_parse.return_value = "bgt"
    sdcResource = SdcResource()
    details = {'invariantUUID': '1234',
               'lifecycleState': 'state',
               'distributionStatus': 'trez',
               'version': 'v12',
               'uniqueId': '5678'}

    sdcResource.update_informations_from_sdc_creation(details)
    assert sdcResource.unique_uuid == "1234"
    assert sdcResource.status == "bgt"
    assert sdcResource.version == "v12"
    assert sdcResource.unique_identifier == "5678"
    mock_parse.assert_called_once_with("state", 'trez', mock.ANY)
