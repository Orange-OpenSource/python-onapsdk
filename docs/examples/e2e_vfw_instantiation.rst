E2E Instantiation of vFW (a'la carte)
#####################################


.. code:: Python

    import logging
    import time
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
        VnfParameter
    )
    from onapsdk.sdc import SDC
    from onapsdk.sdc.vendor import Vendor
    from onapsdk.sdc.vsp import Vsp
    from onapsdk.sdc.vf import Vf
    from onapsdk.sdc.service import Service
    import onapsdk.constants as const
    import os
    from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project

    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    fh = logging.StreamHandler()
    fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)



    # Create required A&AI resources
    VENDOR = "VNFVendor"
    VSPFILE = "vsp/vfw.zip"
    VSPNAME = "vfw_VSP"
    VFNAME = "vfw_VF"
    SERVICENAME = "vfw_SERVICE"

    GLOBAL_CUSTOMER_ID = ""  # FILL ME
    COMPLEX_PHYSICAL_LOCATION_ID = ""  # FILL ME
    COMPLEX_DATA_CENTER_CODE = ""  # FILL ME

    CLOUD_OWNER = ""  # FILL ME
    CLOUD_REGION = ""  # FILL ME

    VIM_USERNAME = ""  # FILL ME
    VIM_PASSWORD = ""  # FILL ME
    VIM_SERVICE_URL = ""  # FILL ME

    TENANT_NAME = ""  # FILL ME
    OWNING_ENTITY = ""  # FILL ME
    PROJECT = ""  # FILL ME
    PLATFORM = ""  # FILL ME
    LINE_OF_BUSINESS = ""  # FILL ME

    SERVICE_INSTANCE_NAME = "vFW-Instance"
    SERVICE_DELETION = True

    logger.info("*******************************")
    logger.info("******** SERVICE DESIGN *******")
    logger.info("*******************************")

    logger.info("******** Onboard Vendor *******")
    vendor = Vendor(name=VENDOR)
    vendor.onboard()

    logger.info("******** Onboard VSP *******")
    mypath = os.path.dirname(os.path.realpath(__file__))
    myvspfile = os.path.join(mypath, VSPFILE)
    vsp = Vsp(name=VSPNAME, vendor=vendor, package=open(myvspfile, 'rb'))
    vsp.onboard()

    logger.info("******** Onboard VF *******")
    vf = Vf(name=VFNAME)
    vf.vsp = vsp
    vf.onboard()

    logger.info("******** Onboard Service *******")
    svc = Service(name=SERVICENAME, resources=[vf])
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
        cloud_type="openstack",
        cloud_region_version="titanium_cloud",
        cloud_zone="z1",
        complex_name=COMPLEX_PHYSICAL_LOCATION_ID
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
    registration_completed = False
    nb_try = 0
    nb_try_max = 10
    while registration_completed is False and nb_try < nb_try_max:
        for tenant in cloud_region.tenants:
            logger.debug("Tenant %s found in %s_%s",tenant.name,cloud_region.cloud_owner,cloud_region.cloud_region_id)
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
        logger.debug("Service %s is found, distribution %s",found_service.name, found_service.distribution_status)
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
        customer.subscribe_service(service, "service_type")

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

    logger.info("******** Instantiate Service *******")
    service_instance = None
    service_instantiation = None
    for se in service_subscription.service_instances:
       if se.instance_name == SERVICE_INSTANCE_NAME:
           service_instance = se
           break
    if not service_instance:
        logger.info("******** Service Instance not existing: Instantiate *******")
        # Instantiate service
        service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
            service,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            vid_project,
            service_instance_name=SERVICE_INSTANCE_NAME
        )
        time.sleep(60)
    else:
        logger.info("******** Service Instance already existing *******")

    service_instance = None
    for se in service_subscription.service_instances:
       if se.instance_name == SERVICE_INSTANCE_NAME:
           service_instance = se
           break
    if not service_instance:
        logger.error("******** Service %s instantiation failed",SERVICE_INSTANCE_NAME)
        exit(1)

    nb_try = 0
    nb_try_max = 10
    service_active = False
    while service_active is False and nb_try < nb_try_max:
        if service_instance.orchestration_status == "Active":
           logger.info("******** Service Instance %s is active *******",service_instance.name)
           service_active = True
           break
        logger.info("Service %s instantiation not complete,Status:%s, wait 10s",service_instance.name,service_instance.orchestration_status)
        time.sleep(10)
        nb_try += 1

    if service_active is False:
        logger.error("Service %s instantiation failed",service_instance.name)
        exit(1)


    logger.info("******** Get VNFs in Service Model *******")
    vnfs = service_instance.service_subscription.sdc_service.vnfs

    logger.info("******** Create VNFs *******")
    for vnf in vnfs:
        logger.debug("Check if VNF instance of class %s exist", vnf.name)
        vnf_found = False
        for vnf_instance in service_instance.vnf_instances:
            logger.debug("VNF instance %s found in Service Instance ",vnf_instance.name)
            vnf_found = True
        if vnf_found is False:
            vnf_instantiation = service_instance.add_vnf(vnf, vid_line_of_business, vid_platform)
            while not vnf_instantiation.finished:
                print("Wait for VNF %s instantiation",vnf.name)
                time.sleep(10)


    for vnf_instance in service_instance.vnf_instances:
        logger.debug("VNF instance %s found in Service Instance ",vnf_instance.name)
        logger.info("******** Get VfModules in VNF Model *******")
        logger.info("******** Check VF Modules *******")
        vf_module = vnf_instance.vnf.vf_module

        logger.info("******** Create VF Module %s *******",vf_module.name)

        vf_module_instantiation = vnf_instance.add_vf_module(
                                   vf_module,
                                   vnf_parameters=[
                                     VnfParameter(name="vfw_image_name", value="Ubuntu_1404"),
                                     VnfParameter(name="vpg_image_name", value="Ubuntu_1404"),
                                     VnfParameter(name="vsn_image_name", value="Ubuntu_1404"),
                                     VnfParameter(name="vfw_flavor_name", value="m1.small"),
                                     VnfParameter(name="vpg_flavor_name", value="m1.small"),
                                     VnfParameter(name="vsn_flavor_name", value="m1.small"),
                                     VnfParameter(name="public_net_id", value="admin"),
                                     VnfParameter(name="onap_private_net_id", value="admin"),
                                     VnfParameter(name="onap_private_subnet_id", value="admin-subnet"),
                                     VnfParameter(name="onap_private_net_cidr", value="10.41.1.0/24"),
                                     VnfParameter(name="vfw_onap_private_ip_0", value="10.41.1.10"),
                                     VnfParameter(name="vpg_onap_private_ip_0", value="10.41.1.11"),
                                     VnfParameter(name="vsn_onap_private_ip_0", value="10.41.1.12"),
                                     VnfParameter(name="sec_group", value="ci-onap-master-vnfs-onap")
                                     ]
                                  )
        nb_try = 0
        nb_try_max = 30
        while not vf_module_instantiation.finished and nb_try < nb_try_max:
            logger.info("Wait for vf module instantiation")
            nb_try += 1
            time.sleep(10)
        if vf_module_instantiation.finished:
            logger.info("VfModule %s instantiated",vf_module.name)
        else:
            logger.error("VfModule instantiation %s failed",vf_module.name)

    if SERVICE_DELETION is False:
        logger.info("*****************************************")
        logger.info("**** No Deletion requested, finished ****")
        logger.info("*****************************************")
        exit(0)

    logger.info("*******************************")
    logger.info("**** SERVICE DELETION *********")
    logger.info("*******************************")
    time.sleep(30)

    for vnf_instance in service_instance.vnf_instances:
        logger.debug("VNF instance %s found in Service Instance ",vnf_instance.name)
        logger.info("******** Get VF Modules *******")
        for vf_module in vnf_instance.vf_modules:
            logger.info("******** Delete VF Module %s *******",vf_module.name)
            vf_module_deletion = vf_module.delete()

            nb_try = 0
            nb_try_max = 30
            while not vf_module_deletion.finished and nb_try < nb_try_max:
                logger.info("Wait for vf module deletion")
                nb_try += 1
                time.sleep(10)
            if vf_module_deletion.finished:
                logger.info("VfModule %s deleted",vf_module.name)
            else:
                logger.error("VfModule deletion %s failed",vf_module.name)
                exit(1)

        logger.info("******** Delete VNF %s *******",vnf_instance.name)
        vnf_deletion = vnf_instance.delete()

        nb_try = 0
        nb_try_max = 30
        while not vnf_deletion.finished and nb_try < nb_try_max:
            logger.info("Wait for vnf deletion")
            nb_try += 1
            time.sleep(10)
        if vnf_deletion.finished:
            logger.info("VNF %s deleted",vnf_instance.name)
        else:
            logger.error("VNF deletion %s failed",vnf_instance.name)
            exit(1)

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

