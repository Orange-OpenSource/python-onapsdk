from unittest import mock

import pytest

from onapsdk.aai.business import Customer, ServiceSubscription, ServiceInstance
from onapsdk.sdc.service import Service as SdcService


SERVICE_INSTANCES = {
    "service-instance":[
        {
            "service-instance-id":"5410bf79-2aa3-450e-a324-ec5630dc18cf",
            "service-instance-name":"test",
            "environment-context":"General_Revenue-Bearing",
            "workload-context":"Production",
            "model-invariant-id":"2a51a89b-6f94-4417-8831-c468fb30ed02",
            "model-version-id":"92a82807-b483-4579-86b1-c79b1286aab4",
            "resource-version":"1589457727708",
            "orchestration-status":"Active",
            "relationship-list":{
                "relationship":[
                    {
                        "related-to":"owning-entity",
                        "relationship-label":"org.onap.relationships.inventory.BelongsTo",
                        "related-link":"/aai/v16/business/owning-entities/owning-entity/ff6c945f-89ab-4f14-bafd-0cdd6eac791a",
                        "relationship-data":[
                            {
                                "relationship-key":"owning-entity.owning-entity-id",
                                "relationship-value":"ff6c945f-89ab-4f14-bafd-0cdd6eac791a"
                            }
                        ]
                    },
                    {
                        "related-to":"project",
                        "relationship-label":"org.onap.relationships.inventory.Uses",
                        "related-link":"/aai/v16/business/projects/project/python_onap_sdk_project",
                        "relationship-data":[
                            {
                                "relationship-key":"project.project-name",
                                "relationship-value":"python_onap_sdk_project"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}


@mock.patch.object(ServiceSubscription, "send_message_json")
def test_get_service_instance_by_filter_parameter(mock_send_message_json):
    """Test Service Subscription get_service_instance_by_filter_parameter method"""
    customer = Customer("generic", "generic", "INFRA")
    service_subscription = ServiceSubscription(customer=customer,
                                               service_type="test_service_type",
                                               resource_version="test_resource_version")
    mock_send_message_json.return_value = SERVICE_INSTANCES
    service_instance = service_subscription._get_service_instance_by_filter_parameter(filter_parameter_name="service-instance-id", filter_parameter_value="5410bf79-2aa3-450e-a324-ec5630dc18cf")
    assert service_instance.instance_name == "test"
    assert service_instance.instance_id == "5410bf79-2aa3-450e-a324-ec5630dc18cf"


@mock.patch.object(ServiceSubscription, "_get_service_instance_by_filter_parameter")
def test_get_service_instance_by_id(mock_get):
    """Test Service Subscription get_service_instance_by_id method"""
    service_subscription = ServiceSubscription(customer=None,
                                               service_type="test_service_type",
                                               resource_version="test_resource_version")
    mock_get.return_value = ServiceInstance(service_subscription="ServiceSubscription",
                                            instance_id="5410bf79-2aa3-450e-a324-ec5630dc18cf")
    service_instance = service_subscription.get_service_instance_by_id(service_instance_id="5410bf79-2aa3-450e-a324-ec5630dc18cf")
    assert service_instance.instance_id == "5410bf79-2aa3-450e-a324-ec5630dc18cf"


@mock.patch.object(ServiceSubscription, "_get_service_instance_by_filter_parameter")
def test_get_service_instance_by_name(mock_get):
    """Test Service Subscription get_service_instance_by_name method"""
    service_subscription = ServiceSubscription(customer=None,
                                               service_type="test_service_type",
                                               resource_version="test_resource_version")
    mock_get.return_value = ServiceInstance(service_subscription="ServiceSubscription",
                                            instance_id="5410bf79-2aa3-450e-a324-ec5630dc18cf",
                                            instance_name="test")
    service_instance = service_subscription.get_service_instance_by_name(service_instance_name="test")
    assert service_instance.instance_name == "test"


def test_sdc_service_subscription():
    """Test service subscription sdc property"""
    service_subscription = ServiceSubscription(customer=None,
                                               service_type="test_service_type",
                                               resource_version="test_resource_version")  
    assert service_subscription.sdc_service == SdcService("test_service_type")
