"""AAI business module."""
from dataclasses import dataclass
from typing import Iterator
from urllib.parse import urlencode

from onapsdk.sdc.service import Service as SdcService
from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiElement, Relationship
from ..cloud_infrastructure.cloud_region import CloudRegion
from .service import ServiceInstance


@dataclass
class ServiceSubscriptionCloudRegionTenantData:
    """Dataclass to store cloud regions and tenants data for service subscription."""

    cloud_owner: str = None
    cloud_region_id: str = None
    tenant_id: str = None


@dataclass
class ServiceSubscription(AaiElement):
    """Service subscription class."""

    service_type: str
    resource_version: str
    customer: "Customer"

    def __init__(self, customer: "Customer", service_type: str, resource_version: str) -> None:
        """Service subscription object initialization.

        Args:
            customer (Customer): Customer object
            service_type (str): Service type
            resource_version (str): Service subscription resource version
        """
        super().__init__()
        self.customer: "Customer" = customer
        self.service_type: str = service_type
        self.resource_version: str = resource_version

    def _get_service_instance_by_filter_parameter(self,
                                                  filter_parameter_name: str,
                                                  filter_parameter_value: str) -> ServiceInstance:
        """Call a request to get service instance with given filter parameter and value.

        Args:
            filter_parameter_name (str): Name of parameter to filter
            filter_parameter_value (str): Value of filter parameter

        Raises:
            ValueError: Service instance with given filter parameters
                doesn't exist

        Returns:
            ServiceInstance: ServiceInstance object

        """
        service_instance: dict = self.send_message_json(
            "GET",
            f"Get service instance with {filter_parameter_value} {filter_parameter_name}",
            f"{self.url}/service-instances?{filter_parameter_name}={filter_parameter_value}",
            exception=ValueError
        )["service-instance"][0]
        return ServiceInstance(
            service_subscription=self,
            instance_id=service_instance.get("service-instance-id"),
            instance_name=service_instance.get("service-instance-name"),
            service_type=service_instance.get("service-type"),
            service_role=service_instance.get("service-role"),
            environment_context=service_instance.get("environment-context"),
            workload_context=service_instance.get("workload-context"),
            created_at=service_instance.get("created-at"),
            updated_at=service_instance.get("updated-at"),
            description=service_instance.get("description"),
            model_invariant_id=service_instance.get("model-invariant-id"),
            model_version_id=service_instance.get("model-version-id"),
            persona_model_version=service_instance.get("persona-model-version"),
            widget_model_id=service_instance.get("widget-model-id"),
            widget_model_version=service_instance.get("widget-model-version"),
            bandwith_total=service_instance.get("bandwidth-total"),
            vhn_portal_url=service_instance.get("vhn-portal-url"),
            service_instance_location_id=service_instance.get("service-instance-location-id"),
            resource_version=service_instance.get("resource-version"),
            selflink=service_instance.get("selflink"),
            orchestration_status=service_instance.get("orchestration-status"),
            input_parameters=service_instance.get("input-parameters")
        )

    @classmethod
    def create_from_api_response(cls,
                                 api_response: dict,
                                 customer: "Customer") -> "ServiceSubscription":
        """Create service subscription using API response dict.

        Returns:
            ServiceSubscription: ServiceSubscription object.

        """
        return cls(
            service_type=api_response.get("service-type"),
            resource_version=api_response.get("resource-version"),
            customer=customer
        )

    @property
    def url(self) -> str:
        """Cloud region object url.

        URL used to call CloudRegion A&AI API

        Returns:
            str: CloudRegion object url

        """
        return (
            f"{self.base_url}{self.api_version}/business/customers/"
            f"customer/{self.customer.global_customer_id}/service-subscriptions/"
            f"service-subscription/{self.service_type}"
        )

    @property
    def service_instances(self) -> Iterator[ServiceInstance]:
        """Service instances.

        Yields:
            Iterator[ServiceInstance]: Service instance

        """
        for service_instance in \
            self.send_message_json("GET",
                                   (f"Get all service instances for {self.service_type} service "
                                    f"subscription"),
                                   f"{self.url}/service-instances").get("service-instance", []):
            yield ServiceInstance(
                service_subscription=self,
                instance_id=service_instance.get("service-instance-id"),
                instance_name=service_instance.get("service-instance-name"),
                service_type=service_instance.get("service-type"),
                service_role=service_instance.get("service-role"),
                environment_context=service_instance.get("environment-context"),
                workload_context=service_instance.get("workload-context"),
                created_at=service_instance.get("created-at"),
                updated_at=service_instance.get("updated-at"),
                description=service_instance.get("description"),
                model_invariant_id=service_instance.get("model-invariant-id"),
                model_version_id=service_instance.get("model-version-id"),
                persona_model_version=service_instance.get("persona-model-version"),
                widget_model_id=service_instance.get("widget-model-id"),
                widget_model_version=service_instance.get("widget-model-version"),
                bandwith_total=service_instance.get("bandwidth-total"),
                vhn_portal_url=service_instance.get("vhn-portal-url"),
                service_instance_location_id=service_instance.get("service-instance-location-id"),
                resource_version=service_instance.get("resource-version"),
                selflink=service_instance.get("selflink"),
                orchestration_status=service_instance.get("orchestration-status"),
                input_parameters=service_instance.get("input-parameters")
            )

    @property
    def tenant_relationships(self) -> Iterator["Relationship"]:
        """Tenant related relationships.

        Iterate through relationships and get related to tenant.

        Yields:
            Relationship: Relationship related to tenant.

        """
        for relationship in self.relationships:
            if relationship.related_to == "tenant":
                yield relationship

    @property
    def cloud_region(self) -> "CloudRegion":
        """Cloud region associated with service subscription.

        IT'S DEPRECATED! `cloud_regions` parameter SHOULD BE USED

        Raises:
            AttributeError: Service subscription has no associated cloud region.

        Returns:
            CloudRegion: CloudRegion object

        """
        try:
            return next(self.cloud_regions)
        except StopIteration:
            raise AttributeError

    @property
    def tenant(self) -> "Tenant":
        """Tenant associated with service subscription.

        IT'S DEPRECATED! `tenants` parameter SHOULD BE USED

        Raises:
            AttributeError: Service subscription has no associated tenants

        Returns:
            Tenant: Tenant object

        """
        try:
            return next(self.tenants)
        except StopIteration:
            raise AttributeError

    @property
    def _cloud_regions_tenants_data(self) -> Iterator["ServiceSubscriptionCloudRegionTenantData"]:
        for relationship in self.tenant_relationships:
            cr_tenant_data: ServiceSubscriptionCloudRegionTenantData = \
                ServiceSubscriptionCloudRegionTenantData()
            for data in relationship.relationship_data:
                if data["relationship-key"] == "cloud-region.cloud-owner":
                    cr_tenant_data.cloud_owner = data["relationship-value"]
                if data["relationship-key"] == "cloud-region.cloud-region-id":
                    cr_tenant_data.cloud_region_id = data["relationship-value"]
                if data["relationship-key"] == "tenant.tenant-id":
                    cr_tenant_data.tenant_id = data["relationship-value"]
            if all([cr_tenant_data.cloud_owner,
                    cr_tenant_data.cloud_region_id,
                    cr_tenant_data.tenant_id]):
                yield cr_tenant_data
            else:
                self._logger.error("Invalid tenant relationship: %s", relationship)

    @property
    def cloud_regions(self) -> Iterator["CloudRegion"]:
        """Cloud regions associated with service subscription.

        Yields:
            CloudRegion: CloudRegion object

        """
        cloud_region_set: set = set()
        for cr_data in self._cloud_regions_tenants_data:
            cloud_region_set.add((cr_data.cloud_owner, cr_data.cloud_region_id))
        for cloud_region_data in cloud_region_set:
            try:
                yield CloudRegion.get_by_id(cloud_owner=cloud_region_data[0],
                                            cloud_region_id=cloud_region_data[1])
            except ValueError:
                self._logger.error("Can't get cloud region %s %s", cloud_region_data[0], \
                                                                   cloud_region_data[1])

    @property
    def tenants(self) -> Iterator["Tenant"]:
        """Tenants associated with service subscription.

        Yields:
            Tenant: Tenant object

        """
        for cr_data in self._cloud_regions_tenants_data:
            try:
                cloud_region: CloudRegion = CloudRegion.get_by_id(cr_data.cloud_owner,
                                                                  cr_data.cloud_region_id)
                yield cloud_region.get_tenant(cr_data.tenant_id)
            except ValueError:
                self._logger.error("Can't get %s tenant", cr_data.tenant_id)

    @property
    def sdc_service(self) -> "SdcService":
        """Sdc service.

        SDC service associated with service subscription.

        Returns:
            SdcService: SdcService object

        """
        return SdcService(self.service_type)

    def get_service_instance_by_id(self, service_instance_id) -> ServiceInstance:
        """Get service instance using it's ID.

        Args:
            service_instance_id (str): ID of the service instance

        Raises:
            ValueError: service subscription has no related service instance with given ID

        Returns:
            ServiceInstance: ServiceInstance object

        """
        return self._get_service_instance_by_filter_parameter(
            "service-instance-id",
            service_instance_id
        )

    def get_service_instance_by_name(self, service_instance_name: str) -> ServiceInstance:
        """Get service instance using it's name.

        Args:
            service_instance_name (str): Name of the service instance

        Raises:
            ValueError: service subscription has no related service instance with given name

        Returns:
            ServiceInstance: ServiceInstance object

        """
        return self._get_service_instance_by_filter_parameter(
            "service-instance-name",
            service_instance_name
        )

    def link_to_cloud_region_and_tenant(self,
                                        cloud_region: "CloudRegion",
                                        tenant: "Tenant") -> None:
        """Create relationship between object and cloud region with tenant.

        Args:
            cloud_region (CloudRegion): Cloud region to link to
            tenant (Tenant): Cloud region tenant to link to
        """
        relationship: Relationship = Relationship(
            related_to="tenant",
            related_link=tenant.url,
            relationship_data=[
                {
                    "relationship-key": "cloud-region.cloud-owner",
                    "relationship-value": cloud_region.cloud_owner,
                },
                {
                    "relationship-key": "cloud-region.cloud-region-id",
                    "relationship-value": cloud_region.cloud_region_id,
                },
                {
                    "relationship-key": "tenant.tenant-id",
                    "relationship-value": tenant.tenant_id,
                },
            ],
            related_to_property=[
                {"property-key": "tenant.tenant-name", "property-value": tenant.name}
            ],
        )
        self.add_relationship(relationship)


