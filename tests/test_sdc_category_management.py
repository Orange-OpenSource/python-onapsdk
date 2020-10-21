#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcElement module."""
from unittest import mock

from onapsdk.sdc.category_management import ResourceCategory, ServiceCategory


@mock.patch.object(ResourceCategory, "send_message_json")
def test_resource_category_create(mock_send_message_json):

    test_name = "test_name"
    rc = ResourceCategory.create(name=test_name)
    assert rc.name == test_name


@mock.patch.object(ServiceCategory, "send_message_json")
def test_service_category_create(mock_send_message_json):

    test_name = "test_name"
    sc = ServiceCategory.create(name=test_name)
    assert sc.name == test_name
