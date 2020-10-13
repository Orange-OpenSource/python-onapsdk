from unittest import mock

import pytest

from onapsdk.msb.k8s import Definition, Profile, ConfigurationTemplate, ConnectivityInfo, InstantiationParameter, InstantiationRequest, Instance


CONNECTIVITY_INFO = {
    "cloud-region": "test_cloud_region",
    "cloud-owner": "test_cloud_owner",
    "other-connectivity-list": {},
    "kubeconfig": "test_kubeconfig"
}


DEFINITION = {
    "rb-name": "test_rb_name_0",
    "rb-version": "test_rb_version_0"
}


DEFINITIONS = [
    DEFINITION,
    {
        "rb-name": "test_rb_name_1",
        "rb-version": "test_rb_version_1",
        "chart-name": "test_chart_name_1",
        "description": "test_description_1",
        "labels": {}
    }
]


PROFILE = {
    "rb-name": "test_rb_name",
    "rb-version": "test_rb_version",
    "profile-name": "test_profile_name",
    "namespace": "test_namespace"
}


PROFILES = [
    PROFILE,
    {
        "rb-name": "test_rb_name_1",
        "rb-version": "test_rb_version_1",
        "profile-name": "test_profile_name_1",
        "namespace": "test_namespace_1"
    }
]


CONFIGURATION_TEMPLATE = {
    "template-name": "test_configuration_template_name",
    "description": "test_configuration_template_description"
}


CONFIGURATION_TEMPLATES = [
    CONFIGURATION_TEMPLATE,
    {
        "template-name": "test_configuration_template_name_0"
    }
]


INSTANCE = {
  "id": "ID_GENERATED_BY_K8SPLUGIN",
  "namespace": "NAMESPACE_WHERE_INSTANCE_HAS_BEEN_DEPLOYED_AS_DERIVED_FROM_PROFILE",
  "release-name": "RELEASE_NAME_AS_COMPUTED_BASED_ON_INSTANTIATION_REQUEST_AND_PROFILE_DEFAULT",
  "request": {
    "rb-name": "test-rbdef",
    "rb-version": "v1",
    "profile-name": "p1",
    "release-name": "release-x",
    "cloud-region": "krd",
    "override-values": {
        "optionalDictOfParameters": "andTheirValues, like",
        "global.name": "dummy-name"
    },
    "labels": {
        "optionalLabelForInternalK8spluginInstancesMetadata": "dummy-value"
    },
  },
  "resources": [
        {                                                                                                                                                                                                         
            "GVK": {                                                                                                                                                                                              
                "Group": "",                                                                                                                                                                                      
                "Kind": "ConfigMap",                                                                                                                                                                              
                "Version": "v1"                                                                                                                                                                                   
            },                                                                                                                                                                                                    
            "Name": "test-cm"                                                                                                                                                                              
        },                                                                                                                                                                                                        
        {                                                                                                                                                                                                         
            "GVK": {                                                                                                                                                                                              
                "Group": "",                                                                                                                                                                                      
                "Kind": "Service",                                                                                                                                                                                
                "Version": "v1"                                                                                                                                                                                   
            },                                                                                                                                                                                                    
            "Name": "test-svc"                                                                                                                                                                           
        },                                                                                                                                                                                                        
        {
            "GVK": {
                "Group": "apps",
                "Kind": "Deployment",
                "Version": "v1"
            },
            "Name": "test-dep"
        }
  ]
}


INSTANCES = [
    INSTANCE
]


@mock.patch.object(ConnectivityInfo, "send_message_json")
def test_get_connectivity_info_by_region_id(mock_send_message_json):
    mock_send_message_json.return_value = CONNECTIVITY_INFO
    conn_info: ConnectivityInfo = ConnectivityInfo.get_connectivity_info_by_region_id("test_cloud_region_id")
    assert conn_info.cloud_region_id == "test_cloud_region"
    assert conn_info.cloud_owner == "test_cloud_owner"
    assert conn_info.other_connectivity_list == {}
    assert conn_info.kubeconfig == "test_kubeconfig"


@mock.patch.object(ConnectivityInfo, "send_message")
@mock.patch.object(ConnectivityInfo, "send_message_json")
def test_connectivity_info_create_delete(mock_send_message_json, mock_send_message):
    mock_send_message_json.return_value = CONNECTIVITY_INFO
    conn_info: ConnectivityInfo = ConnectivityInfo.create("test_cloud_region", "test_cloud_owner", b"kubeconfig")
    assert conn_info.cloud_region_id == "test_cloud_region"
    assert conn_info.cloud_owner == "test_cloud_owner"
    assert conn_info.other_connectivity_list == {}
    assert conn_info.kubeconfig == "test_kubeconfig"
    conn_info.delete()


