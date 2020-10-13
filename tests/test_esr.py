from unittest import mock

import pytest

from onapsdk.msb.esr import ESR, MSB


def test_esr():
    esr = ESR()
    assert esr.base_url == f"{MSB.base_url}/api/aai-esr-server/v1/vims"


@mock.patch.object(ESR, "send_message")
def test_est_register_vim(mock_esr_send_message):
    ESR.register_vim(
        "test_cloud_owner",
        "test_cloud_region_id",
        "test_cloud_type",
        "test_cloud_region_version",
        "test_auth_info_cloud_domain",
        "test_auth_info_username",
        "test_auth_info_password",
        "test_auth_info_url"
    )
    mock_esr_send_message.assert_called_once()
    method, _, url = mock_esr_send_message.call_args[0]
    assert method == "POST"
    assert url == ESR.base_url