class Customer(AaiElement):
    """Customer class."""

    def __init__(self,
                 global_customer_id: str,
                 subscriber_name: str,
                 subscriber_type: str,
                 resource_version: str = None) -> None:
        """Initialize Customer class object.

        Args:
            global_customer_id (str): Global customer id used across ONAP to
                uniquely identify customer.
            subscriber_name (str): Subscriber name, an alternate way to retrieve a customer.
            subscriber_type (str): Subscriber type, a way to provide VID with
                only the INFRA customers.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update
                and delete. Defaults to None.

        """
        super().__init__()
        self.global_customer_id: str = global_customer_id
        self.subscriber_name: str = subscriber_name
        self.subscriber_type: str = subscriber_type
        self.resource_version: str = resource_version

    def __repr__(self) -> str:  # noqa
        """Customer description.

        Returns:
            str: Customer object description

        """
        return (f"Customer(global_customer_id={self.global_customer_id}, "
                f"subscriber_name={self.subscriber_name}, "
                f"subscriber_type={self.subscriber_type}, "
                f"resource_version={self.resource_version})")

    def get_service_subscription_by_service_type(self, service_type: str) -> ServiceSubscription:
        """Get subscribed service by service type.

        Call a request to get service subscriptions filtered by service-type parameter.

        Args:
            service_type (str): Service type

        Raises:
            ValueError: No service subscription with given service-type.

        Returns:
            ServiceSubscription: Service subscription

        """
        response: dict = self.send_message_json(
            "GET",
            f"Get service subscription with {service_type} service type",
            (f"{self.base_url}{self.api_version}/business/customers/"
             f"customer/{self.global_customer_id}/service-subscriptions"
             f"?service-type={service_type}"),
            exception=ValueError
        )
        return ServiceSubscription.create_from_api_response(response["service-subscription"][0],
                                                            self)

    @classmethod
    def get_all(cls,
                global_customer_id: str = None,
                subscriber_name: str = None,
                subscriber_type: str = None) -> Iterator["Customer"]:
        """Get all customers.

        Call an API to retrieve all customers. It can be filtered
            by global-customer-id, subscriber-name and/or subsriber-type.

        Args:
            global_customer_id (str): global-customer-id to filer customers by. Defaults to None.
            subscriber_name (str): subscriber-name to filter customers by. Defaults to None.
            subscriber_type (str): subscriber-type to filter customers by. Defaults to None.

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "global-customer-id": global_customer_id,
                "subscriber-name": subscriber_name,
                "subscriber-type": subscriber_type,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/business/customers?"
                    f"{urlencode(filter_parameters)}")
        for customer in cls.send_message_json("GET", "get customers", url).get("customer", []):
            yield Customer(
                global_customer_id=customer["global-customer-id"],
                subscriber_name=customer["subscriber-name"],
                subscriber_type=customer["subscriber-type"],
                resource_version=customer["resource-version"],
            )

    @classmethod
    def get_by_global_customer_id(cls, global_customer_id: str) -> "Customer":
        """Get customer by it's global customer id.

        Args:
            global_customer_id (str): global customer ID

        Returns:
            Customer: Customer with given global_customer_id

        Raises:
            ValueError: Customer with given global_customer_id doesn't exist

        """
        response: dict = cls.send_message_json(
            "GET",
            f"Get {global_customer_id} customer",
            f"{cls.base_url}{cls.api_version}/business/customers/customer/{global_customer_id}",
            exception=ValueError
        )
        return Customer(
            global_customer_id=response["global-customer-id"],
            subscriber_name=response["subscriber-name"],
            subscriber_type=response["subscriber-type"],
            resource_version=response["resource-version"],
        )

    @classmethod
    def create(cls,
               global_customer_id: str,
               subscriber_name: str,
               subscriber_type: str) -> "Customer":
        """Create customer.

        Args:
            global_customer_id (str): Global customer id used across ONAP
                to uniquely identify customer.
            subscriber_name (str): Subscriber name, an alternate way
                to retrieve a customer.
            subscriber_type (str): Subscriber type, a way to provide
                VID with only the INFRA customers.

        Returns:
            Customer: Customer object.

        """
        url: str = (
            f"{cls.base_url}{cls.api_version}/business/customers/"
            f"customer/{global_customer_id}"
        )
        cls.send_message(
            "PUT",
            "declare customer",
            url,
            data=jinja_env()
            .get_template("customer_create.json.j2")
            .render(
                global_customer_id=global_customer_id,
                subscriber_name=subscriber_name,
                subscriber_type=subscriber_type,
            ),
        )
        response: dict = cls.send_message_json(
            "GET", "get created customer", url
        )  # Call API one more time to get Customer's resource version
        return Customer(
            global_customer_id=response["global-customer-id"],
            subscriber_name=response["subscriber-name"],
            subscriber_type=response["subscriber-type"],
            resource_version=response["resource-version"],
        )

    @property
    def url(self) -> str:
        """Return customer object url.

        Unique url address to get customer's data.

        Returns:
            str: Customer object url

        """
        return (
            f"{self.base_url}{self.api_version}/business/customers/customer/"
            f"{self.global_customer_id}?resource-version={self.resource_version}"
        )

    @property
    def service_subscriptions(self) -> Iterator[ServiceSubscription]:
        """Service subscriptions of customer resource.

        Yields:
            ServiceSubscription: ServiceSubscription object

        """
        response: dict = self.send_message_json(
            "GET",
            "get customer service subscriptions",
            f"{self.base_url}{self.api_version}/business/customers/"
            f"customer/{self.global_customer_id}/service-subscriptions"
        )
        for service_subscription in response.get("service-subscription", []):
            yield ServiceSubscription.create_from_api_response(
                service_subscription,
                self
            )

    def subscribe_service(self, service: SdcService) -> "ServiceSubscription":
        """Create SDC Service subscription.

        If service is already subscribed it won't create a new resource but use the
            existing one.

        Args:
            service (SdcService): SdcService object to subscribe.

        Raises:
            ValueError: Request response with HTTP error code

        """
        try:
            return self.get_service_subscription_by_service_type(service.name)
        except ValueError:
            self._logger.info("Create service subscription for %s customer",
                              self.global_customer_id)
        self.send_message(
            "PUT",
            "Create service subscription",
            (f"{self.base_url}{self.api_version}/business/customers/"
             f"customer/{self.global_customer_id}/service-subscriptions/"
             f"service-subscription/{service.name}"),
            data=jinja_env()
            .get_template("customer_service_subscription_create.json.j2")
            .render(
                service_id=service.unique_uuid,
            ),
            exception=ValueError
        )
        return self.get_service_subscription_by_service_type(service.name)