@mock.patch.object(Definition, "send_message_json")
def test_definition_get_all(mock_send_message_json):
    mock_send_message_json.return_value = []
    assert len(list(Definition.get_all())) == 0
    
    mock_send_message_json.return_value = DEFINITIONS
    definitions = list(Definition.get_all())
    assert len(definitions) == 2

    def_0, def_1 = definitions
    assert def_0.rb_name == "test_rb_name_0"
    assert def_0.rb_version == "test_rb_version_0"
    assert def_0.chart_name is None
    assert def_0.description is None
    assert def_0.labels is None

    assert def_1.rb_name == "test_rb_name_1"
    assert def_1.rb_version == "test_rb_version_1"
    assert def_1.chart_name == "test_chart_name_1"
    assert def_1.description == "test_description_1"
    assert def_1.labels == {}


@mock.patch.object(Definition, "send_message_json")
def test_get_definition_by_name_version(mock_send_message_json):
    mock_send_message_json.return_value = DEFINITION
    def_0 = Definition.get_definition_by_name_version("rb_name", "rb_version")
    assert def_0.rb_name == "test_rb_name_0"
    assert def_0.rb_version == "test_rb_version_0"
    assert def_0.chart_name is None
    assert def_0.description is None
    assert def_0.labels is None


@mock.patch.object(Definition, "send_message_json")
@mock.patch.object(Definition, "send_message")
def test_create_definition(mock_send_message, mock_send_message_json):
    mock_send_message_json.return_value = DEFINITION
    def_0 = Definition.create(
        rb_name="test_rb_name_0",
        rb_version="test_rb_version_0"
    )
    assert def_0.rb_name == "test_rb_name_0"
    assert def_0.rb_version == "test_rb_version_0"
    assert def_0.chart_name is None
    assert def_0.description is None
    assert def_0.labels is None


@mock.patch.object(Definition, "send_message_json")
@mock.patch.object(Definition, "send_message")
def test_definition_create_profile(mock_send_message, mock_send_message_json):
    mock_send_message_json.return_value = PROFILE
    deff = Definition(
        rb_name="test_rb_name",
        rb_version="test_rb_version",
        chart_name="test_chart_name",
        description="test_description",
        labels={}
    )
    profile = deff.create_profile(
        profile_name="test_profile_name",
        namespace="test_namespace",
        kubernetes_version="test_k8s_version"
    )
    assert profile.rb_name == "test_rb_name"
    assert profile.rb_version == "test_rb_version"
    assert profile.profile_name == "test_profile_name"
    assert profile.namespace == "test_namespace"
    assert profile.kubernetes_version is None
    assert profile.labels == {}
    assert profile.release_name == "test_profile_name"


@mock.patch.object(Definition, "send_message_json")
def test_definition_get_profile_by_name(mock_send_message_json):
    mock_send_message_json.return_value = PROFILE
    deff = Definition(
        rb_name="test_rb_name",
        rb_version="test_rb_version",
        chart_name="test_chart_name",
        description="test_description",
        labels={}
    )
    profile = deff.get_profile_by_name("test_profile_name")
    assert profile.rb_name == "test_rb_name"
    assert profile.rb_version == "test_rb_version"
    assert profile.profile_name == "test_profile_name"
    assert profile.namespace == "test_namespace"
    assert profile.kubernetes_version is None
    assert profile.labels == {}
    assert profile.release_name == "test_profile_name"


@mock.patch.object(Definition, "send_message_json")
def test_definition_get_all_profiles(mock_send_message_json):
    mock_send_message_json.return_value = []
    deff = Definition(
        rb_name="test_rb_name",
        rb_version="test_rb_version",
        chart_name="test_chart_name",
        description="test_description",
        labels={}
    )
    assert len(list(deff.get_all_profiles())) == 0

    mock_send_message_json.return_value = PROFILES
    profiles = list(deff.get_all_profiles())
    assert len(profiles) == 2
    prof_0, prof_1 = profiles

    assert prof_0.rb_name == "test_rb_name"
    assert prof_0.rb_version == "test_rb_version"
    assert prof_0.profile_name == "test_profile_name"
    assert prof_0.namespace == "test_namespace"
    assert prof_0.kubernetes_version is None
    assert prof_0.labels == {}
    assert prof_0.release_name == "test_profile_name"

    assert prof_1.rb_name == "test_rb_name_1"
    assert prof_1.rb_version == "test_rb_version_1"
    assert prof_1.profile_name == "test_profile_name_1"
    assert prof_1.namespace == "test_namespace_1"
    assert prof_1.kubernetes_version is None
    assert prof_1.labels == {}
    assert prof_1.release_name == "test_profile_name_1"


