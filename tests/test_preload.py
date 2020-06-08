from unittest import mock

import pytest

from onapsdk.sdnc.preload import VfModulePreload


@mock.patch.object(VfModulePreload, "send_message_json")
def test_vf_module_preload_vnf_api(mock_send_message_json):
    VfModulePreload.upload_vf_module_preload(vnf_instance=mock.MagicMock(),
                                             vf_module_instance_name="test",
                                             vf_module=mock.MagicMock(),
                                             use_vnf_api=True)
    mock_send_message_json.assert_called_once()
    method, description, url = mock_send_message_json.call_args[0]
    assert method == "POST"
    assert description == "Upload VF module preload using VNF-API"
    assert url == (f"{VfModulePreload.base_url}/restconf/operations/"
                   "VNF-API:preload-vnf-topology-operation")


@mock.patch.object(VfModulePreload, "send_message_json")
def test_vf_module_preload_gr_api(mock_send_message_json):
    VfModulePreload.upload_vf_module_preload(vnf_instance=mock.MagicMock(),
                                             vf_module_instance_name="test",
                                             vf_module=mock.MagicMock(),
                                             use_vnf_api=False)
    mock_send_message_json.assert_called_once()
    method, description, url = mock_send_message_json.call_args[0]
    assert method == "POST"
    assert description == "Upload VF module preload using GENERIC-RESOURCE-API"
    assert url == (f"{VfModulePreload.base_url}/restconf/operations/"
                   "GENERIC-RESOURCE-API:preload-vf-module-topology-operation")
