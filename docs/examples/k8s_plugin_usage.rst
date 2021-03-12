E2E msb k8s plugin usage
########################


.. code:: Python

    import logging
    import os

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
    DEFINITION_ARTIFACT_PATH = "artifacts\\vault-consul-dev.tar.gz"  # FILL ME
    PROFILE_NAME = "test-profile"
    PROFILE_NAMESPACE = "test"
    PROFILE_K8S_VERSION = "1.0"
    PROFILE_ARTIFACT_PATH = "artifacts\\profile.tar.gz"  # FILL ME
    CLOUD_REGION_ID = "k8s_region_test"  # FILL ME
    CLOUD_OWNER = "CloudOwner"
    KUBECONFIG_PATH = "artifacts\\kubeconfig"  # FILL ME
    MYPATH = os.path.dirname(os.path.realpath(__file__))

    ######## Create new Definition ############################################
    definition = Definition.create(RB_NAME, RB_VERSION)

    ######## Upload artifact for created definition ###########################
    definition_artifact_file = os.path.join(MYPATH, DEFINITION_ARTIFACT_PATH)
    definition.upload_artifact(open(definition_artifact_file, 'rb').read())

    ######## Get one Definition ###############################################
    check_definition = Definition.get_definition_by_name_version(RB_NAME,
                                                                RB_VERSION)

    ######## Get all Definitions ##############################################
    definitions = list(Definition.get_all())

    ######## Create profile for Definition ####################################
    profile = definition.create_profile(PROFILE_NAME,
                                        PROFILE_NAMESPACE,
                                        PROFILE_K8S_VERSION)

    ######## Upload artifact for created profile ##############################
    profile_artifact_file = os.path.join(MYPATH, PROFILE_ARTIFACT_PATH)
    profile.upload_artifact(open(profile_artifact_file, 'rb').read())

    ######## Get one Profile ##################################################
    check_profile = definition.get_profile_by_name(PROFILE_NAME)

    ######## Get all Profiles #################################################
    profiles = list(definition.get_all_profiles())

    ######## Create Connectivity Info #########################################
    kubeconfig_file = os.path.join(MYPATH, KUBECONFIG_PATH)
    conninfo = ConnectivityInfo.create(CLOUD_REGION_ID,
                                    CLOUD_OWNER,
                                    open(kubeconfig_file, 'rb').read())

    ######## Instantiate Profile ##############################################
    instance = Instance.create(CLOUD_REGION_ID,
                            profile.profile_name,
                            definition.rb_name,
                            definition.rb_version)

    ######## Get Instance by ID ###############################################
    check_instance = Instance.get_by_id(instance.instance_id)

    ######## Get all Instances ################################################
    instances = list(Instance.get_all())

    ######## Delete Instance ##################################################
    instance.delete()

    ######## Check instance deletion ##########################################
    instances = list(Instance.get_all())

    ######## Delete Connectivity Info #########################################
    conninfo.delete()

    ######## Delete Profile ###################################################
    profile.delete()

    ######## Delete Definition ################################################
    definition.delete()