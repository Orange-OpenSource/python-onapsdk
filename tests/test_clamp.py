#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test clamp module."""

from unittest import mock
from unittest.mock import MagicMock
import os
import json
import pytest

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.clamp.loop_instance import LoopInstance
from onapsdk.exceptions import ParameterError, ResourceNotFound
from onapsdk.sdc.service import Service

#examples
TEMPLATES = [
    {
        "name" : "test_template",
        "modelService" : {
            "serviceDetails" : {
                "name" : "test"
            }
        }
    }
]

POLICIES = [
    {
        "policyModelType" : "onap.policies.controlloop.Test",
        "version" : "1.0.0",
        "policyAcronym" : "Test",
        "createdDate" : "2020-04-30T09:03:30.362897Z",
        "updatedDate" : "2020-04-30T09:03:30.362897Z",
        "updatedBy" : "Not found",
        "createdBy" : "Not found"
    }
]

LOOP_DETAILS = {
    "name" : "LOOP_test",
    "globalPropertiesJson": {
        "dcaeDeployParameters" : {
            "uniqueBlueprintParameters" : {
                "policy_id" : "Microservice12345"
            }
        }
    },
    "components" : {
        "POLICY" : {
            "componentState" : {
                "stateName" : "UNKNOWN"
            }
        },
        "DCAE" : {
            "componentState" : {
                "stateName" : "BLUEPRINT_DEPLOYED"
            }
        }
    },
    "modelService" : {
        "resourceDetails": {
            "VFModule" : {
                "resourceID" : {
                    "vfModuleModelName" : "resourceID",
                    "vfModuleModelInvariantUUID" : "InvariantUUID",
                    "vfModuleModelUUID" : "UUID",
                    "vfModuleModelVersion" : "1.0",
                    "vfModuleModelCustomizationUUID" : "CustomizationUUID"
                }
            }
        }
    },
    "operationalPolicies" : [
        {
            "name" : "MICROSERVICE_test"
        }
    ],
    "microServicePolicies" : [
        {
            "name" : "MICROSERVICE_test"
        }
    ]
}

#for policy deploy to policy engine
SUBMITED_POLICY = {
        "components" : {
        "POLICY" : {
            "componentState" : {
                "stateName" : "SENT_AND_DEPLOYED"
            }
        }
    }
}

NOT_SUBMITED_POLICY = {
        "components" : {
        "POLICY" : {
            "componentState" : {
                "stateName" : "SENT"
            }
        }
    }
}

#for the deploy to DCAE
SUBMITED = {
        "components" : {
        "DCAE" : {
            "componentState" : {
                "stateName" : "MICROSERVICE_INSTALLED_SUCCESSFULLY"
            }
        }
    }
}

NOT_SUBMITED = {
        "components" : {
        "DCAE" : {
            "componentState" : {
                "stateName" : "MICROSERVICE_INSTALLATION_FAILED"
            }
        }
    }
}
#end of examples


def test_initialization():
    """Class initialization test."""
    clamp = Clamp()
    assert isinstance(clamp, Clamp)


@mock.patch.object(Clamp, 'send_message_json')
def test_check_loop_template(mock_send_message_json):
    """Test Clamp's class method."""
    svc = Service(name='test')
    mock_send_message_json.return_value = TEMPLATES
    template = Clamp.check_loop_template(service=svc)
    mock_send_message_json.assert_called_once_with('GET',
                                                   'Get Loop Templates',
                                                   (f"{Clamp.base_url()}/templates/"),
                                                   cert=Clamp.cert)
    assert template == "test_template"


@mock.patch.object(Clamp, 'send_message_json')
def test_check_loop_template_none(mock_send_message_json):
    """Test Clamp's class method."""
    svc = Service(name='test')
    mock_send_message_json.return_value = {}
    with pytest.raises(ResourceNotFound) as exc:
        template = Clamp.check_loop_template(service=svc)
        assert template is None
    assert exc.type is ResourceNotFound


