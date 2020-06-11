Instantiated resources deletion
###############################

Service, vnf and vf module deletion
-----------------------------------

.. code:: Python

    from onapsdk.aai.business import Customer

    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    service_subscription = next(customer.service_subscriptions)
    service_instance = service_subscription.get_service_instance_by_name(SERVICE_INSTANCE_NAME)
    for vnf_instance in service_instance.vnf_instances:
        for vf_module_instance in vnf_instance.vf_modules:
            vf_module_deletion_request = vf_module_instance.delete()
            while not vf_module_deletion.finished:
                time.sleep(10)

        vnf_instance_deletion_request = vnf_instance.delete()
        while not vnf_instance_deletion_request.finished:
            time.sleep(10)

    service_instance_deletion_request = service_instance.delete()
    while not service_instance_deletion_request.finished:
        time.sleep(10)
