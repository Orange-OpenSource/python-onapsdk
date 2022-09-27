"""Geo region module."""

from typing import Iterator, Optional

from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiResource


class GeoRegion(AaiResource):  # pylint: disable=too-many-instance-attributes
    """Geo region class."""

    def __init__(self,
                 geo_region_id: str,
                 *,
                 geo_region_name: str = "",
                 geo_region_type: str = "",
                 geo_region_role: str = "",
                 geo_region_function: str = "",
                 data_owner: str = "",
                 data_source: str = "",
                 data_source_version: str = "",
                 resource_version: str = "",
                 ) -> None:
        """Geo region init.

        Args:
            geo_region_id (str): UUID, key for geo-region object.
            geo_region_name (str, optional): Name of geo-region. Defaults to "".
            geo_region_type (str, optional): Type of geo-region. Defaults to "".
            geo_region_role (str, optional): Role of geo-region. Defaults to "".
            geo_region_function (str, optional): Function of geo-region. Defaults to "".
            data_owner (str, optional): Identifies the entity that is responsible managing
                this inventory object. Defaults to "".
            data_source (str, optional): Identifies the upstream source of the data.
                Defaults to "".
            data_source_version (str, optional): Identifies the version of
                the upstream source. Defaults to "".
            resource_version (str, optional): Resource version. Defaults to "".

        """
        super().__init__()
        self.geo_region_id: str = geo_region_id
        self.geo_region_name: str = geo_region_name
        self.geo_region_type: str = geo_region_type
        self.geo_region_role: str = geo_region_role
        self.geo_region_function: str = geo_region_function
        self.data_owner: str = data_owner
        self.data_source: str = data_source
        self.data_source_version: str = data_source_version
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Geo region object representation.

        Returns:
            str: Human readable string contains most important information about geo region.

        """
        return (
            f"GeoRegion(geo_region_id={self.geo_region_id})"
        )

    @property
    def url(self) -> str:
        """Geo region's url.

        Returns:
            str: Geo Region's url

        """
        return (f"{self.base_url}{self.api_version}/cloud-infrastructure/"
                f"geo-regions/geo-region/{self.geo_region_id}")

    @classmethod
    def get_all_url(cls, *args, **kwargs) -> str:  # pylint: disable=arguments-differ
        """Return url to get all geo regions.

        Returns:
            str: Url to get all geo regions

        Raises:
            ResourceNotFound: No geo regions found

        """
        return f"{cls.base_url}{cls.api_version}/cloud-infrastructure/geo-regions"

    @classmethod
    def get_all(cls) -> Iterator["GeoRegion"]:
        """Get all geo regions.

        Yields:
            GeoRegion: Geo region

        """
        for geo_region_data in cls.send_message_json("GET",
                                                     "Get all geo regions",
                                                     cls.get_all_url()).get("geo-region", []):
            yield cls(geo_region_id=geo_region_data["geo-region-id"],
                      geo_region_name=geo_region_data.get("geo-region-name", ""),
                      geo_region_type=geo_region_data.get("geo-region-type", ""),
                      geo_region_role=geo_region_data.get("geo-region-role", ""),
                      geo_region_function=geo_region_data.get("geo-region-function", ""),
                      data_owner=geo_region_data.get("data-owner", ""),
                      data_source=geo_region_data.get("data-source", ""),
                      data_source_version=geo_region_data.get("data-source-version", ""),
                      resource_version=geo_region_data.get("resource-version", ""))

    @classmethod
    def get_by_geo_region_id(cls, geo_region_id: str) -> "GeoRegion":
        """Get geo region by it's id.

        Args:
            geo_region_id (str): Geo region id

        Returns:
            GeoRegion: Geo region

        """
        resp = cls.send_message_json("GET",
                                     f"Get geo region with {geo_region_id} id",
                                     f"{cls.get_all_url()}/geo-region/{geo_region_id}")
        return GeoRegion(resp["geo-region-id"],
                         geo_region_name=resp.get("geo-region-name", ""),
                         geo_region_type=resp.get("geo-region-type", ""),
                         geo_region_role=resp.get("geo-region-role", ""),
                         geo_region_function=resp.get("geo-region-function", ""),
                         data_owner=resp.get("data-owner", ""),
                         data_source=resp.get("data-source", ""),
                         data_source_version=resp.get("data-source-version", ""),
                         resource_version=resp["resource-version"])

    @classmethod
    def create(cls,  # pylint: disable=too-many-arguments
               geo_region_id: str,
               geo_region_name: Optional[str] = None,
               geo_region_type: Optional[str] = None,
               geo_region_role: Optional[str] = None,
               geo_region_function: Optional[str] = None,
               data_owner: Optional[str] = None,
               data_source: Optional[str] = None,
               data_source_version: Optional[str] = None) -> "GeoRegion":
        """Create geo region.

        Args:
            geo_region_id (str): UUID, key for geo-region object.
            geo_region_name (Optional[str], optional): Name of geo-region. Defaults to None.
            geo_region_type (Optional[str], optional): Type of geo-region. Defaults to None.
            geo_region_role (Optional[str], optional): Role of geo-region. Defaults to None.
            geo_region_function (Optional[str], optional): Function of geo-region.
                Defaults to None.
            data_owner (Optional[str], optional): Identifies the entity that is
                responsible managing this inventory object.. Defaults to None.
            data_source (Optional[str], optional): Identifies the upstream source of the data.
                Defaults to None.
            data_source_version (Optional[str], optional): Identifies the version of
                the upstream source. Defaults to None.

        Returns:
            GeoRegion: Geo region object

        """
        cls.send_message(
            "PUT",
            "Create geo region",
            f"{cls.get_all_url()}/geo-region/{geo_region_id}",
            data=jinja_env()
            .get_template("geo_region_create.json.j2")
            .render(geo_region_id=geo_region_id,
                    geo_region_name=geo_region_name,
                    geo_region_type=geo_region_type,
                    geo_region_role=geo_region_role,
                    geo_region_function=geo_region_function,
                    data_owner=data_owner,
                    data_source=data_source,
                    data_source_version=data_source_version),
        )
        return cls.get_by_geo_region_id(geo_region_id)