@mock.patch.object(Clamp, 'send_message_json')
def test_check_policies(mock_send_message_json):
    mock_send_message_json.return_value = POLICIES
    exists = Clamp.check_policies(policy_name="Test", req_policies=1)
    mock_send_message_json.\
        assert_called_once_with('GET',
                                'Get stocked policies',
                                (f"{Clamp.base_url()}/policyToscaModels/"),
                                cert=Clamp.cert)
    assert exists


@mock.patch.object(Clamp, 'send_message_json')
def test_check_policies_none(mock_send_message_json):
    mock_send_message_json.return_value = POLICIES
    exists = Clamp.check_policies(policy_name="Test")
    mock_send_message_json.\
            assert_called_once_with('GET',
                                    'Get stocked policies',
                                    (f"{Clamp.base_url()}/policyToscaModels/"),
                                    cert=Clamp.cert)
    assert not exists


def test_cl_initialization():
    """Class initialization test."""
    loop = LoopInstance(template="template", name="LOOP_name", details={})
    assert isinstance(loop, LoopInstance)


@mock.patch.object(LoopInstance, '_update_loop_details')
def test_details(mock_update):
    """Test loop instace details gette."""
    loop = LoopInstance(template="template", name="LOOP_name", details={})
    mock_update.return_value = {"name" : "test"}
    details = loop.details
    assert details == {}


@mock.patch.object(LoopInstance, 'send_message_json')
def test_update_loop_details(mock_send_message_json):
    """Test Loop instance methode."""
    loop = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = LOOP_DETAILS
    loop.details = loop._update_loop_details()
    mock_send_message_json.assert_called_once_with('GET', 'Get loop details',
         (f"{loop.base_url()}/loop/LOOP_test"),
         cert=loop.cert)
    assert loop.details == LOOP_DETAILS


@mock.patch.object(LoopInstance, 'send_message_json')
def test_refresh_status(mock_send_message_json):
    """Test Loop instance methode."""
    loop = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = LOOP_DETAILS
    loop.refresh_status()
    mock_send_message_json.assert_called_once_with('GET', 'Get loop status',
         (f"{loop.base_url()}/loop/getstatus/LOOP_test"),
         cert=loop.cert)
    assert loop.details == LOOP_DETAILS


@mock.patch.object(LoopInstance, 'send_message_json')
def test_refresh_status_error(mock_send_message_json):
    """Test Loop instance methode."""
    loop = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = {}
    with pytest.raises(ParameterError) as exc:       
        loop.refresh_status()
        mock_send_message_json.assert_called_once_with('GET', 'Get loop status',
            (f"{loop.base_url()}/loop/getstatus/LOOP_test"),
            cert=loop.cert)
        assert loop.details == {}
    assert exc.type is ParameterError


@mock.patch.object(LoopInstance, 'send_message_json')
def test_not_update_loop_details(mock_send_message_json):
    """Test Loop instance update details."""
    loop = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = {}
    with pytest.raises(ResourceNotFound) as exc:
        loop._update_loop_details()
        mock_send_message_json.assert_called_once_with('POST', 'Create Loop Instance',
            (f"{loop.base_url()}/loop/create/LOOP_test?templateName=template"),
            cert=loop.cert)
    assert exc.type is ResourceNotFound


def test_validate_details():
    """Test Loop instance details validation."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    valid = loop.validate_details()
    assert  valid


def test_validate_details():
    """Test Loop instance details validation."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    loop.details = {"test":"test"}
    valid = loop.validate_details()
    assert  not valid


@mock.patch.object(LoopInstance, 'send_message_json')
def test_create(mock_send_message_json):
    """Test Loop instance creation."""
    instance = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = LOOP_DETAILS
    instance.create()
    mock_send_message_json.assert_called_once_with('POST', 'Create Loop Instance',
         (f"{instance.base_url()}/loop/create/LOOP_test?templateName=template"),
         cert=instance.cert)
    assert instance.name == "LOOP_test"
    assert len(instance.details["microServicePolicies"]) > 0


