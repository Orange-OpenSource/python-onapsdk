from unittest import mock

import pytest

from onapsdk.so.so_element import OrchestrationRequest
from onapsdk.so.deletion import (
    ServiceDeletionRequest,
    VfModuleDeletionRequest,
    VnfDeletionRequest
)


@mock.patch.object(ServiceDeletionRequest, "send_message")
def test_service_deletion_request(mock_send_message):
    mock_instance = mock.MagicMock()
    mock_instance.instance_id = "test_instance_id"
    ServiceDeletionRequest.send_request(instance=mock_instance)
    mock_send_message.assert_called_once()
    method, _, url = mock_send_message.call_args[0]
    assert method == "DELETE"
    assert url == (f"{ServiceDeletionRequest.base_url}/onap/so/infra/"
                   f"serviceInstantiation/{ServiceDeletionRequest.api_version}/"
                   "serviceInstances/test_instance_id")


@mock.patch.object(VfModuleDeletionRequest, "send_message")
def test_vf_module_deletion_request(mock_send_message):
    mock_vf_module_instance = mock.MagicMock()
    mock_vf_module_instance.vf_module_id = "test_vf_module_id"

    mock_vnf_instance = mock.MagicMock()
    mock_vnf_instance.vnf_id = "test_vnf_id"
    mock_vf_module_instance.vnf_instance = mock_vnf_instance

    mock_service_instance = mock.MagicMock()
    mock_service_instance.instance_id = "test_service_instance_id"
    mock_vnf_instance.service_instance = mock_service_instance

    VfModuleDeletionRequest.send_request(instance=mock_vf_module_instance)
    mock_send_message.assert_called_once()
    method, _, url = mock_send_message.call_args[0]
    assert method == "DELETE"
    assert url == (f"{VfModuleDeletionRequest.base_url}/onap/so/infra/"
                   f"serviceInstantiation/{VfModuleDeletionRequest.api_version}/"
                   "serviceInstances/test_service_instance_id/"
                   "vnfs/test_vnf_id/vfModules/test_vf_module_id")


@mock.patch.object(VnfDeletionRequest, "send_message")
def test_vnf_deletion_request(mock_send_message):
    mock_vnf_instance = mock.MagicMock()
    mock_vnf_instance.vnf_id = "test_vnf_id"

    mock_service_instance = mock.MagicMock()
    mock_service_instance.instance_id = "test_service_instance"
    mock_vnf_instance.service_instance = mock_service_instance

    VnfDeletionRequest.send_request(instance=mock_vnf_instance)
    mock_send_message.assert_called_once()
    method, _, url = mock_send_message.call_args[0]
    assert method == "DELETE"
    assert url == (f"{VnfDeletionRequest.base_url}/onap/so/infra/"
                   f"serviceInstantiation/{VnfDeletionRequest.api_version}/"
                   "serviceInstances/test_service_instance/"
                   "vnfs/test_vnf_id")
