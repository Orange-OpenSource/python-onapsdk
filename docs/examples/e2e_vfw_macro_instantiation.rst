E2E Instantiation of vFW
########################


.. code:: Python

    import logging
    import time
    import json
    from uuid import uuid4
    from onapsdk.aai.aai_element import AaiElement
    from onapsdk.aai.cloud_infrastructure import (
        CloudRegion,
        Complex,
        Tenant
    )
    from onapsdk.aai.service_design_and_creation import (
        Service as AaiService
    )
    from onapsdk.aai.business import (
        ServiceInstance,
        VnfInstance,
        VfModuleInstance,
        ServiceSubscription,
        Customer,
        OwningEntity as AaiOwningEntity
    )
    from onapsdk.so.instantiation import (
        ServiceInstantiation,
        VnfInstantiation,
        InstantiationParameter,
        VnfParameters,
        VfmoduleParameters
    )
    from onapsdk.sdc.properties import Property
    from onapsdk.sdc import SDC
    from onapsdk.sdc.vendor import Vendor
    from onapsdk.sdc.vsp import Vsp
    from onapsdk.sdc.vf import Vf
    from onapsdk.sdc.service import Service, ServiceInstantiationType
    import onapsdk.constants as const
    import os
    from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project

    from onapsdk.cds.blueprint import Blueprint
    from onapsdk.cds.data_dictionary import DataDictionary, DataDictionarySet

    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    logname = "./vfwcds.debug.log"
    fh = logging.FileHandler(logname)
    fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    ###########################################################################
    ######## CDS Design settings ##############################################
    ######## vFW CDS Example     ##############################################
    ###########################################################################
    # DDF Settings (dd files located in following location)
    DDDIR = "resources/starter-dictionary"
    DDFILE = "resources/my_dd.json"

    # CBA resources (location of base CBA file)
    CBAFILE = "resources/vFWCDS/CBA/CBA.zip"
    ARTIFACT_LABEL = "vnfcds"
    ARTIFACT_NAME = "CBA_enriched.zip"
    ARTIFACT_TYPE = "CONTROLLER_BLUEPRINT_ARCHIVE"
    ARTIFACT_FILE_PATH = "resources/vFWCDS/CBA/CBA_enriched.zip"
    SDNC_TEMPLATE_NAME = "vFW-CDS"
    SDNC_TEMPLATE_VERSION = "1.0.0"
    SDNC_ARTIFACT_NAME = "vnf"

    ###########################################################################
    ######## Service Design settings ##########################################
    ###########################################################################
    VENDOR = "VNFVendor"

    # HEAT resources (location of zipped HEAT file)
    VSPFILE = "resources/vFWCDS/HEAT/vFW/vFW.zip"
    VSPNAME = "vfwcds_VS"
    VFNAME = "vfwcds_VF"
    SERVICENAME = "vfwcds_SERVICE"

    ###########################################################################
    ######## Runtime preparation settings #####################################
    ###########################################################################
    # Default Cloud
    CLOUD_OWNER = "CloudOwner"
    CLOUD_REGION = "RegionOne"

    GLOBAL_CUSTOMER_ID = "generic"
    CLOUD_TYPE = "openstack"
    CLOUD_VERSION = "pike"
    VIM_USERNAME = <user>  # FILL ME
    VIM_PASSWORD = <password>  # FILL ME
    VIM_SERVICE_URL = "http://<vim-url>/v3"  # FILL ME
    TENANT_NAME = <tenant>  # FILL ME
    TENANT_SEC_GROUP = <sec-group>  # FILL ME
    COMPLEX_PHYSICAL_LOCATION_ID = "location"
    COMPLEX_DATA_CENTER_CODE = "1234"


    # common
    OWNING_ENTITY = "Test-OE"
    PROJECT = "Test-Project"
    PLATFORM = "Test-Platform"
    LINE_OF_BUSINESS = "Test-BusinessLine"

    SERVICE_DELETION = False

    ###########################################################################
    ######## Service Instance attributes ######################################
    ###########################################################################
    SERVICE_INSTANCE_NAME = "vFWCDS-Instance-1"
    ONAP_PRIVATE_NET = "onap-oam"   # FILL ME
    ONAP_PRIVATE_SUBNET = "onap-oam-subnet" # FILL ME
    PUBLIC_NET = "admin"   # FILL ME
    IMAGE_NAME = "Ubuntu_1604"   # FILL ME
    FLAVOR_NAME = "m1.small"    # FILL ME

    logger.info("*******************************")
    logger.info("********* CBA Creation ********")
    logger.info("*******************************")

    logger.info("******** Load Data Dictionary *******")
    mypath = os.path.dirname(os.path.realpath(__file__))
    myddpath = os.path.join(mypath, DDDIR)
    myddfile = os.path.join(mypath, DDFILE)

    logger.info("path: %s", myddpath)
    dd_set = DataDictionarySet()
    for file in os.listdir(myddpath):
        logger.info("file: %s", file)
        if file.endswith(".json"):
            with open(os.path.join(myddpath, file), "r") as dd_file:  # type file
                dd_json: dict = json.loads(dd_file.read())
                logger.info("DD: %s", dd_json)
            dd_set.add(DataDictionary(dd_json))
    logger.info("DD Length: %d", dd_set.length)
    dd_set.upload()

    logger.info("******** Open Blueprint *******")
    cbafile = os.path.join(mypath, CBAFILE)
    artifactfile = os.path.join(mypath, ARTIFACT_FILE_PATH)

    blueprint = Blueprint.load_from_file(cbafile)
    enriched_blueprint = blueprint.enrich()  # returns enriched blueprint object
    enriched_blueprint.save(artifactfile)


    logger.info("*******************************")
    logger.info("******** SERVICE DESIGN *******")
    logger.info("*******************************")

    logger.info("******** Onboard Vendor *******")
    vendor = Vendor(name=VENDOR)
    vendor.onboard()

    logger.info("******** Onboard VSP *******")
    vspfile = os.path.join(mypath, VSPFILE)
    vsp = Vsp(name=VSPNAME, vendor=vendor, package=open(vspfile, 'rb'))
    vsp.onboard()


    logger.info("******** Onboard VF *******")
    vf = Vf(name=VFNAME)
    vf.vsp = vsp
    vf.create()

    if vf.status == const.DRAFT:

        logger.info("******** Extract Artifact Data *******")
        data = open(artifactfile, 'rb').read()

        logger.info("******** Upload Artifact *******")
        vf.add_deployment_artifact(artifact_type=ARTIFACT_TYPE,
                                   artifact_name=ARTIFACT_NAME,
                                   artifact_label=ARTIFACT_LABEL,
                                   artifact=artifactfile)

    vf.onboard()

    svc = Service(name=SERVICENAME,instantiation_type=ServiceInstantiationType.MACRO)
    svc.create()

    if svc.status == const.DRAFT:
        svc.add_resource(vf)

        logger.info("******** Set SDNC properties for VF ********")
        component = svc.get_component(vf)
        prop = component.get_property("sdnc_model_version")
        prop.value = SDNC_TEMPLATE_VERSION
        prop = component.get_property("sdnc_artifact_name")
        prop.value = SDNC_ARTIFACT_NAME
        prop = component.get_property("sdnc_model_name")
        prop.value = SDNC_TEMPLATE_NAME
        prop = component.get_property("controller_actor")
        prop.value = "CDS"
        prop = component.get_property("skip_post_instantiation_configuration")
        prop.value = False

        logger.info("******** Onboard Service *******")
        svc.checkin()
        svc.onboard()

    logger.info("******** Check Service Distribution *******")
    distribution_completed = False
    nb_try = 0
    nb_try_max = 10
    while distribution_completed is False and nb_try < nb_try_max:
        distribution_completed = svc.distributed
        if distribution_completed is True:
           logger.info("Service Distribution for %s is sucessfully finished",svc.name)
           break
        logger.info("Service Distribution for %s ongoing, Wait for 60 s",svc.name)
        time.sleep(60)
        nb_try += 1

    if distribution_completed is False:
        logger.error("Service Distribution for %s failed !!",svc.name)
        exit(1)

    logger.info("*******************************")
    logger.info("***** RUNTIME PREPARATION *****")
    logger.info("*******************************")

    logger.info("******** Create Complex *******")
    cmplx = Complex.create(
        physical_location_id=COMPLEX_PHYSICAL_LOCATION_ID,
        data_center_code=COMPLEX_DATA_CENTER_CODE,
        name=COMPLEX_PHYSICAL_LOCATION_ID
    )

    logger.info("******** Create CloudRegion *******")
    cloud_region = CloudRegion.create(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION,
        orchestration_disabled=False,
        in_maint=False,
        cloud_type=CLOUD_TYPE,
        cloud_zone="z1",
        complex_name=COMPLEX_PHYSICAL_LOCATION_ID,
        sriov_automation=False,
        owner_defined_type="t1",
        cloud_region_version=CLOUD_VERSION
    )

    logger.info("******** Link Complex to CloudRegion *******")
    cloud_region.link_to_complex(cmplx)

    logger.info("******** Add ESR Info to CloudRegion *******")
    cloud_region.add_esr_system_info(
        esr_system_info_id=str(uuid4()),
        user_name=VIM_USERNAME,
        password=VIM_PASSWORD,
        system_type="VIM",
        service_url=VIM_SERVICE_URL,
        cloud_domain="Default",
        ssl_insecure=False,
        system_status="active",
        default_tenant=TENANT_NAME
    )

    logger.info("******** Register CloudRegion to MultiCloud *******")
    cloud_region.register_to_multicloud()

    logger.info("******** Check MultiCloud Registration *******")
    time.sleep(60)
    tenant_found = False
    availability_zone_found = False
    registration_completed = False
    nb_try = 0
    nb_try_max = 10
    while registration_completed is False and nb_try < nb_try_max:
        for tenant in cloud_region.tenants:
            logger.debug("Tenant %s found in %s_%s",tenant.name,cloud_region.cloud_owner,cloud_region.cloud_region_id)
            tenant_found = True
        for az in cloud_region.availability_zones:
            logger.debug("A-Zone %s found",az.name)
            availability_zone_found = True
        if availability_zone_found and tenant_found:
            registration_completed = True
        if registration_completed is False:
            time.sleep(60)
        nb_try += 1

    if registration_completed is False:
        logger.error("Registration of Cloud %s_%s failed !!",cloud_region.cloud_owner,cloud_region.cloud_region_id)
        exit(1)
    else:
        logger.info("Registration of Cloud %s_%s successful !!",cloud_region.cloud_owner,cloud_region.cloud_region_id)

    logger.info("*******************************")
    logger.info("**** SERVICE INSTANTIATION ****")
    logger.info("*******************************")

    logger.info("******** Create Customer *******")
    customer = None
    for found_customer in list(Customer.get_all()):
        logger.debug("Customer %s found", found_customer.subscriber_name)
        if found_customer.subscriber_name == GLOBAL_CUSTOMER_ID:
            logger.info("Customer %s found", found_customer.subscriber_name)
            customer = found_customer
            break
    if not customer:
        customer = Customer.create(GLOBAL_CUSTOMER_ID,GLOBAL_CUSTOMER_ID, "INFRA")

    logger.info("******** Find Service in SDC *******")
    service = None
    services = Service.get_all()
    for found_service in services:
        logger.debug("Service %s is found, distribution %s",found_service.name,    found_service.distribution_status)
        if found_service.name == SERVICENAME:
            logger.info("Found Service %s in SDC",found_service.name)
            service = found_service
            break

    if not service:
        logger.error("Service %s not found in SDC",SERVICENAME)
        exit(1)

    logger.info("******** Check Service Subscription *******")
    service_subscription = None
    for service_sub in customer.service_subscriptions:
        logger.debug("Service subscription %s is found",service_sub.service_type)
        if service_sub.service_type == SERVICENAME:
            logger.info("Service %s subscribed",SERVICENAME)
            service_subscription = service_sub
            break

    if not service_subscription:
        logger.info("******** Subscribe Service *******")
        customer.subscribe_service(service)

    logger.info("******** Get Tenant *******")
    cloud_region = CloudRegion(cloud_owner=CLOUD_OWNER, cloud_region_id=CLOUD_REGION,
                               orchestration_disabled=True, in_maint=False)
    tenant = None
    for found_tenant in cloud_region.tenants:
        logger.debug("Tenant %s found in %s_%s",found_tenant.name,cloud_region.cloud_owner,cloud_region.cloud_region_id)
        if found_tenant.name == TENANT_NAME:
            logger.info("Found my Tenant %s",found_tenant.name)
            tenant = found_tenant
            break

    if not tenant:
        logger.error("tenant %s not found",TENANT_NAME)
        exit(1)

    logger.info("******** Connect Service to Tenant *******")
    service_subscription = None
    for service_sub in customer.service_subscriptions:
        logger.debug("Service subscription %s is found",service_sub.service_type)
        if service_sub.service_type == SERVICENAME:
            logger.info("Service %s subscribed",SERVICENAME)
            service_subscription = service_sub
            break

    if not service_subscription:
        logger.error("Service subscription %s is not found",SERVICENAME)
        exit(1)

    service_subscription.link_to_cloud_region_and_tenant(cloud_region, tenant)

    logger.info("******** Add Business Objects (OE, P, Pl, LoB) in VID *******")
    vid_owning_entity = OwningEntity.create(OWNING_ENTITY)
    vid_project = Project.create(PROJECT)
    vid_platform = Platform.create(PLATFORM)
    vid_line_of_business = LineOfBusiness.create(LINE_OF_BUSINESS)

    logger.info("******** Add Owning Entity in AAI *******")
    owning_entity = None
    for oe in AaiOwningEntity.get_all():
        if oe.name == vid_owning_entity.name:
            owning_entity = oe
            break
    if not owning_entity:
        logger.info("******** Owning Entity not existing: create *******")
        owning_entity = AaiOwningEntity.create(vid_owning_entity.name, str(uuid4()))

    ###########################################################################
    ######## VFModule parameters ##############################################
    ###########################################################################
    vfm_base=[
       InstantiationParameter(name="sec_group", value=TENANT_SEC_GROUP),
       InstantiationParameter(name="public_net_id", value=PUBLIC_NET)
    ]

    vfm_vsn=[
       InstantiationParameter(name="sec_group", value=TENANT_SEC_GROUP),
       InstantiationParameter(name="public_net_id", value=PUBLIC_NET)
    ]

    vfm_vfw=[
       InstantiationParameter(name="sec_group", value=TENANT_SEC_GROUP),
       InstantiationParameter(name="public_net_id", value=PUBLIC_NET)
    ]

    vfm_vpkg=[
       InstantiationParameter(name="sec_group", value=TENANT_SEC_GROUP),
       InstantiationParameter(name="public_net_id", value=PUBLIC_NET)
    ]

    base_paras=VfmoduleParameters("base_template",vfm_base)
    vpkg_paras=VfmoduleParameters("vpkg",vfm_vpkg)
    vsn_paras=VfmoduleParameters("vsn",vfm_vsn)
    vfw_paras=VfmoduleParameters("vfw",vfm_vfw)

    ###########################################################################
    ######## VNF parameters ###################################################
    ###########################################################################

    vnf_vfw=[
       InstantiationParameter(name="onap_private_net_id", value=ONAP_PRIVATE_NET),
       InstantiationParameter(name="onap_private_subnet_id", value=ONAP_PRIVATE_SUBNET),
       InstantiationParameter(name="pub_key", value="ssh-rsa    AAAAB3NzaC1yc2EAAAADAQABAAABAQDFBOB1Ea2yej68aqIQw10kEsVf+rNoxT39qrV8JvvTK2yhkniQka1t2oD9h6DlXOLM3HJ6nBegWjOasJmIbminKZ6wvmxZrDVFJXp9Sn1gni0vtEnlDgH14shRUrFDYO0PYjXRHoj7QXZMYxtAdFSbzGuCsaTLcV/xchLBQmqZ4AGhMIiYMfJJF+Ygy0lbgcVmT+8DH7kUUt8SAdh2rRsYFwpKANnQJyPV1dBNuTcD0OW1hEOhXnwqH28tjfb7uHJzTyGZlTmwTs544teTNz5B9L4yT3XiCAlMcaLOBMfBTKRIse+NkiTb+tc60JNnEYR6MqZoqTea/w+YBQaIMcil"),
       InstantiationParameter(name="image_name", value=IMAGE_NAME),
       InstantiationParameter(name="flavor_name", value=FLAVOR_NAME),
       InstantiationParameter(name="sec_group", value=TENANT_SEC_GROUP),
       InstantiationParameter(name="install_script_version", value="1.4.0-SNAPSHOT"),
       InstantiationParameter(name="demo_artifacts_version", value="1.4.0-SNAPSHOT"),
       InstantiationParameter(name="cloud_env", value=CLOUD_TYPE),
       InstantiationParameter(name="public_net_id", value=PUBLIC_NET),
       InstantiationParameter(name="aic-cloud-region", value=CLOUD_REGION)
    ]

    vnf_paras=VnfParameters("vfwcds_VF", vnf_vfw, 
              [base_paras, vpkg_paras, vsn_paras, vfw_paras])

    # You must define for each VNF and its vFModule the parameters, 
    # otherwise they stay empty.
    # The matching critera are:
    # - VnfParameters.name must match VNF ModelInstanceName
    #   (see above "vfwcds_VF")
    # - VfmoduleParameters.name must match substring in vfModule "instanceName"
    #   (e.g. "vfwcds_vf0..VfwcdsVf..vsn..module-1")
    logger.info("******** Instantiate Service *******")

    service_instantiation = ServiceInstantiation.instantiate_macro(
        service,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        vid_project,
        vid_line_of_business,
        vid_platform,
        service_instance_name=SERVICE_INSTANCE_NAME,
        vnf_parameters=[vnf_paras]
    )

    if service_instantiation.wait_for_finish():
        logger.info("Success")
    else:
        logger.error("Instantiation failed, check logs")
        exit(1)

    service_instance = None
    for se in service_subscription.service_instances:
       if se.instance_name == SERVICE_INSTANCE_NAME:
           service_instance = se
           break
    if not service_instance:
        logger.error("******** Service %s instantiation failed",SERVICE_INSTANCE_NAME)
        exit(1)

    if SERVICE_DELETION is False:
        logger.info("*****************************************")
        logger.info("**** No Deletion requested, finished ****")
        logger.info("*****************************************")
        exit(0)

    logger.info("*******************************")
    logger.info("**** SERVICE DELETION *********")
    logger.info("*******************************")
    time.sleep(30)

    logger.info("******** Delete Service %s *******",service_instance.name)
    service_deletion = service_instance.delete()

    nb_try = 0
    nb_try_max = 30
    while not service_deletion.finished and nb_try < nb_try_max:
        logger.info("Wait for Service deletion")
        nb_try += 1
        time.sleep(10)
    if service_deletion.finished:
        logger.info("Service %s deleted",service_instance.name)
    else:
        logger.error("Service deletion %s failed",service_instance.name)
        exit(1)

