import logging
import os

import pytest

from onapsdk.msb.k8s import (
    Definition,
    Instance,
    ConnectivityInfo)

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

RB_NAME = "test_definition"
RB_VERSION = "ver_1"
PROFILE_NAME = "test-profile"
PROFILE_NAMESPACE = "test"
PROFILE_K8S_VERSION = "1.0"
PROFILE_ARTIFACT_PATH = "artifacts\\profile.tar.gz"  # FILL ME
TEMPLATE_NAME = "test_template"
TEMPLATE_DESCRIPTION = "test description"
CLOUD_REGION_ID = "k8s_region_test"  # FILL ME
CLOUD_OWNER = "CloudOwner"
KUBECONFIG_PATH = "artifacts\\kubeconfig"  # FILL ME
MYPATH = os.path.dirname(os.path.realpath(__file__))

pytest.INSTANCE_ID = ""


@pytest.mark.integration
def test_definition_create_upload_artifact():
    definition = Definition.create(RB_NAME, RB_VERSION)
    definition.upload_artifact(b'definition_artifact_file')


@pytest.mark.integration
def test_definition_get_all():
    definitions = list(Definition.get_all())


@pytest.mark.integration
def test_configuration_template():
    definition = Definition.get_definition_by_name_version(RB_NAME,
                                                           RB_VERSION)
    definition.create_configuration_template(TEMPLATE_NAME, TEMPLATE_DESCRIPTION)
    definition.get_all_configuration_templates()
    definition.get_configuration_template_by_name(TEMPLATE_NAME)


@pytest.mark.integration
def test_profile_create_upload_artifact():
    definition = Definition.get_definition_by_name_version(RB_NAME,
                                                           RB_VERSION)
    profile = definition.create_profile(PROFILE_NAME,
                                        PROFILE_NAMESPACE,
                                        PROFILE_K8S_VERSION)
    profile.upload_artifact(b'profile_artifact_file')


@pytest.mark.integration
def test_profile_get_all():
    definition = Definition.get_definition_by_name_version(RB_NAME,
                                                           RB_VERSION)
    profiles = list(definition.get_all_profiles())


@pytest.mark.integration
def test_connectivity_info_create():
    conninfo = ConnectivityInfo.create(CLOUD_REGION_ID,
                                       CLOUD_OWNER,
                                       b'kubeconfig_content_test')


@pytest.mark.integration
def test_instance_create():
    definition = Definition.get_definition_by_name_version(RB_NAME,
                                                           RB_VERSION)
    profile = definition.get_profile_by_name(PROFILE_NAME)
    instance = Instance.create(CLOUD_REGION_ID,
                               profile.profile_name,
                               definition.rb_name,
                               definition.rb_version)
    pytest.INSTANCE_ID = instance.instance_id


@pytest.mark.integration
def test_instance_get_all():
    instances = list(Instance.get_all())


@pytest.mark.integration
def test_instance_delete():
    instance = Instance.get_by_id(pytest.INSTANCE_ID)
    instance.delete()


@pytest.mark.integration
def test_connectivity_info_delete():
    conninfo = ConnectivityInfo.get_connectivity_info_by_region_id(CLOUD_REGION_ID)
    conninfo.delete()


@pytest.mark.integration
def test_definition_profile_get_delete():
    definition = Definition.get_definition_by_name_version(RB_NAME, RB_VERSION)
    profile = definition.get_profile_by_name(PROFILE_NAME)
    profile.delete()
    definition.delete()
