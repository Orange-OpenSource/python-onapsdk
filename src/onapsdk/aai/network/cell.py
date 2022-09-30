"""Cell module."""

from typing import Any, Dict, Iterable, Optional

from onapsdk.utils.jinja import jinja_env
from ..aai_element import AaiResource, Relationship
# from ..aai_element import AaiResource
# from ..cloud_infrastructure import GeoRegion
from ..cloud_infrastructure import Complex
from ..mixins import AaiResourceLinkToGeoRegionMixin


class Cell(AaiResource, AaiResourceLinkToGeoRegionMixin):

    def __init__(self,
                 cell_id: str,
                 cell_name: str,
                 radio_access_technology: str,
                 *,
                 cell_local_id: str = "",
                 mno_id: str = "",
                 node_id: str = "",
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 azimuth: Optional[float] = None,
                 height: Optional[float] = None,
                 mechanical_tilt: Optional[float] = None,
                 electrical_tilt: Optional[float] = None,
                 beamwidth: Optional[float] = None,
                 cell_type: str = "",
                 coverage_area: str = "",
                 frequency_band: str = "",
                 mnc: str = "",
                 mcc: str = "",
                 selflink: str = "",
                 resource_verion: str = "") -> None:
        super().__init__()
        self.cell_id: str = cell_id
        self.cell_name: str = cell_name
        self.radio_access_technology: str = radio_access_technology
        self.cell_local_id: str = cell_local_id
        self.mno_id: str = mno_id
        self.node_id: str = node_id
        self.latitude: Optional[float] = latitude
        self.longitude: Optional[float] = longitude
        self.azimuth: Optional[float] = azimuth
        self.height: Optional[float] = height
        self.mechanical_tilt: Optional[float] = mechanical_tilt
        self.electrical_tilt: Optional[float] = electrical_tilt
        self.beamwidth: Optional[float] = beamwidth
        self.cell_type: str = cell_type
        self.coverage_area: str = coverage_area
        self.frequency_band: str = frequency_band
        self.mnc: str = mnc
        self.mcc: str = mcc
        self.selflink: str = selflink
        self.resource_verion: str = resource_verion

    @property
    def url(self) -> str:
        return f"{self.get_all_url()}/cell/{self.cell_id}"

    @classmethod
    def get_all_url(cls, *args, **kwargs) -> str:
        """Get all cells request url.

        Returns:
            str: Url used on get all cells request

        """
        return f"{cls.base_url}{cls.api_version}/network/cells"

    @classmethod
    def get_all(cls) -> Iterable["Cell"]:
        for cell_data in cls.send_message_json("GET",
                                               "Get all cells",
                                               cls.get_all_url()).get("cells", []):
            yield Cell(cell_id=cell_data["cell-id"],
                       cell_name=cell_data["cell-name"],
                       radio_access_technology=cell_data["radio-access-technology"],
                       cell_local_id=cell_data.get("cell-local-id", ""),
                       mno_id=cell_data.get("mano-id"),
                       node_id=cell_data.get("node-id"),
                       latitude=cell_data.get("latitude"),
                       longitude=cell_data.get("longitude"),
                       azimuth=cell_data.get("azimuth"),
                       height=cell_data.get("height"),
                       mechanical_tilt=cell_data.get("mechanical-tilt"),
                       electrical_tilt=cell_data.get("electrical-tilt"),
                       beamwidth=cell_data.get("beamwidth"),
                       cell_type=cell_data.get("cell-type", ""),
                       coverage_area=cell_data.get("coverage-area", ""),
                       frequency_band=cell_data.get("frequency-band", ""),
                       mnc=cell_data.get("mnc", ""),
                       mcc=cell_data.get("mcc", ""),
                       selflink=cell_data.get("selflink", ""),
                       resource_verion=cell_data["resource_version"])

    @classmethod
    def get_by_cell_id(cls, cell_id: str) -> "Cell":
        cell_data: Dict[str, Any] = cls.send_message_json("GET",
                                                          f"Get cell with {cell_id} cell id",
                                                          f"{cls.get_all_url()}/cell/{cell_id}")
        return Cell(cell_id=cell_data["cell-id"],
                    cell_name=cell_data["cell-name"],
                    radio_access_technology=cell_data["radio-access-technology"],
                    cell_local_id=cell_data.get("cell-local-id", ""),
                    mno_id=cell_data.get("mano-id"),
                    node_id=cell_data.get("node-id"),
                    latitude=cell_data.get("latitude"),
                    longitude=cell_data.get("longitude"),
                    azimuth=cell_data.get("azimuth"),
                    height=cell_data.get("height"),
                    mechanical_tilt=cell_data.get("mechanical-tilt"),
                    electrical_tilt=cell_data.get("electrical-tilt"),
                    beamwidth=cell_data.get("beamwidth"),
                    cell_type=cell_data.get("cell-type", ""),
                    coverage_area=cell_data.get("coverage-area", ""),
                    frequency_band=cell_data.get("frequency-band", ""),
                    mnc=cell_data.get("mnc", ""),
                    mcc=cell_data.get("mcc", ""),
                    selflink=cell_data.get("selflink", ""),
                    resource_verion=cell_data["resource-version"])

    @classmethod
    def create(cls,
               cell_id: str,
               cell_name: str,
               radio_access_technology: str,
               cell_local_id: Optional[str] = None,
               mno_id: Optional[str] = None,
               node_id: Optional[str] = None,
               latitude: Optional[float] = None,
               longitude: Optional[float] = None,
               azimuth: Optional[float] = None,
               height: Optional[float] = None,
               mechanical_tilt: Optional[float] = None,
               electrical_tilt: Optional[float] = None,
               beamwidth: Optional[float] = None,
               cell_type: Optional[str] = None,
               coverage_area: Optional[str] = None,
               frequency_band: Optional[str] = None,
               mnc: Optional[str] = None,
               mcc: Optional[str] = None,
               selflink: Optional[str] = None) -> "Cell":
        cls.send_message("PUT",
                         f"Create cell {cell_id}",
                         f"{cls.get_all_url()}/cell/{cell_id}",
                         data=jinja_env()
                         .get_template("cell_create.json.j2")
                         .render(cell_id=cell_id,
                                 cell_local_id=cell_local_id,
                                 mno_id=mno_id,
                                 node_id=node_id,
                                 cell_name=cell_name,
                                 radio_access_technology=radio_access_technology,
                                 latitude=latitude,
                                 longitude=longitude,
                                 azimuth=azimuth,
                                 height=height,
                                 mechanical_tilt=mechanical_tilt,
                                 electrical_tilt=electrical_tilt,
                                 beamwidth=beamwidth,
                                 cell_type=cell_type,
                                 coverage_area=coverage_area,
                                 frequency_band=frequency_band,
                                 mnc=mnc,
                                 mcc=mcc,
                                 selflink=selflink))
        return cls.get_by_cell_id(cell_id)

    def link_to_complex(self, cmplx: Complex) -> None:
        relationship: Relationship = Relationship(
            related_to="complex",
            related_link=cmplx.url,
            relationship_data=[
                {
                    "relationship-key": "complex.physical-location-id",
                    "relationship-value": cmplx.physical_location_id,
                }
            ],
            relationship_label="org.onap.relationships.inventory.LocatedIn",
        )
        self.add_relationship(relationship)

    def delete(self) -> None:
        self.send_message("DELETE",
                          f"Delete cell {self.cell_id}",
                          f"{self.url}?resource-version={self.resource_verion}")

    # def link_to_geo_region(self, geo_region: GeoRegion) -> None:
    #     relationship: Relationship = Relationship(
    #         related_to="geo-region",
    #         related_link=geo_region.url,
    #         relationship_data=[
    #             {
    #                 "relationship-key": "geo-region.geo-region-id",
    #                 "relationship-value": geo_region.geo_region_id,
    #             }
    #         ],
    #         relationship_label="org.onap.relationships.inventory.MemberOf",
    #     )
    #     self.add_relationship(relationship)
