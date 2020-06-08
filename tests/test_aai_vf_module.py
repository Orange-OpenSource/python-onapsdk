from unittest import mock

import pytest

from onapsdk.aai.business import VfModuleInstance
from onapsdk.so.deletion import VfModuleDeletionRequest


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
    mock_deletion_request.assert_called_once_with(vf_module_instance)
    