@mock.patch.object(LoopInstance, 'send_message_json')
def test_create_none(mock_send_message_json):
    """Test Loop instance creation."""
    instance = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = {}
    with pytest.raises(ValueError):
        instance.create()
        mock_send_message_json.assert_called_once_with('POST', 'Create Loop Instance',
            (f"{instance.base_url()}/loop/create/LOOP_test?templateName=template"),
            cert=instance.cert)


@mock.patch.object(LoopInstance, 'send_message_json')
def test_add_operational_policy(mock_send_message_json):
    """Test adding an op policy."""
    loop = LoopInstance(template="template", name="test", details={})
    loop.details = {
        "name" : "LOOP_test",
        "operationalPolicies" : None,
        "microServicePolicies" : [
            {
                "name" : "MICROSERVICE_test"
            }
        ]
    }
    mock_send_message_json.return_value = LOOP_DETAILS
    loop.add_operational_policy(policy_type="FrequencyLimiter", policy_version="1.0.0")
    mock_send_message_json.assert_called_once_with('PUT', 'Create Operational Policy',
        (f"{loop.base_url()}/loop/addOperationaPolicy/{loop.name}/policyModel/FrequencyLimiter/1.0.0"),
        cert=loop.cert)
    assert loop.name == "LOOP_test"
    assert len(loop.details["operationalPolicies"]) > 0


@mock.patch.object(LoopInstance, 'send_message_json')
def test_not_add_operational_policy(mock_send_message_json):
    """Test adding an op policy."""
    loop = LoopInstance(template="template", name="test", details={})
    loop.details = {
        "name" : "LOOP_test",
        "operationalPolicies" : [],
        "microServicePolicies" : [
            {
                "name" : "MICROSERVICE_test"
            }
        ]
    }
    with pytest.raises(ValueError):
        mock_send_message_json.return_value = loop.details
        #mistaken policy version
        loop.add_operational_policy(policy_type="FrequencyLimiter", policy_version="not_correct")
        mock_send_message_json.assert_called_once_with('PUT', 'Create Operational Policy',
            (f"{loop.base_url()}/loop/addOperationaPolicy/{loop.name}/policyModel/FrequencyLimiter/not_correct"),
            cert=loop.cert)
        assert len(loop.details["operationalPolicies"]) == 0


@mock.patch.object(LoopInstance, 'send_message_json')
def test_remove_operational_policy(mock_send_message_json):
    """Test remove an op policy."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message_json.return_value = {
        "name" : "LOOP_test",
        "operationalPolicies" : [],
        "microServicePolicies" : [
            {
                "name" : "MICROSERVICE_test"
            }
        ]
    }
    loop.remove_operational_policy(policy_type="FrequencyLimiter", policy_version="1.0.0")
    mock_send_message_json.assert_called_once_with('PUT', 'Remove Operational Policy',
        (f"{loop.base_url()}/loop/removeOperationaPolicy/{loop.name}/policyModel/FrequencyLimiter/1.0.0"),
        cert=loop.cert,
        exception=ValueError)
    assert len(loop.details["operationalPolicies"]) == 0


@mock.patch.object(LoopInstance, 'send_message')
def test_update_microservice_policy(mock_send_message):
    """Test Loop Instance add TCA configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.update_microservice_policy()
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD TCA config"
    assert url == (f"{loop.base_url()}/loop/updateMicroservicePolicy/{loop.name}")


