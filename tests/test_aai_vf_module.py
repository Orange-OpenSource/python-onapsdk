from unittest import mock

import pytest

from onapsdk.aai.business import VfModuleInstance
from onapsdk.so.deletion import VfModuleDeletionRequest
from onapsdk.exceptions import ResourceNotFound


COUNT = {
    "results":[
        {
            "vf-module":1
        }
    ]
}


def test_vf_module():
    vnf_instance = mock.MagicMock()
    vnf_instance.url = "test_url"
    vf_module_instance = VfModuleInstance(vnf_instance=vnf_instance,
                                          vf_module_id="test_vf_module_id",
                                          is_base_vf_module=True,
                                          automated_assignment=False)

    assert vf_module_instance.url == (f"{vf_module_instance.vnf_instance.url}/vf-modules/"
                                      f"vf-module/{vf_module_instance.vf_module_id}")


@mock.patch.object(VfModuleDeletionRequest, "send_request")
def test_vf_module_deletion(mock_deletion_request):
    vf_module_instance = VfModuleInstance(vnf_instance=mock.MagicMock(),
                                          vf_module_id="test_vf_module_id",
                                          is_base_vf_module=True,
                                          automated_assignment=False)
    vf_module_instance.delete()
    mock_deletion_request.assert_called_once_with(vf_module_instance, True)


def test_vnf_vf_module():
    """Test VfModudleInstance's vf_module property"""
    vnf_instance = mock.MagicMock()
    vnf_instance.vnf = mock.MagicMock()

    vf_module = mock.MagicMock()
    vf_module.model_version_id = "test_model_version_id"

    vf_module_instance = VfModuleInstance(vnf_instance=vnf_instance,
                                          model_version_id="test_model_version_id",
                                          vf_module_id="test_vf_module_id",
                                          is_base_vf_module=True,
                                          automated_assignment=False)

    vnf_instance.vnf.vf_modules = []
    with pytest.raises(ResourceNotFound) as exc:
        vf_module_instance.vf_module
    assert exc.type == ResourceNotFound
    assert vf_module_instance._vf_module is None

    vnf_instance.vnf.vf_modules = [vf_module]

    assert vf_module == vf_module_instance.vf_module
    assert vf_module_instance._vf_module is not None
    assert vf_module_instance.vf_module == vf_module_instance._vf_module

@mock.patch.object(VfModuleInstance, "send_message_json")
def test_vf_module_instance_count(mock_send_message_json):
    mock_send_message_json.return_value = COUNT
    assert VfModuleInstance.count(vnf_instance=mock.MagicMock()) == 1
