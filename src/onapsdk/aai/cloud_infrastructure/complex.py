"""A&AI Complex module."""
from typing import Iterator
from urllib.parse import urlencode

from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiElement


class Complex(AaiElement):  # pylint: disable=too-many-instance-attributes
    """Complex class.

    Collection of physical locations that can house cloud-regions.
    """

    def __init__(self,  # pylint: disable=too-many-locals
                 physical_location_id: str,
                 *,
                 name: str = "",
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
        return (f"Complex(name={self.name}, "
                f"physical_location_id={self.physical_location_id}, "
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
    def create(cls,  # pylint: disable=too-many-locals
               physical_location_id: str,
               *,
               name: str = "",
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
                name=complex_json.get("complex-name"),
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
