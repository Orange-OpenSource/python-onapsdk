Instantiation
#############

Create business objects
-----------------------

.. code:: Python

    from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project

    vid_owning_entity = OwningEntity.create(OWNING_ENTITY)
    vid_project = Project.create(PROJECT)
    vid_platform = Platform.create(PLATFORM)
    vid_line_of_business = LineOfBusiness.create(LINE_OF_BUSINESS)

Instantiate a service
---------------------

.. code:: Python

    import time
    from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
    from onapsdk.aai.business import Customer
    from onapsdk.service import Service
    from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project
    from onapsdk.so.instantiation import ServiceInstantiation

    # We assume that:
    #   - service is onboarded,
    #   - cloud region, customer, owning_entity and project have been already created,
    #   - cloud region has at least one tenant
    #   - customer has service subscription
    #   - service subscription is connected with cloud region and tenant

    service = Service(name="myService")
    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    tenant = next(cloud_region.tenants)
    vid_owning_entity = OwningEntity(OWNING_ENTITY)
    owning_entity = AaiOwningEntity.get_by_owning_entity_name(OWNING_ENTITY)
    vid_project = Project(PROJECT)

    service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
        service,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        vid_project,
        service_instance_name=SERVICE_INSTANCE_NAME
    )
    while not service_instantiation.finished:
        time.sleep(10)

Instantiate VNF
---------------

.. code:: Python

    import time
    from onapsdk.aai.business import Customer
    from onapsdk.vid import LineOfBusiness, Platform

    # We assume that
    #   - service has been already instantiated,
    #   - line of business and platform are created

    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    service_subscription = next(customer.service_subscriptions)
    service_instance = service_subscription.get_service_instance_by_name(SERVICE_INSTANCE_NAME)
    vnf = service_subscription.sdc_service.vnfs[0]
    vid_line_of_business = LineOfBusiness.create(LINE_OF_BUSINESS)
    vid_platform = Platform.create(PLATFORM)
    vnf_instantiation = service_instance.add_vnf(vnf, vid_line_of_business, vid_platform)
    while not vnf_instantiation.finished:
        time.sleep(10)

Instantiate Vf module
---------------------

.. code:: Python

    import time
    from onapsdk.aai.business import Customer

    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    service_subscription = next(customer.service_subscriptions)
    service_instance = service_subscription.get_service_instance_by_name(SERVICE_INSTANCE_NAME)
    vnf_instance = next(service_instance.vnf_instances)
    vf_module = vnf_instance.vnf.vf_module
    vf_module_instantiation = vnf_instance.add_vf_module(
        vf_module,
        vnf_parameters=[
            VnfParameter(name="parameter1", value="parameter1_value"),
            VnfParameter(name="parameter2", value="parameter2_value
        ]
    )
    while not vf_module_instantiation.finished:
        time.sleep(10)
