from unittest import mock

import pytest

from onapsdk.aai.business import ServiceInstance, VnfInstance
from onapsdk.so.deletion import ServiceDeletionRequest
from onapsdk.so.instantiation import VnfInstantiation


RELATIONSHIPS = {
    "relationship": [
        {
            "related-to": "generic-vnf",
            "relationship_label": "anything",
            "related_link": "test_relationship_related_link",
            "relationship_data": []
        }
    ]
}


def test_service_instance():
    service_subscription = mock.MagicMock()
    service_subscription.url = "test_url"
    service_instance = ServiceInstance(service_subscription=service_subscription,
                                       instance_id="test_service_instance_id")
    assert service_instance.url == (f"{service_instance.service_subscription.url}/service-instances/"
                                    f"service-instance/{service_instance.instance_id}")


@mock.patch.object(ServiceInstance, "send_message_json")
def test_service_instance_vnf_instances(mock_relationships_send_message_json):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    mock_relationships_send_message_json.return_value = {"relationship": []}
    assert len(list(service_instance.vnf_instances)) == 0
    mock_relationships_send_message_json.return_value = RELATIONSHIPS
    assert len(list(service_instance.vnf_instances)) == 1


@mock.patch.object(VnfInstantiation, "instantiate_ala_carte")
def test_service_instance_add_vnf(mock_vnf_instantiation):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    service_instance.orchestration_status = "Inactive"
    with pytest.raises(AttributeError):
        service_instance.add_vnf(mock.MagicMock(),
                                 mock.MagicMock(),
                                 mock.MagicMock())
    service_instance.orchestration_status = "Active"
    service_instance.add_vnf(mock.MagicMock(),
                             mock.MagicMock(),
                             mock.MagicMock())
    mock_vnf_instantiation.assert_called_once()


@mock.patch.object(ServiceDeletionRequest, "send_request")
def test_service_instance_deletion(mock_service_deletion_request):
    service_instance = ServiceInstance(service_subscription=mock.MagicMock(),
                                       instance_id="test_service_instance_id")
    service_instance.delete()
    mock_service_deletion_request.assert_called_once_with(service_instance)
