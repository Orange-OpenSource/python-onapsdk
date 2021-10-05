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

Instantiate a service (ALaCarte)
--------------------------------

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
    SERVICE_INSTANCE_NAME = "vFW-AlaCarte-1"

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
    service_instantiation.wait_for_finish():
        print("Success")
    else:
        print("Instantiation failed, check logs")

Instantiate a service (Macro)
-----------------------------

.. code:: Python

    import time
    from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
    from onapsdk.aai.business import Customer
    from onapsdk.service import Service
    from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project
    from onapsdk.so.instantiation import (
        ServiceInstantiation,
        VnfInstantiation,
        InstantiationParameter,
        VnfParameters,
        VfmoduleParameters
    )
    
    ...
    VSPNAME = "vfwcds_VS"
    VFNAME = "vfwcds_VF"
    ...
    vf = Vf(name=VFNAME)
    ...
    
    # We assume that:
    #   - service is onboarded,
    #   - cloud region, customer, owning_entity and project have been already created,
    #   - cloud region has at least one tenant
    #   - customer has service subscription
    #   - service subscription is connected with cloud region and tenant
    SERVICE_INSTANCE_NAME = "vFW-Macro-1"

    service = Service(name="myMacroService")
    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    tenant = next(cloud_region.tenants)
    vid_owning_entity = OwningEntity(OWNING_ENTITY)
    owning_entity = AaiOwningEntity.get_by_owning_entity_name(OWNING_ENTITY)
    vid_project = Project(PROJECT)

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
       InstantiationParameter(name="pub_key", value="ssh-rsa AAAAB3NzaC1yc2EAA\
    AADAQABAAABAQDFBOB1Ea2yej68aqIQw10kEsVf+rNoxT39qrV8JvvTK2yhkniQka1t2oD9h6DlXOL\
    M3HJ6nBegWjOasJmIbminKZ6wvmxZrDVFJXp9Sn1gni0vtEnlDgH14shRUrFDYO0PYjXRHoj7QXZMY\
    xtAdFSbzGuCsaTLcV/xchLBQmqZ4AGhMIiYMfJJF+Ygy0lbgcVmT+8DH7kUUt8SAdh2rRsYFwpKANn\
    QJyPV1dBNuTcD0OW1hEOhXnwqH28tjfb7uHJzTyGZlTmwTs544teTNz5B9L4yT3XiCAlMcaLOBMfBT\
    KRIse+NkiTb+tc60JNnEYR6MqZoqTea/w+YBQaIMcil"),
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

    service_instantiation.wait_for_finish():
        print("Success")
    else:
        print("Instantiation failed, check logs")

Instantiate a service using SO service template (Macro)
-------------------------------------------------------

To provide more control on the SO macro instantiation, you can define your service as follows:

.. code:: Yaml

    myservice:
        subscription_service_type: myservice
        vnfs:
            - model_name: myvfmodel
              vnf_name: myfirstvnf
              parameters:
                  param1: value1
              processing_priority: 1
              vf_modules:
                  - vf_module_name: mysecondvfm
                    model_name: base
                    processing_priority: 2
                    parameters:
                        param-vfm1: value-vfm1
                  - vf_module_name: myfirstvfm
                    model_name: base
                    processing_priority: 1
                    parameters:
                        param-vfm1: value-vfm1
            - model_name: myvfmodel
              vnf_name: mysecondvnf
              parameters:
                  param1: value1
              processing_priority: 2
              vf_modules:
                  - vf_module_name: myfirstvfm
                    model_name: base
                    processing_priority: 1
                    parameters:
                        param-vfm1: value-vfm1
                  - vf_module_name: mysecondvfm
                    model_name: base
                    processing_priority: 2
                    parameters:
                        param-vfm1: value-vfm1

.. code:: Python

    from onapsdk.aai.business import Customer, OwningEntity, Project, LineOfBusiness, Platform
    from onapsdk.aai.cloud_infrastructure import CloudRegion
    from onapsdk.sdc.service import Service
    from onapsdk.so.instantiation import ServiceInstantiation
    from yaml import load

    so_yaml_service = "/path/to/yaml/service"
    with open(so_yaml_service, "r") as yaml_template:
        so_service = load(yaml_template)

    # We assume that:
    #   - service is onboarded,
    #   - cloud region, customer, owning_entity and project have been already created,
    #   - cloud region has at least one tenant
    #   - customer has service subscription
    #   - service subscription is connected with cloud region and tenant

    service = Service(next(so_service.keys()))
    SERVICE_INSTANCE_NAME = "my_svc_instance_name"

    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    tenant = next(cloud_region.tenants)
    owning_entity = OwningEntity(OWNING_ENTITY)
    project = Project(PROJECT)
    line_of_business = LineOfBusiness(LINE_OF_BUSINESS)
    platform = Platform(PLATFORM)

    service_instantiation = ServiceInstantiation.instantiate_macro(
        sdc_service=service,
        customer=customer,
        owning_entity=owning_entity,
        project=project,
        line_of_business=line_of_business,
        platform=platform,
        cloud_region=cloud_region,
        tenant=tenant,
        service_instance_name=SERVICE_INSTANCE_NAME,
        so_service=so_service
    )

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
    vnf_instantiation.wait_for_finish():
        print("Success")
    else:
        print("Instantiation failed, check logs")

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
    vf_module_instantiation.wait_for_finish():
        print("Success")
    else:
        print("Instantiation failed, check logs")

Instantiate Vl module
---------------------

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

    logger.info("******** Get 1st Network in Service Model *******")
    network = service_subscription.sdc_service.networks[0]

    logger.info("******** Create Network *******")
    sn=Subnet(name="my_subnet",
              start_address="10.0.0.1",
              cidr_mask="24",
              gateway_address="10.0.0.1)

    vid_line_of_business = LineOfBusiness.create(LINE_OF_BUSINESS)
    vid_platform = Platform.create(PLATFORM)

    network_instantiation = service_instance.add_network(network, vid_line_of_business,
                            vid_platform, network_instance_name="my_net", subnets=[sn])

    if network_instantiation.wait_for_finish():
        print("Success")
    else:
        print("Instantiation failed, check logs")
