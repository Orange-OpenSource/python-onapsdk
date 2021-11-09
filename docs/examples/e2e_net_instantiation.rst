E2E Instantiation of a simple Network
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
        ServiceSubscription,
        Customer,
        OwningEntity as AaiOwningEntity
    )
    from onapsdk.so.instantiation import (
        ServiceInstantiation,
        Subnet
    )
    from onapsdk.sdc.service import Service
    from onapsdk.sdc.vl import Vl
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
    VL_NAME = "Generic NeutronNet"
    SERVICENAME = "net_SERVICE"

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

    SERVICE_INSTANCE_NAME = "net-Instance"
    SERVICE_DELETION = True

    logger.info("*******************************")
    logger.info("******** SERVICE DESIGN *******")
    logger.info("*******************************")

    logger.info("******** Get VL *******")
    vl = Vl(VL_NAME)

    logger.info("******** Onboard Service *******")
    svc = Service(name=SERVICENAME, resources=[vl])
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
        customer.subscribe_service(SERVICENAME)

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


    logger.info("******** Get Networks in Service Model *******")
    networks = service_instance.service_subscription.sdc_service.networks

    logger.info("******** Create Network *******")
    sn=Subnet(name="test", start_address="127.0.0.0", gateway_address="127.0.0.1")
    for network in networks:
        logger.debug("Check if Network instance of class %s exist", network.name)
        network_found = False
        for network_instance in service_instance.network_instances:
            logger.debug("Network instance %s found in Service Instance ",network_intance.name)
            network_found = True
        if network_found is False:
            network_instantiation = service_instance.add_network(network, vid_line_of_business, vid_platform, subnets=[sn])
            network_instantiation.wait_for_finish()


    if SERVICE_DELETION is False:
        logger.info("*****************************************")
        logger.info("**** No Deletion requested, finished ****")
        logger.info("*****************************************")
        exit(0)

    logger.info("*******************************")
    logger.info("**** SERVICE DELETION *********")
    logger.info("*******************************")
    time.sleep(30)

    for network_instance in service_instance.network_instances:
        logger.debug("Network instance %s found in Service Instance ",network_instance.name)

        logger.info("******** Delete Network %s *******",network_instance.name)
        network_deletion = network_instance.delete()
        network_deletion.wait_for_finish()

    logger.info("******** Delete Service %s *******",service_instance.name)
    service_deletion = service_instance.delete()
    service_deletion.wait_for_finish()


