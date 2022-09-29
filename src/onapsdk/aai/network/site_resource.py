"""A&AI site resource module."""

from typing import Iterable, Optional
from onapsdk.aai.network.cell import Cell

from onapsdk.utils.jinja import jinja_env
from ..aai_element import AaiResource, Relationship
from ..cloud_infrastructure import Complex


class SiteResource(AaiResource):  # pylint: disable=too-many-instance-attributes
    """Site resource class."""

    def __init__(self,  # pylint: disable=too-many-locals
                 site_resource_id: str,
                 *,
                 site_resource_name: str = "",
                 description: str = "",
                 site_resource_type: str = "",
                 role: str = "",
                 generated_site_id: str = "",
                 selflink: str = "",
                 operational_status: str = "",
                 model_customization_id: str = "",
                 model_invariant_id: str = "",
                 model_version_id: str = "",
                 data_owner: str = "",
                 data_source: str = "",
                 data_source_version: str = "",
                 resource_version: str = "") -> None:
        """Site resource object init.

        Args:
            site_resource_id (str): Uniquely identifies this site-resource by id.
            site_resource_name (str, optional): Store the name of this site-resource.
                Defaults to "".
            description (str, optional): Store the description of this site-resource.
                Defaults to "".
            site_resource_type (str, optional): Store the type of this site-resource.
                Defaults to "".
            role (str, optional): Store the role of this site-resource. Defaults to "".
            generated_site_id (str, optional): Store the generated-site-id of this site-resource.
                Defaults to "".
            selflink (str, optional): Store the link to get more information for this object.
                Defaults to "".
            operational_status (str, optional): Store the operational-status for this object.
                Defaults to "".
            model_customization_id (str, optional): Store the model-customization-id
                for this object. Defaults to "".
            model_invariant_id (str, optional): The ASDC model id for this resource or
                service model. Defaults to "".
            model_version_id (str, optional): The ASDC model version for this resource or service
                model. Defaults to "".
            data_owner (str, optional): Identifies the entity that is responsible managing
                this inventory object. Defaults to "".
            data_source (str, optional): Identifies the upstream source of the data.
                Defaults to "".
            data_source_version (str, optional): Identifies the version of the upstream source.
                Defaults to "".
            resource_version (str, optional): Used for optimistic concurrency. Must be empty on
                create, valid on update and delete. Defaults to "".

        """
        super().__init__()
        self.site_resource_id: str = site_resource_id
        self.site_resource_name: str = site_resource_name
        self.description: str = description
        self.site_resource_type: str = site_resource_type
        self.role: str = role
        self.generated_site_id: str = generated_site_id
        self.selflink: str = selflink
        self.operational_status: str = operational_status
        self.model_customization_id: str = model_customization_id
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id
        self.data_owner: str = data_owner
        self.data_source: str = data_source
        self.data_source_version: str = data_source_version
        self.resource_version: str = resource_version

    @property
    def url(self) -> str:
        """Site resource's url.

        Returns:
            str: Site resources's url

        """
        return (f"{self.base_url}{self.api_version}/network/site-resources"
                f"/site-resource/{self.site_resource_id}")

    @classmethod
    def get_all_url(cls, *args, **kwargs) -> str:
        """Get all site resources request url.

        Returns:
            str: Url used on get all site resources request

        """
        return f"{cls.base_url}{cls.api_version}/network/site-resources"

    @classmethod
    def get_all(cls) -> Iterable["SiteResource"]:
        """Get all site resources.

        Yields:
            SiteResource: Site resource object

        """
        for site_resource_data in cls.send_message_json("GET",
                                                        "Get all site resources",
                                                        cls.get_all_url()).get("site-resource", []):
            yield SiteResource(site_resource_id=site_resource_data["site-resource-id"],
                               site_resource_name=site_resource_data.get("site-resource-name", ""),
                               description=site_resource_data.get("description", ""),
                               site_resource_type=site_resource_data.get("type", ""),
                               role=site_resource_data.get("role", ""),
                               generated_site_id=site_resource_data.get("generated-site-id", ""),
                               selflink=site_resource_data.get("selflink", ""),
                               operational_status=site_resource_data.get("operational-status", ""),
                               model_customization_id=site_resource_data.\
                                   get("model-customization-id", ""),
                               model_invariant_id=site_resource_data.get("model-invariant-id", ""),
                               model_version_id=site_resource_data.get("model-version-id", ""),
                               data_owner=site_resource_data.get("data-owner", ""),
                               data_source=site_resource_data.get("data-source", ""),
                               data_source_version=site_resource_data.get("data-source-version",
                                                                          ""),
                               resource_version=site_resource_data.get("resource-version", ""))

    @classmethod
    def get_by_site_resource_id(cls, site_resource_id: str) -> "SiteResource":
        """Get site resource by it's id.

        Args:
            site_resource_id (str): Site resource id.

        Returns:
            SiteResource: Site resource object.

        """
        site_resource_data = cls.send_message_json("GET",
                                                   f"Get site resource with {site_resource_id} id",
                                                   f"{cls.get_all_url()}"
                                                   f"/site-resource/{site_resource_id}")
        return SiteResource(site_resource_id=site_resource_data["site-resource-id"],
                            site_resource_name=site_resource_data.get("site-resource-name", ""),
                            description=site_resource_data.get("description", ""),
                            site_resource_type=site_resource_data.get("type", ""),
                            role=site_resource_data.get("role", ""),
                            generated_site_id=site_resource_data.get("generated-site-id", ""),
                            selflink=site_resource_data.get("selflink", ""),
                            operational_status=site_resource_data.get("operational-status", ""),
                            model_customization_id=site_resource_data.get("model-customization-id",
                                                                          ""),
                            model_invariant_id=site_resource_data.get("model-invariant-id", ""),
                            model_version_id=site_resource_data.get("model-version-id", ""),
                            data_owner=site_resource_data.get("data-owner", ""),
                            data_source=site_resource_data.get("data-source", ""),
                            data_source_version=site_resource_data.get("data-source-version", ""),
                            resource_version=site_resource_data.get("resource-version", ""))

    @classmethod
    def create(cls,  # pylint: disable=too-many-arguments
               site_resource_id: str,
               site_resource_name: Optional[str] = None,
               description: Optional[str] = None,
               site_resource_type: Optional[str] = None,
               role: Optional[str] = None,
               generated_site_id: Optional[str] = None,
               selflink: Optional[str] = None,
               operational_status: Optional[str] = None,
               model_customization_id: Optional[str] = None,
               model_invariant_id: Optional[str] = None,
               model_version_id: Optional[str] = None,
               data_owner: Optional[str] = None,
               data_source: Optional[str] = None,
               data_source_version: Optional[str] = None) -> "SiteResource":
        """Create site resource.

        Args:
            site_resource_id (str): Uniquely identifies this site-resource by id
            site_resource_name (Optional[str], optional): Store the name of this site-resource.
                Defaults to None.
            description (Optional[str], optional): Store the description of this site-resource.
                Defaults to None.
            site_resource_type (Optional[str], optional): Store the type of this site-resource.
                Defaults to None.
            role (Optional[str], optional): Store the role of this site-resource.
                Defaults to None.
            generated_site_id (Optional[str], optional): Store the generated-site-id of
                this site-resource. Defaults to None.
            selflink (Optional[str], optional): Store the link to get more information
                for this object. Defaults to None.
            operational_status (Optional[str], optional): Store the operational-status
                for this object. Defaults to None.
            model_customization_id (Optional[str], optional): Store the model-customization-id
                for this object. Defaults to None.
            model_invariant_id (Optional[str], optional): The ASDC model id for
                this resource or service model. Defaults to None.
            model_version_id (Optional[str], optional): The ASDC model version for this
                resource or service model. Defaults to None.
            data_owner (Optional[str], optional): Identifies the entity that is responsible
                managing this inventory object. Defaults to None.
            data_source (Optional[str], optional): Identifies the upstream source of the data.
                Defaults to None.
            data_source_version (Optional[str], optional): Identifies the version of the upstream
                source. Defaults to None.

        Returns:
            SiteResource: Site resource object

        """
        cls.send_message("PUT",
                         f"Create site resource {site_resource_id}",
                         f"{cls.get_all_url()}/site-resource/{site_resource_id}",
                         data=jinja_env()
                         .get_template("site_resource_create.json.j2")
                         .render(site_resource_id=site_resource_id,
                                 site_resource_name=site_resource_name,
                                 description=description,
                                 site_resource_type=site_resource_type,
                                 role=role,
                                 generated_site_id=generated_site_id,
                                 selflink=selflink,
                                 operational_status=operational_status,
                                 model_customization_id=model_customization_id,
                                 model_invariant_id=model_invariant_id,
                                 model_version_id=model_version_id,
                                 data_owner=data_owner,
                                 data_source=data_source,
                                 data_source_version=data_source_version))
        return cls.get_by_site_resource_id(site_resource_id)

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
            relationship_label="org.onap.relationships.inventory.Uses",
        )
        self.add_relationship(relationship)

    def link_to_cell(self, cell: Cell) -> None:
        relationship: Relationship = Relationship(
            related_to="cell",
            related_link=cell.url,
            relationship_data=[
                {
                    "relationship-key": "cell.cell-id",
                    "relationship-value": cell.cell_id,
                }
            ],
            relationship_label="org.onap.relationships.inventory.ControlledBy",
        )
        self.add_relationship(relationship)
