from unittest import mock

import pytest

from onapsdk.multicloud import Multicloud


@mock.patch.object(Multicloud, "send_message")
def test_multicloud_register(mock_send_message):
    Multicloud.register_vim(cloud_owner="test_cloud_owner",
                            cloud_region_id="test_cloud_region")
    mock_send_message.assert_called_once()
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "Register VIM instance to ONAP"
    assert url == f"{Multicloud.base_url}/test_cloud_owner/test_cloud_region/registry"


@mock.patch.object(Multicloud, "send_message")
def test_multicloud_unregister(mock_send_message):
    Multicloud.unregister_vim(cloud_owner="test_cloud_owner",
                              cloud_region_id="test_cloud_region")
    mock_send_message.assert_called_once()
    method, description, url = mock_send_message.call_args[0]
    assert method == "DELETE"
    assert description == "Unregister VIM instance from ONAP"
    assert url == f"{Multicloud.base_url}/test_cloud_owner/test_cloud_region"
