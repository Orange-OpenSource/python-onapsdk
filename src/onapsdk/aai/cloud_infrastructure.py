"""AAI cloud-infrastructure module."""
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlencode

from onapsdk.multicloud import Multicloud
from onapsdk.utils.jinja import jinja_env

from .aai_element import AaiElement, Relationship


class Complex(AaiElement):  # pylint: disable=R0902
    """Complex class.

    Collection of physical locations that can house cloud-regions.
    """

    def __init__(self,  # pylint: disable=R0914
                 name: str,
                 physical_location_id: str,
                 *,
                 data_center_code: str = "",
                 identity_url: str = "",
                 resource_version: str = "",
                 physical_location_type: str = "",
                 street1: str = "",
                 street2: str = "",
                 city: str = "",
                 state: str = "",
                 postal_code: str = "",
                 country: str = "",
                 region: str = "",
                 latitude: str = "",
                 longitude: str = "",
                 elevation: str = "",
                 lata: str = "") -> None:
        """Complex object initialization.

        Args:
            name (str): complex name
            physical_location_id (str): complex ID
            data_center_code (str, optional): complex data center code. Defaults to "".
            identity_url (str, optional): complex identity url. Defaults to "".
            resource_version (str, optional): complex resource version. Defaults to "".
            physical_location_type (str, optional): complex physical location type. Defaults to "".
            street1 (str, optional): complex address street part one. Defaults to "".
            street2 (str, optional): complex address street part two. Defaults to "".
            city (str, optional): complex address city. Defaults to "".
            state (str, optional): complex address state. Defaults to "".
            postal_code (str, optional): complex address postal code. Defaults to "".
            country (str, optional): complex address country. Defaults to "".
            region (str, optional): complex address region. Defaults to "".
            latitude (str, optional): complex geographical location latitude. Defaults to "".
            longitude (str, optional): complex geographical location longitude. Defaults to "".
            elevation (str, optional): complex elevation. Defaults to "".
            lata (str, optional): complex lata. Defaults to "".

        """
        super().__init__()
        self.name: str = name
        self.physical_location_id: str = physical_location_id
        self.data_center_code: str = data_center_code
        self.identity_url: str = identity_url
        self.resource_version: str = resource_version
        self.physical_location_type: str = physical_location_type
        self.street1: str = street1
        self.street2: str = street2
        self.city: str = city
        self.state: str = state
        self.postal_code: str = postal_code
        self.country: str = country
        self.region: str = region
        self.latitude: str = latitude
        self.longitude: str = longitude
        self.elevation: str = elevation
        self.lata: str = lata

    def __repr__(self) -> str:
        """Complex object description.

        Returns:
            str: Complex object description

        """
        return (f"Complex(name={self.name}, physical_location_id={self.physical_location_id}, "
                f"resource_version={self.resource_version})")

    @property
    def url(self) -> str:
        """Complex url.

        Returns:
            str: Complex url

        """
        return (f"{self.base_url}{self.api_version}/cloud-infrastructure/complexes/complex/"
                f"{self.physical_location_id}?resource-version={self.resource_version}")

    @classmethod
    def create(cls,  # pylint: disable=R0914
               name: str,
               physical_location_id: str,
               *,
               data_center_code: str = "",
               identity_url: str = "",
               resource_version: str = "",
               physical_location_type: str = "",
               street1: str = "",
               street2: str = "",
               city: str = "",
               state: str = "",
               postal_code: str = "",
               country: str = "",
               region: str = "",
               latitude: str = "",
               longitude: str = "",
               elevation: str = "",
               lata: str = "") -> "Complex":
        """Create complex.

        Create complex object by calling A&AI API.
        If API request doesn't fail it returns Complex object.

        Returns:
            Complex: Created complex object

        """
        complex_object: Complex = Complex(
            name=name,
            physical_location_id=physical_location_id,
            data_center_code=data_center_code,
            identity_url=identity_url,
            resource_version=resource_version,
            physical_location_type=physical_location_type,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            region=region,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            lata=lata,
        )
        payload: str = jinja_env().get_template("complex_create.json.j2").render(
            complex=complex_object)
        url: str = (
            f"{cls.base_url}{cls.api_version}/cloud-infrastructure/complexes/complex/"
            f"{complex_object.physical_location_id}"
        )
        cls.send_message("PUT", "create complex", url, data=payload)
        return complex_object

    @classmethod
    def get_all(cls,
                physical_location_id: str = None,
                data_center_code: str = None,
                complex_name: str = None,
                identity_url: str = None) -> Iterator["Complex"]:
        """Get all complexes from A&AI.

        Call A&AI API to get all complex objects.

        Args:
            physical_location_id (str, optional): Unique identifier for physical location,
                e.g., CLLI. Defaults to None.
            data_center_code (str, optional): Data center code which can be an alternate way
                to identify a complex. Defaults to None.
            complex_name (str, optional): Gamma complex name for LCP instance. Defaults to None.
            identity_url (str, optional): URL of the keystone identity service. Defaults to None.

        Yields:
            Complex -- Complex object. Can not yield anything if any complex with given filter
                parameters doesn't exist

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "physical-location-id": physical_location_id,
                "data-center-code": data_center_code,
                "complex-name": complex_name,
                "identity-url": identity_url,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/cloud-infrastructure/"
                    f"complexes?{urlencode(filter_parameters)}")
        for complex_json in cls.send_message_json("GET",
                                                  "get cloud regions",
                                                  url).get("complex", []):
            yield Complex(
                name=complex_json["complex-name"],
                physical_location_id=complex_json["physical-location-id"],
                data_center_code=complex_json.get("data-center-code"),
                identity_url=complex_json.get("identity-url"),
                resource_version=complex_json.get("resource-version"),
                physical_location_type=complex_json.get("physical-location-type"),
                street1=complex_json.get("street1"),
                street2=complex_json.get("street2"),
                city=complex_json.get("city"),
                state=complex_json.get("state"),
                postal_code=complex_json.get("postal-code"),
                country=complex_json.get("country"),
                region=complex_json.get("region"),
                latitude=complex_json.get("latitude"),
                longitude=complex_json.get("longitude"),
                elevation=complex_json.get("elevation"),
                lata=complex_json.get("lata"),
            )


@dataclass
class AvailabilityZone:
    """Availability zone.

    A collection of compute hosts/pservers
    """

    name: str
    hypervisor_type: str
    operational_status: str = None
    resource_version: str = None


@dataclass
class EsrSystemInfo:  # pylint: disable=R0902
    """Persist common address information of external systems."""

    esr_system_info_id: str
    user_name: str
    password: str
    system_type: str
    resource_version: str
    system_name: str = None
    esr_type: str = None
    vendor: str = None
    version: str = None
    service_url: str = None
    protocol: str = None
    ssl_cacert: str = None
    ssl_insecure: Optional[bool] = None
    ip_address: str = None
    port: str = None
    cloud_domain: str = None
    default_tenant: str = None
    passive: Optional[bool] = None
    remote_path: str = None
    system_status: str = None
    openstack_region_id: str = None


class CloudRegion(AaiElement):  # pylint: disable=R0902
    """Cloud region class.

    Represents A&AI cloud region object.
    """

    def __init__(self,
                 cloud_owner: str,
                 cloud_region_id: str,
                 orchestration_disabled: bool,
                 in_maint: bool,
                 *,  # rest of parameters are keyword
                 cloud_type: str = "",
                 owner_defined_type: str = "",
                 cloud_region_version: str = "",
                 identity_url: str = "",
                 cloud_zone: str = "",
                 complex_name: str = "",
                 sriov_automation: str = "",
                 cloud_extra_info: str = "",
                 upgrade_cycle: str = "",
                 resource_version: str = "") -> None:
        """Cloud region object initialization.

        Args:
            cloud_owner (str): Identifies the vendor and cloud name.
            cloud_region_id (str): Identifier used by the vendor for the region.
            orchestration_disabled (bool): Used to indicate whether orchestration is
                enabled for this cloud-region.
            in_maint (bool): Used to indicate whether or not cloud-region object
                is in maintenance mode.
            owner_defined_type (str, optional): Cloud-owner defined type
                indicator (e.g., dcp, lcp). Defaults to "".
            cloud_region_version (str, optional): Software version employed at the site.
                Defaults to "".
            identity_url (str, optional): URL of the keystone identity service. Defaults to "".
            cloud_zone (str, optional): Zone where the cloud is homed. Defaults to "".
            complex_name (str, optional): Complex name for cloud-region instance. Defaults to "".
            sriov_automation (str, optional): Whether the cloud region supports (true) or does
                not support (false) SR-IOV automation. Defaults to "".
            cloud_extra_info (str, optional): ESR inputs extra information about the VIM or Cloud
                which will be decoded by MultiVIM. Defaults to "".
            upgrade_cycle (str, optional): Upgrade cycle for the cloud region.
                For AIC regions upgrade cycle is designated by A,B,C etc. Defaults to "".
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to "".

        """
        super().__init__()
        self.cloud_owner = cloud_owner
        self.cloud_region_id = cloud_region_id
        self.orchestration_disabled = orchestration_disabled
        self.in_maint = in_maint
        self.cloud_type = cloud_type
        self.owner_defined_type = owner_defined_type
        self.cloud_region_version = cloud_region_version
        self.identity_url = identity_url
        self.cloud_zone = cloud_zone
        self.complex_name = complex_name
        self.sriov_automation = sriov_automation
        self.cloud_extra_info = cloud_extra_info
        self.upgrade_cycle = upgrade_cycle
        self.resource_version = resource_version

    def __repr__(self) -> str:
        """Cloud region object representation.

        Returns:
            str: Human readable string contains most important information about cloud region.

        """
        return (
            f"CloudRegion(cloud_owner={self.cloud_owner}, cloud_region_id={self.cloud_region_id})"
        )

    @classmethod
    def get_all(cls,
                cloud_owner: str = None,
                cloud_region_id: str = None,
                cloud_type: str = None,
                owner_defined_type: str = None) -> Iterator["CloudRegion"]:
        """Get all A&AI cloud regions.

        Cloud regions can be filtered by 4 parameters: cloud-owner,
        cloud-region-id, cloud-type and owner-defined-type.

        Yields:
            CloudRegion -- CloudRegion object. Can not yield anything
                if cloud region with given filter parameters doesn't exist

        """
        # Filter request parameters - use only these which are not None
        filter_parameters: dict = cls.filter_none_key_values(
            {
                "cloud-owner": cloud_owner,
                "cloud-region-id": cloud_region_id,
                "cloud-type": cloud_type,
                "owner-defined-type": owner_defined_type,
            }
        )
        url: str = (f"{cls.base_url}{cls.api_version}/cloud-infrastructure/"
                    f"cloud-regions?{urlencode(filter_parameters)}")
        response_json: Dict[str, List[Dict[str, Any]]] = cls.send_message_json(
            "GET", "get cloud regions", url
        )
        for cloud_region in response_json.get("cloud-region", []):  # typing: dict
            yield CloudRegion(
                cloud_owner=cloud_region["cloud-owner"],  # required
                cloud_region_id=cloud_region["cloud-region-id"],  # required
                cloud_type=cloud_region.get("cloud-type"),
                owner_defined_type=cloud_region.get("owner-defined-type"),
                cloud_region_version=cloud_region.get("cloud-region-version"),
                identity_url=cloud_region.get("identity_url"),
                cloud_zone=cloud_region.get("cloud-zone"),
                complex_name=cloud_region.get("complex-name"),
                sriov_automation=cloud_region.get("sriov-automation"),
                cloud_extra_info=cloud_region.get("cloud-extra-info"),
                upgrade_cycle=cloud_region.get("upgrade-cycle"),
                orchestration_disabled=cloud_region["orchestration-disabled"],  # required
                in_maint=cloud_region["in-maint"],  # required
                resource_version=cloud_region.get("resource-version"),
            )

    @classmethod
    def get_by_id(cls, cloud_owner, cloud_region_id: str) -> "CloudRegion":
        """Get CloudRegion object by cloud_owner and cloud-region-id field value.

        This method calls A&AI cloud region API filtering them by cloud_owner and
        cloud-region-id field value.

        Raises:
            ValueError: Cloud region with given id does not exist.

        Returns:
            CloudRegion: CloudRegion object with given cloud-region-id.

        """
        try:
            return next(cls.get_all(cloud_owner=cloud_owner, cloud_region_id=cloud_region_id))
        except StopIteration:
            raise ValueError(f"CloudRegion with {cloud_owner},{cloud_region_id} cloud-id not found")

    @classmethod
    def create(cls,  # pylint: disable=R0914
               cloud_owner: str,
               cloud_region_id: str,
               orchestration_disabled: bool,
               in_maint: bool,
               *,  # rest of parameters are keyword
               cloud_type: str = "",
               owner_defined_type: str = "",
               cloud_region_version: str = "",
               identity_url: str = "",
               cloud_zone: str = "",
               complex_name: str = "",
               sriov_automation: str = "",
               cloud_extra_info: str = "",
               upgrade_cycle: str = "") -> "CloudRegion":
        """Create CloudRegion object.

        Create cloud region with given values.

        Returns:
            CloudRegion: Created cloud region.

        """
        cloud_region: "CloudRegion" = CloudRegion(
            cloud_owner=cloud_owner,
            cloud_region_id=cloud_region_id,
            orchestration_disabled=orchestration_disabled,
            in_maint=in_maint,
            cloud_type=cloud_type,
            owner_defined_type=owner_defined_type,
            cloud_region_version=cloud_region_version,
            identity_url=identity_url,
            cloud_zone=cloud_zone,
            complex_name=complex_name,
            sriov_automation=sriov_automation,
            cloud_extra_info=cloud_extra_info,
            upgrade_cycle=upgrade_cycle,
        )
        url: str = (
            f"{cls.base_url}{cls.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
            f"{cloud_region.cloud_owner}/{cloud_region.cloud_region_id}"
        )
        cls.send_message(
            "PUT",
            "Create cloud region",
            url,
            data=jinja_env()
            .get_template("cloud_region_create.json.j2")
            .render(cloud_region=cloud_region),
        )
        return cloud_region

    @property
    def url(self) -> str:
        """Cloud region object url.

        URL used to call CloudRegion A&AI API

        Returns:
            str: CloudRegion object url

        """
        return (
            f"{self.base_url}{self.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
            f"{self.cloud_owner}/{self.cloud_region_id}"
        )

    @property
    def tenants(self) -> Iterator["Tenant"]:
        """Tenants iterator.

        Cloud region tenants iterator.

        Returns:
            Iterator[Tenant]: Iterate through cloud region tenants

        """
        response: dict = self.send_message_json("GET", "get tenants", f"{self.url}/tenants")
        return (
            Tenant(
                cloud_region=self,
                tenant_id=tenant["tenant-id"],
                tenant_name=tenant["tenant-name"],
                tenant_context=tenant.get("tenant-context"),
                resource_version=tenant.get("resource-version"),
            )
            for tenant in response.get("tenant", [])
        )

    @property
    def availability_zones(self) -> Iterator[AvailabilityZone]:
        """Cloud region availability zones.

        Iterate over CloudRegion availability zones. Relationship list is given using A&AI API call.

        Returns:
            Iterator[AvailabilityZone]: CloudRegion availability zone

        """
        response: dict = self.send_message_json(
            "GET", "get cloud region availability zones", f"{self.url}/availability-zones"
        )
        return (
            AvailabilityZone(
                name=availability_zone.get("availability-zone-name"),
                hypervisor_type=availability_zone.get("hypervisor-type"),
                operational_status=availability_zone.get("operational-status"),
                resource_version=availability_zone.get("resource-version")
            )
            for availability_zone in response.get("availability-zone", [])
        )

    @property
    def esr_system_infos(self) -> Iterator[EsrSystemInfo]:
        """Cloud region collection of persistent block-level external system auth info.

        Returns:
            Iterator[EsrSystemInfo]: Cloud region external system address information.

        """
        response: dict = self.send_message_json(
            "GET", "get cloud region external systems info list", f"{self.url}/esr-system-info-list"
        )
        return (
            EsrSystemInfo(
                esr_system_info_id=esr_system_info.get("esr-system-info-id"),
                user_name=esr_system_info.get("user-name"),
                password=esr_system_info.get("password"),
                system_type=esr_system_info.get("system-type"),
                system_name=esr_system_info.get("system-name"),
                esr_type=esr_system_info.get("type"),
                vendor=esr_system_info.get("vendor"),
                version=esr_system_info.get("version"),
                service_url=esr_system_info.get("service-url"),
                protocol=esr_system_info.get("protocol"),
                ssl_cacert=esr_system_info.get("ssl-cacert"),
                ssl_insecure=esr_system_info.get("ssl-insecure"),
                ip_address=esr_system_info.get("ip-address"),
                port=esr_system_info.get("port"),
                cloud_domain=esr_system_info.get("cloud-domain"),
                default_tenant=esr_system_info.get("default-tenant"),
                passive=esr_system_info.get("passive"),
                remote_path=esr_system_info.get("remote-path"),
                system_status=esr_system_info.get("system-status"),
                openstack_region_id=esr_system_info.get("openstack-region-id"),
                resource_version=esr_system_info.get("resource-version"),
            )
            for esr_system_info in response.get("esr-system-info", [])
        )

    def add_tenant(self, tenant_id: str, tenant_name: str, tenant_context: str = None) -> None:
        """Add tenant to cloud region.

        Args:
            tenant_id (str): Unique id relative to the cloud-region.
            tenant_name (str): Readable name of tenant
            tenant_context (str, optional): This field will store
                the tenant context.. Defaults to None.

        """
        self.send_message(
            "PUT",
            "add tenant to cloud region",
            f"{self.url}/tenants/tenant/{tenant_id}",
            data=jinja_env()
            .get_template("cloud_region_add_tenant.json.j2")
            .render(tenant_id=tenant_id, tenant_name=tenant_name, tenant_context=tenant_context),
        )

    def get_tenant(self, tenant_id: str) -> "Tenant":
        """Get tenant with provided ID.

        Args:
            tenant_id (str): Tenant ID

        Returns:
            Tenant: Tenant object

        Raises:
            ValueError: Tenant with provided ID doesn't exist

        """
        response: dict = self.send_message_json(
            "GET",
            "get tenants",
            f"{self.url}/tenants/tenant/{tenant_id}",
            exception=ValueError
        )
        return Tenant(
            cloud_region=self,
            tenant_id=response["tenant-id"],
            tenant_name=response["tenant-name"],
            tenant_context=response.get("tenant-context"),
            resource_version=response.get("resource-version"),
        )

    def add_availability_zone(self,
                              availability_zone_name: str,
                              availability_zone_hypervisor_type: str,
                              availability_zone_operational_status: str = None) -> None:
        """Add avaiability zone to cloud region.

        Args:
            availability_zone_name (str): Name of the availability zone.
                Unique across a cloud region
            availability_zone_hypervisor_type (str): Type of hypervisor
            availability_zone_operational_status (str, optional): State that indicates whether
                the availability zone should be used. Defaults to None.
        """
        self.send_message(
            "PUT",
            "Add availability zone to cloud region",
            f"{self.url}/availability-zones/availability-zone/{availability_zone_name}",
            data=jinja_env()
            .get_template("cloud_region_add_availability_zone.json.j2")
            .render(availability_zone_name=availability_zone_name,
                    availability_zone_hypervisor_type=availability_zone_hypervisor_type,
                    availability_zone_operational_status=availability_zone_operational_status)
        )

    def add_esr_system_info(self,  # pylint: disable=R0913, R0914
                            esr_system_info_id: str,
                            user_name: str,
                            password: str,
                            system_type: str,
                            system_name: str = None,
                            esr_type: str = None,
                            vendor: str = None,
                            version: str = None,
                            service_url: str = None,
                            protocol: str = None,
                            ssl_cacert: str = None,
                            ssl_insecure: Optional[bool] = None,
                            ip_address: str = None,
                            port: str = None,
                            cloud_domain: str = None,
                            default_tenant: str = None,
                            passive: Optional[bool] = None,
                            remote_path: str = None,
                            system_status: str = None,
                            openstack_region_id: str = None,
                            resource_version: str = None) -> None:
        """Add external system info to cloud region.

        Args:
            esr_system_info_id (str): Unique ID of esr system info
            user_name (str): username used to access external system
            password (str): password used to access external system
            system_type (str): it could be vim/vnfm/thirdparty-sdnc/
                ems-resource/ems-performance/ems-alarm
            system_name (str, optional): name of external system. Defaults to None.
            esr_type (str, optional): type of external system. Defaults to None.
            vendor (str, optional): vendor of external system. Defaults to None.
            version (str, optional): version of external system. Defaults to None.
            service_url (str, optional): url used to access external system. Defaults to None.
            protocol (str, optional): protocol of third party SDNC,
                for example netconf/snmp. Defaults to None.
            ssl_cacert (str, optional): ca file content if enabled ssl on auth-url.
                Defaults to None.
            ssl_insecure (bool, optional): Whether to verify VIM's certificate. Defaults to True.
            ip_address (str, optional): service IP of ftp server. Defaults to None.
            port (str, optional): service port of ftp server. Defaults to None.
            cloud_domain (str, optional): domain info for authentication. Defaults to None.
            default_tenant (str, optional): default tenant of VIM. Defaults to None.
            passive (bool, optional): ftp passive mode or not. Defaults to False.
            remote_path (str, optional): resource or performance data file path. Defaults to None.
            system_status (str, optional): he status of external system. Defaults to None.
            openstack_region_id (str, optional): OpenStack region ID used by MultiCloud plugin to
                interact with an OpenStack instance. Defaults to None.
        """
        self.send_message(
            "PUT",
            "Add external system info to cloud region",
            f"{self.url}/esr-system-info-list/esr-system-info/{esr_system_info_id}",
            data=jinja_env()
            .get_template("cloud_region_add_esr_system_info.json.j2")
            .render(esr_system_info_id=esr_system_info_id,
                    user_name=user_name,
                    password=password,
                    system_type=system_type,
                    system_name=system_name,
                    esr_type=esr_type,
                    vendor=vendor,
                    version=version,
                    service_url=service_url,
                    protocol=protocol,
                    ssl_cacert=ssl_cacert,
                    ssl_insecure=ssl_insecure,
                    ip_address=ip_address,
                    port=port,
                    cloud_domain=cloud_domain,
                    default_tenant=default_tenant,
                    passive=passive,
                    remote_path=remote_path,
                    system_status=system_status,
                    openstack_region_id=openstack_region_id,
                    resource_version=resource_version)
        )

    def register_to_multicloud(self, default_tenant: str = None) -> None:
        """Register cloud to multicloud using MSB API.

        Args:
            default_tenant (str, optional): Default tenant. Defaults to None.
        """
        Multicloud.register_vim(self.cloud_owner, self.cloud_region_id, default_tenant)

    def unregister_from_multicloud(self) -> None:
        """Unregister cloud from mutlicloud."""
        Multicloud.unregister_vim(self.cloud_owner, self.cloud_region_id)

    def delete(self) -> None:
        """Delete cloud region."""
        self.send_message(
            "DELETE",
            f"Delete cloud region {self.cloud_region_id}",
            self.url,
            params={"resource-version": self.resource_version}
        )

    def link_to_complex(self, complex_object: Complex) -> None:
        """Link cloud region to comples.

        It creates relationhip object and add it into cloud region.
        """
        relationship = Relationship(
            related_to="complex",
            related_link=(f"aai/v13/cloud-infrastructure/complexes/"
                          f"complex/{complex_object.physical_location_id}"),
            relationship_data={
                "relationship-key": "complex.physical-location-id",
                "relationship-value": f"{complex_object.physical_location_id}",
            },
            relationship_label="org.onap.relationships.inventory.LocatedIn",
        )
        self.add_relationship(relationship)


class Tenant(AaiElement):
    """Tenant class."""

    def __init__(self,  # pylint: disable=R0913
                 cloud_region: "CloudRegion",
                 tenant_id: str,
                 tenant_name: str,
                 tenant_context: str = None,
                 resource_version: str = None):
        """Tenant object initialization.

        Tenant object represents A&AI Tenant resource.

        Args:
            cloud_region (str): Cloud region object
            tenant_id (str): Unique Tenant ID
            tenant_name (str): Tenant name
            tenant_context (str, optional): Tenant context. Defaults to None.
            resource_version (str, optional): Tenant resource version. Defaults to None.

        """
        super().__init__()
        self.cloud_region: "CloudRegion" = cloud_region
        self.tenant_id: str = tenant_id
        self.name: str = tenant_name
        self.context: str = tenant_context
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Tenant repr.

        Returns:
            str: Human readable Tenant object description

        """
        return (
            f"Tenant(tenant_id={self.tenant_id}, tenant_name={self.name}, "
            f"tenant_context={self.context}, "
            f"resource_version={self.resource_version}, "
            f"cloud_region={self.cloud_region.cloud_region_id})"
        )

    @property
    def url(self) -> str:
        """Tenant url.

        Returns:
            str: Url which can be used to update or delete tenant.

        """
        return (
            f"{self.base_url}{self.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
            f"{self.cloud_region.cloud_owner}/{self.cloud_region.cloud_region_id}"
            f"/tenants/tenant/{self.tenant_id}?"
            f"resource-version={self.resource_version}"
        )

    def delete(self) -> None:
        """Delete tenant.

        Remove tenant from cloud region.

        """
        return self.send_message(
            "DELETE",
            f"Remove tenant {self.name} from {self.cloud_region.cloud_region_id} cloud region",
            url=self.url,
        )
