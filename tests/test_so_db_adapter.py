from unittest import mock

from onapsdk.so.so_db_adapter import SoDbAdapter, IdentityService

ADD_CLOUD_SITE_RESPONSE = {
    '_links': {
        'cloudSite': {
            'href': 'http://so.api.simpledemo.onap.org:30277/cloudSite/mc_test_cloud_site_3'
        },
        'self': {
            'href': 'http://so.api.simpledemo.onap.org:30277/cloudSite/mc_test_cloud_site_3'
        }
    },
    'aic_version': '2.5',
    'clli': 'test_clli_0',
    'cloud_owner': None,
    'cloudify_id': None,
    'creation_timestamp': '2021-05-12T08:52:48.134+0000',
    'identityService': {
        'admin_tenant': 'service',
        'creation_timestamp': '2021-05-12T08:52:48.134+0000',
        'identityServerTypeAsString': 'KEYSTONE',
        'identity_authentication_type': 'USERNAME_PASSWORD',
        'identity_server_type': 'KEYSTONE',
        'identity_url': 'http://1.2.3.4:5000/v2.0',
        'last_updated_by': None,
        'member_role': 'admin',
        'mso_id': 'onapsdk_user',
        'mso_pass': 'mso_pass_onapsdk',
        'project_domain_name': 'NULL',
        'tenant_metadata': True,
        'update_timestamp': '2021-05-12T08:52:48.134+0000',
        'user_domain_name': 'NULL'
    },
    'identity_service_id': 'test_identity_0',
    'last_updated_by': None,
    'orchestrator': 'multicloud',
    'platform': None,
    'region_id': 'test_region_0',
    'support_fabric': True,
    'update_timestamp': '2021-05-12T08:52:48.134+0000',
    'uri': None
}

SERVICE_VNF_RESPONSE = {
    'serviceVnfs': [
        {
            'modelInfo': {
                'modelName': 'test_vnf_01', 
                'modelUuid': 'd2779cc5-fb01-449f-a355-7e5d911dca93', 
                'modelInvariantUuid': '027cb696-f68f-47db-9b0e-585ea3eaa512', 
                'modelVersion': '1.0', 
                'modelCustomizationUuid': 'b8740912-e0fc-426f-af97-7657caf57847', 
                'modelInstanceName': 'test_vnf_01 0'
            }, 
            'toscaNodeType': 'org.openecomp.resource.vf.Mvnr5gCucpVfT003', 
            'nfFunction': None, 
            'nfType': None, 
            'nfRole': None, 
            'nfNamingCode': None, 
            'multiStageDesign': 'false', 
            'vnfcInstGroupOrder': None, 
            'resourceInput': None, 
            'vfModules': [{'modelInfo': 
            {
                'modelName': 'test_vf_01', 
                'modelUuid': '153464b8-4f47-4140-8b92-9614c4578d91', 
                'modelInvariantUuid': '753deff5-99a2-4154-8c1d-3e956cb96f32', 
                'modelVersion': '1', 
                'modelCustomizationUuid': '7ca564f3-b908-499c-b086-ae77ad270d8c'
            }, 
            'isBase': False, 
            'vfModuleLabel': 'vf_mod_label', 
            'initialCount': 0, 
            'hasVolumeGroup': False
            }
        ], 
        'groups': []
    }
  ]
}


def test_identity_service():
    identity_service = IdentityService(identity_id="identity_123")
    assert identity_service.identity_id == "identity_123"
    assert identity_service.url == "http://1.2.3.4:5000/v2.0"
    assert identity_service.mso_id == "onapsdk_user"
    assert identity_service.mso_pass == "mso_pass_onapsdk"
    assert identity_service.project_domain_name == "NULL"
    assert identity_service.user_domain_name == "NULL"
    assert identity_service.admin_tenant == "service"
    assert identity_service.member_role == "admin"
    assert identity_service.identity_server_type == "KEYSTONE"
    assert identity_service.identity_authentication_type == "USERNAME_PASSWORD"
    assert identity_service.hibernate_lazy_initializer == {}
    assert identity_service.server_type_as_string == "KEYSTONE"
    assert identity_service.tenant_metadata is True

@mock.patch.object(SoDbAdapter, "send_message_json")
def test_add_cloud_site(mock_send_message_json):
    identity_service = IdentityService(identity_id="test_identity_0")
    mock_send_message_json.return_value = ADD_CLOUD_SITE_RESPONSE

    response = SoDbAdapter.add_cloud_site(cloud_region_id="test_region_0",
                                          complex_id="test_clli_0",
                                          identity_service=identity_service)
    assert response['region_id'] == "test_region_0"
    assert response['aic_version'] == "2.5"
    assert response['clli'] == "test_clli_0"
    assert response['orchestrator'] == "multicloud"
    assert response['identity_service_id'] == "test_identity_0"

@mock.patch.object(SoDbAdapter, "send_message_json")
def test_get_service_vnf_info(mock_send_message_json):    
    mock_send_message_json.return_value = ADD_CLOUD_SITE_RESPONSE
  
    response = SoDbAdapter.get_service_vnf_info(identifier="test_id_0")
    assert response['region_id'] == "test_region_0"
    assert response['aic_version'] == "2.5"
    assert response['clli'] == "test_clli_0"
    assert response['orchestrator'] == "multicloud"
    assert response['identity_service_id'] == "test_identity_0"