@mock.patch.object(LoopInstance, 'send_message')
def test_update_microservice_policy_none(mock_send_message):
    """Test Loop Instance add TCA configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message.return_value = False
    loop.update_microservice_policy()
    mock_send_message.assert_called_once()


def test_extract_operational_policy_name():
    """Test Loop Instance extract operational policy name."""
    loop = LoopInstance(template="template", name="test", details={})
    loop.details = {"operationalPolicies":[{"name":"test","policyModel":{"policyAcronym":"Drools"}}]}
    policy_name = loop.extract_operational_policy_name(policy_type="Drools")
    assert policy_name=='test'


def test_extract_none():
    """Test Loop Instance extract operational policy name."""
    loop = LoopInstance(template="template", name="test", details={})
    loop.details = {"operationalPolicies":[]}
    with pytest.raises(ValueError):
        policy_name = loop.extract_operational_policy_name(policy_type="Drools")
        assert policy_name == None


@mock.patch.object(LoopInstance, 'extract_operational_policy_name')
@mock.patch.object(LoopInstance, 'send_message')
def test_add_drools_policy_config(mock_send_message, mock_extract):
    """Test Loop Instance add op policy configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.add_op_policy_config(loop.add_drools_conf)
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD operational policy config"
    assert url == (f"{loop.base_url()}/loop/updateOperationalPolicies/{loop.name}")


@mock.patch.object(LoopInstance, 'extract_operational_policy_name')
@mock.patch.object(LoopInstance, 'send_message')
def test_add_minmax_config(mock_send_message, mock_extract):
    """Test Loop Instance add op policy configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.add_op_policy_config(loop.add_minmax_config)
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD operational policy config"
    assert url == (f"{loop.base_url()}/loop/updateOperationalPolicies/{loop.name}")


@mock.patch.object(LoopInstance, 'extract_operational_policy_name')
@mock.patch.object(LoopInstance, 'send_message')
def test_add_frequency_policy_config(mock_send_message, mock_extract):
    """Test Loop Instance add op policy configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.add_op_policy_config(loop.add_frequency_limiter)
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD operational policy config"
    assert url == (f"{loop.base_url()}/loop/updateOperationalPolicies/{loop.name}")

@mock.patch.object(LoopInstance, 'send_message')
@mock.patch.object(LoopInstance, 'add_minmax_config')
@mock.patch.object(LoopInstance, 'add_frequency_limiter')
def test_add_two_policies_config(mock_freq, mock_min, mock_send_message):
    """Test Loop Instance add op policy configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_min.return_value = '[{"test1":"test1"}]'
    mock_freq.return_value = '[{"test2":"test2"}]'
    loop.add_op_policy_config(loop.add_minmax_config)
    mock_min.assert_called_once()
    mock_send_message.assert_called_once()
    loop.add_op_policy_config(loop.add_frequency_limiter)
    mock_freq.assert_called_once()
    assert loop.operational_policies == '[{"test1":"test1"},{"test2":"test2"}]'



@mock.patch.object(LoopInstance, 'add_frequency_limiter')
@mock.patch.object(LoopInstance, 'send_message')
def test_add_op_policy_config_error(mock_send_message, mock_freq):
    """Test Loop Instance add op policy configuration."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message.return_value = False
    #if u put a non cong function
    with pytest.raises(ValueError):      
        loop.add_op_policy_config(loop.add_frequency_limiter)
        mock_send_message.assert_called_once()
        method, description, url = mock_send_message.call_args[0]
        assert method == "POST"
        assert description == "ADD operational policy config"
        assert url == (f"{loop.base_url()}/loop/updateOperationalPolicies/{loop.name}")


