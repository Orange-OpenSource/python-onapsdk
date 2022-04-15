"""A&AI Tenant module."""
# from onapsdk.aai.cloud_infrastructure.cloud_region import CloudRegion
from ..aai_element import AaiResource


class Tenant(AaiResource):
    """Tenant class."""

    def __init__(self,  # pylint: disable=too-many-arguments
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

    @classmethod
    def get_all_url(cls, cloud_region: "CloudRegion") -> str:  # pylint: disable=arguments-differ
        """Return an url to get all tenants for given cloud region.

        Args:
            cloud_region (CloudRegion): Cloud region object

        Returns:
            str: Url to get all tenants

        """
        return (f"{cls.base_url}{cls.api_version}/cloud-infrastructure/cloud-regions/cloud-region/"
                f"{cloud_region.cloud_owner}/{cloud_region.cloud_region_id}"
                f"/tenants/")

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
