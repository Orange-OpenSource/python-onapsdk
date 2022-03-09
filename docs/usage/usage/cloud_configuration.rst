Cloud configuration
###################

Create a complex
----------------

.. code:: Python

    from onapsdk.aai.cloud_infrastructure import Complex
    cmplx = Complex.create(
        physical_location_id=COMPLEX_PHYSICAL_LOCATION_ID,
        data_center_code=COMPLEX_DATA_CENTER_CODE,
        name=COMPLEX_PHYSICAL_LOCATION_ID
    )

Create cloud region
-------------------

.. code:: Python

    from onapsdk.aai.cloud_infrastructure import CloudRegion
    cloud_region = CloudRegion.create(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION,
        orchestration_disabled=False,
        in_maint=False,
        cloud_type=CLOUD_TYPE,
        cloud_region_version=CLOUD_REGION_VERSION
    )

Link cloud region to complex
----------------------------

.. code:: Python

    from onapsdk.aai.cloud_infrastructure import CloudRegion, Complex
    # We assume that complex has been already created
    cmplx = Complex(
        physical_location_id=COMPLEX_PHYSICAL_LOCATION_ID,
        name=COMPLEX_PHYSICAL_LOCATION_ID
    )
    cloud_region = CloudRegion.create(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION,
        orchestration_disabled=False,
        in_maint=False,
        cloud_type=CLOUD_TYPE,
        cloud_region_version=CLOUD_REGION_VERSION
    )
    cloud_region.link_to_complex(cmplx)

Add ESR Info to cloud region
----------------------------

.. code:: Python

    from uuid import uuid4
    from onapsdk.aai.cloud_infrastructure import CloudRegion
    # We assume that cloud region has been already created
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    cloud_region.add_esr_system_info(
        esr_system_info_id=str(uuid4()),
        user_name=VIM_USERNAME,
        password=VIM_PASSWORD,
        system_type=CLOUD_TYPE,
        service_url=VIM_SERVICE_URL,
        cloud_domain=CLOUD_DOMAIN
    )

Register cloud to MultiCloud
----------------------------

.. code:: Python

    from uuid import uuid4
    from onapsdk.aai.cloud_infrastructure import CloudRegion
    # We assume that cloud region has been already created
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    cloud_region.add_esr_system_info(
        esr_system_info_id=str(uuid4()),
        user_name=VIM_USERNAME,
        password=VIM_PASSWORD,
        system_type=CLOUD_TYPE,
        service_url=VIM_SERVICE_URL,
        cloud_domain=CLOUD_DOMAIN
    )
    cloud_region.register_to_multicloud()

Get cloud region tenant
-----------------------

.. code:: Python

    # We assume that cloud region has been already created
    # and connected to multicloud
    from onapsdk.aai.cloud_infrastructure import CloudRegion
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    try:
        tenant = next(cloud_region.tenant)
    except StopIteration
        # No Tenant found in cloud region

Create customer
---------------

.. code:: Python

    from onapsdk.aai.business import Customer
    customer = Customer.create(GLOBAL_CUSTOMER_ID, GLOBAL_CUSTOMER_ID, "INFRA")

Create customer service subscription
------------------------------------

.. code:: Python

    # We assume here that the service has been already onboarded
    # and customer created
    from onapsdk.aai.business import Customer

    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    customer.subscribe_service("service_type")

    # Service subscriptions can be also created during Customer
    # creation
    from onapsdk.aai.business import Customer

    customer = Customer.create(GLOBAL_CUSTOMER_ID, GLOBAL_CUSTOMER_ID, "INFRA", service_subscriptions=["service_type"])

Connect service subscription to cloud region and tenant
-------------------------------------------------------

.. code:: Python

    # We assume here that the service subscription has been already created
    # and cloud region has a tenant
    from onapsdk.aai.business import Customer
    from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant

    customer = Customer.get_by_global_customer_id(GLOBAL_CUSTOMER_ID)
    service_subscription = next(customer.service_subscriptions)
    cloud_region = CloudRegion.get_by_id(
        cloud_owner=CLOUD_OWNER,
        cloud_region_id=CLOUD_REGION
    )
    tenant = next(cloud_region.tenants)
    service_subscription.link_to_cloud_region_and_tenant(cloud_region, tenant)

Add Cloud SIte entry to SO Catalog DB
-------------------------------------------------------

.. code:: Python

    from onapsdk.so.so_db_adapter import IdentityService, SoDbAdapter

    identity_service = IdentityService(identity_id="mc_test_identity_1_KEYSTONE",
                                       url="http://test:5000/v3",
                                       mso_id="test_user",
                                       mso_pass="test_password_encrypted",
                                       roject_domain_name="Default",
                                       user_domain_name="Default",
                                       identity_server_type="KEYSTONE_V3")
    response = SoDbAdapter.add_cloud_site(cloud_region_id="test_region_1",
                                          complex_id="test_clli_1",
                                          identity_service=identity_service,
                                          orchestrator="NULL")

Use A&AI bulk API (experimental)
--------------------------------

.. code:: Python

    from onapsdk.aai.bulk import AaiBulk, AaiBulkRequest
    from onapsdk.aai.cloud_infrastructure.cloud_region import CloudRegion
    from onapsdk.utils.jinja import jinja_env


    for resp in AaiBulk.single_transaction(
        [
            AaiBulkRequest(
                action="put",
                uri=f"/cloud-infrastructure/cloud-regions/cloud-region/aai_bulk_test_cloud_owner_1/aai_bulk_test_cloud_region_id_1",
                body=jinja_env().get_template("cloud_region_create.json.j2").render(cloud_region=CloudRegion(
                        cloud_owner="aai_bulk_test_cloud_owner_1",
                        cloud_region_id="aai_bulk_test_cloud_region_id_1",
                        orchestration_disabled=False,
                        in_maint=False
                    ))
            ),
            AaiBulkRequest(
                action="put",
                uri=f"/cloud-infrastructure/cloud-regions/cloud-region/aai_bulk_test_cloud_owner_2/aai_bulk_test_cloud_region_id_2",
                body=jinja_env().get_template("cloud_region_create.json.j2").render(cloud_region=CloudRegion(
                        cloud_owner="aai_bulk_test_cloud_owner_2",
                        cloud_region_id="aai_bulk_test_cloud_region_id_2",
                        orchestration_disabled=False,
                        in_maint=False
                    ))
            )
        ]
    ):
        print(resp)