@mock.patch.object(LoopInstance, 'refresh_status')
@mock.patch.object(LoopInstance, 'send_message')
def test_submit_policy(mock_send_message, mock_refresh):
    """Test submit policies to policy engine."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    action = loop.act_on_loop_policy(loop.submit)
    mock_send_message.assert_called_once_with('PUT',
                                            'submit policy',
                                            (f"{loop.base_url()}/loop/submit/LOOP_test"),
                                            cert=loop.cert,
                                            exception=ValueError)
    mock_refresh.assert_called_once()
    loop.details = SUBMITED_POLICY
    assert loop.details["components"]["POLICY"]["componentState"]["stateName"] == "SENT_AND_DEPLOYED"


@mock.patch.object(LoopInstance, 'refresh_status')
@mock.patch.object(LoopInstance, 'send_message')
def test_stop_policy(mock_send_message, mock_refresh):
    """Test submit policies to policy engine."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    action = loop.act_on_loop_policy(loop.stop)
    mock_send_message.assert_called_once_with('PUT',
                                            'stop policy',
                                            (f"{loop.base_url()}/loop/stop/LOOP_test"),
                                            cert=loop.cert,
                                            exception=ValueError)
    mock_refresh.assert_called_once()
    loop.details = {"components":{"POLICY":{"componentState":{"stateName":"SENT"}}}}
    assert loop.details["components"]["POLICY"]["componentState"]["stateName"] == "SENT"


@mock.patch.object(LoopInstance, 'refresh_status')
@mock.patch.object(LoopInstance, 'send_message')
def test_restart_policy(mock_send_message, mock_refresh):
    """Test submit policies to policy engine."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    action = loop.act_on_loop_policy(loop.restart)
    mock_send_message.assert_called_once_with('PUT',
                                            'restart policy',
                                            (f"{loop.base_url()}/loop/restart/LOOP_test"),
                                            cert=loop.cert,
                                            exception=ValueError)
    mock_refresh.assert_called_once()
    loop.details = SUBMITED_POLICY
    assert loop.details["components"]["POLICY"]["componentState"]["stateName"] == "SENT_AND_DEPLOYED"


@mock.patch.object(LoopInstance, 'refresh_status')
@mock.patch.object(LoopInstance, 'send_message')
def test_not_submited_policy(mock_send_message, mock_refresh):
    """Test submit policies to policy engine."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_refresh.return_value = NOT_SUBMITED_POLICY
    action = loop.act_on_loop_policy(loop.submit)
    mock_send_message.assert_called_once_with('PUT',
                                            'submit policy',
                                            (f"{loop.base_url()}/loop/submit/LOOP_test"),
                                            cert=loop.cert,
                                            exception=ValueError)
    mock_refresh.assert_called_once()
    loop.details = NOT_SUBMITED_POLICY
    assert loop.details["components"]["POLICY"]["componentState"]["stateName"] == "SENT"


@mock.patch.object(LoopInstance, 'send_message_json')
@mock.patch.object(LoopInstance, 'send_message')
def test_deploy_microservice_to_dcae(mock_send_message, mock_send_message_json):
    """Test stop microservice."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    mock_send_message_json.return_value = SUBMITED
    state = loop.deploy_microservice_to_dcae()
    mock_send_message.assert_called_once_with('PUT',
                                            'Deploy microservice to DCAE',
                                            (f"{loop.base_url()}/loop/deploy/LOOP_test"),
                                            cert=loop.cert,
                                            exception=ValueError)
    assert state


@mock.patch.object(LoopInstance, 'send_message')
def test_undeploy_microservice_from_dcae(mock_send_message):
    """Test stop microservice."""
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    request = loop.undeploy_microservice_from_dcae()
    mock_send_message.assert_called_once_with('PUT',
                                            'Undeploy microservice from DCAE',
                                            (f"{loop.base_url()}/loop/undeploy/LOOP_test"),
                                            cert=loop.cert,
                                            exception=ValueError)


@mock.patch.object(LoopInstance, 'send_message')
def test_delete(mock_send_message):
    loop = LoopInstance(template="template", name="test", details=LOOP_DETAILS)
    request = loop.delete()
    mock_send_message.assert_called_once_with('PUT',
                                            'Delete loop instance',
                                            (f"{loop.base_url()}/loop/delete/{loop.name}"),
                                            cert=loop.cert,
                                            exception=ValueError)