@mock.patch.object(Definition, "send_message_json")
def test_definition_get_configuration_template_by_name(mock_send_message_json):
    mock_send_message_json.return_value = CONFIGURATION_TEMPLATE
    deff = Definition(
        rb_name="test_rb_name",
        rb_version="test_rb_version",
        chart_name="test_chart_name",
        description="test_description",
        labels={}
    )
    configuration_tmpl = deff.get_configuration_template_by_name(
        template_name="test_configuration_template_name"
    )
    assert configuration_tmpl.rb_name == deff.rb_name
    assert configuration_tmpl.rb_version == deff.rb_version
    assert configuration_tmpl.template_name == "test_configuration_template_name"
    assert configuration_tmpl.description == "test_configuration_template_description"


@mock.patch.object(Definition, "send_message_json")
@mock.patch.object(Definition, "send_message")
def test_definition_create_configuration_template(mock_send_message, mock_send_message_json):
    mock_send_message_json.return_value = CONFIGURATION_TEMPLATE
    deff = Definition(
        rb_name="test_rb_name",
        rb_version="test_rb_version",
        chart_name="test_chart_name",
        description="test_description",
        labels={}
    )
    configuration_tmpl = deff.create_configuration_template(
        template_name="test_configuration_template_name",
        description="test_configuration_template_description"
    )
    assert configuration_tmpl.rb_name == deff.rb_name
    assert configuration_tmpl.rb_version == deff.rb_version
    assert configuration_tmpl.template_name == "test_configuration_template_name"
    assert configuration_tmpl.description == "test_configuration_template_description"
    assert configuration_tmpl.url == f"{deff.base_url}/{deff.rb_name}/{deff.rb_version}/config-template/test_configuration_template_name"


@mock.patch.object(Definition, "send_message_json")
def test_definition_get_all_configuration_templates(mock_send_message_json):
    mock_send_message_json.return_value = []
    deff = Definition(
        rb_name="test_rb_name",
        rb_version="test_rb_version",
        chart_name="test_chart_name",
        description="test_description",
        labels={}
    )
    assert len(list(deff.get_all_configuration_templates())) == 0
    
    mock_send_message_json.return_value = CONFIGURATION_TEMPLATES
    configuration_tmplts = list(deff.get_all_configuration_templates())
    assert len(configuration_tmplts) == 2

    tmpl_0, tmpl_1 = configuration_tmplts
    assert tmpl_0.rb_name == deff.rb_name
    assert tmpl_0.rb_version == deff.rb_version
    assert tmpl_0.template_name == "test_configuration_template_name"
    assert tmpl_0.description == "test_configuration_template_description"

    assert tmpl_1.rb_name == deff.rb_name
    assert tmpl_1.rb_version == deff.rb_version
    assert tmpl_1.template_name == "test_configuration_template_name_0"
    assert tmpl_1.description is None


@mock.patch.object(Instance, "send_message_json")
def test_instance_get_all(mock_send_message_json):
    mock_send_message_json.return_value = []
    assert len(list(Instance.get_all())) == 0

    mock_send_message_json.return_value = INSTANCES
    assert len(list(Instance.get_all())) == 1


@mock.patch.object(Instance, "send_message_json")
def test_instance_create(mock_send_message_json):
    mock_send_message_json.return_value = INSTANCE
    instance = Instance.create(
        "test_cloud_region_id",
        "test_profile_name",
        "test_rb_name",
        "test_rb_version"
    )
    assert instance.instance_id == "ID_GENERATED_BY_K8SPLUGIN"
    assert instance.namespace == "NAMESPACE_WHERE_INSTANCE_HAS_BEEN_DEPLOYED_AS_DERIVED_FROM_PROFILE"


@mock.patch.object(Instance, "send_message_json")
@mock.patch.object(Instance, "send_message")
def test_instance_get_by_id(mock_send_message, mock_send_message_json):
    mock_send_message_json.return_value = INSTANCE
    instance = Instance.get_by_id("ID_GENERATED_BY_K8SPLUGIN")
    assert instance.instance_id == "ID_GENERATED_BY_K8SPLUGIN"
    assert instance.namespace == "NAMESPACE_WHERE_INSTANCE_HAS_BEEN_DEPLOYED_AS_DERIVED_FROM_PROFILE"
    instance.delete()
