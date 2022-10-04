"""Cell module."""

from typing import Any, Dict, Iterable, Optional

from onapsdk.utils.jinja import jinja_env
from ..aai_element import AaiResource
from ..mixins.link_to_complex import AaiResourceLinkToComplexMixin
from ..mixins.link_to_geo_region import AaiResourceLinkToGeoRegionMixin


class Cell(AaiResource, AaiResourceLinkToComplexMixin, AaiResourceLinkToGeoRegionMixin):  # pylint: disable=too-many-instance-attributes
    """Cell resource class.

    Inherits from aai.mixinx.AaiResourceLinkToGeoRegionMixin so
        relationship to GeoRegion object is available for that resource.
    """

    def __init__(self,  # pylint: disable=too-many-locals
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
                 resource_version: str = "") -> None:
        """Cell object init.

        Args:
            cell_id (str): unique identifier of the cell (i.e. could be globally unique
                like NCGI or unique within operator domain like NCI)
            cell_name (str): individual name of cell
            radio_access_technology (str): cell radio access technology (i.e. GSM, UMTS, LTE, NR)
            cell_local_id (str, optional): unique identifier of the cell within node
                (like eNodeb, gNodeb). Defaults to "".
            mno_id (str, optional): operator specific cell identifier. Defaults to "".
            node_id (str, optional): cell's node id (like gNodeb id, eNodeb id).
                Defaults to "".
            latitude (Optional[float], optional): latitude of cell. Defaults to None.
            longitude (Optional[float], optional): longitude of cell. Defaults to None.
            azimuth (Optional[float], optional): direction of cell beam  (range: 0-360).
                Defaults to None.
            height (Optional[float], optional): cell height above ground. Defaults to None.
            mechanical_tilt (Optional[float], optional): mechanical tilt of cell. Defaults to None.
            electrical_tilt (Optional[float], optional): electrical tilt of cell. Defaults to None.
            beamwidth (Optional[float], optional): horizontal beamwidth of cell. Defaults to None.
            cell_type (str): type of cell (i.e. macro, micro, indoor, outdoor,
                string). Defaults to "".
            coverage_area (str): type of coverage area (i.e. urban, suburban,
                rural, string). Defaults to "".
            frequency_band (str): cell operating frequency band. Defaults to "".
            mnc (str): operator mobile network code. Defaults to "".
            mcc (str): operator country code. Defaults to "".
            selflink (str): CPS link to additional cell info
                (it may be a collection of links e.g. operator-specific cell attributes,
                3gpp-config, vendor-config, NRCellDU, NRCellCU in CPS). Defaults to "".
            resource_version (str, optional): Cell object resource version. Defaults to "".

        """
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
        self.resource_version: str = resource_version

    @property
    def url(self) -> str:
        """Cell object url.

        Returns:
            str: Cell object url string

        """
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
        """Get all cell resources.

        Yields:
            Cell: Cell resource object

        """
        for cell_data in cls.send_message_json("GET",
                                               "Get all cells",
                                               cls.get_all_url()).get("cell", []):
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
                       resource_version=cell_data["resource-version"])

    @classmethod
    def get_by_cell_id(cls, cell_id: str) -> "Cell":
        """Get cell object by id.

        Args:
            cell_id (str): Cell id.

        Returns:
            Cell: Cell resource object

        """
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
                    resource_version=cell_data["resource-version"])

    @classmethod
    def create(cls,  # pylint: disable=too-many-arguments, too-many-locals
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
        """Create cell resource.

        Args:
            cell_id (str): unique identifier of the cell (i.e. could be globally unique
                like NCGI or unique within operator domain like NCI)
            cell_name (str): individual name of cell
            radio_access_technology (str): cell radio access technology (i.e. GSM, UMTS, LTE, NR)
            cell_local_id (Optional[str], optional): unique identifier of the cell within node
                (like eNodeb, gNodeb). Defaults to None.
            mno_id (Optional[str], optional): operator specific cell identifier. Defaults to None.
            node_id (Optional[str], optional): cell's node id (like gNodeb id, eNodeb id).
                Defaults to None.
            latitude (Optional[float], optional): latitude of cell. Defaults to None.
            longitude (Optional[float], optional): longitude of cell. Defaults to None.
            azimuth (Optional[float], optional): direction of cell beam  (range: 0-360).
                Defaults to None.
            height (Optional[float], optional): cell height above ground. Defaults to None.
            mechanical_tilt (Optional[float], optional): mechanical tilt of cell. Defaults to None.
            electrical_tilt (Optional[float], optional): electrical tilt of cell. Defaults to None.
            beamwidth (Optional[float], optional): horizontal beamwidth of cell. Defaults to None.
            cell_type (Optional[str], optional): type of cell (i.e. macro, micro, indoor, outdoor,
                string). Defaults to None.
            coverage_area (Optional[str], optional): type of coverage area (i.e. urban, suburban,
                rural, string). Defaults to None.
            frequency_band (Optional[str], optional): cell operating frequency band.
                Defaults to None.
            mnc (Optional[str], optional): operator mobile network code. Defaults to None.
            mcc (Optional[str], optional): operator country code. Defaults to None.
            selflink (Optional[str], optional): CPS link to additional cell info
                (it may be a collection of links e.g. operator-specific cell attributes,
                3gpp-config, vendor-config, NRCellDU, NRCellCU in CPS). Defaults to None.

        Returns:
            Cell: Created cell object

        """
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

    def delete(self) -> None:
        """Delete cell."""
        self.send_message("DELETE",
                          f"Delete cell {self.cell_id}",
                          f"{self.url}?resource-version={self.resource_version}")
