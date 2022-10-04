
from ..aai_element import Relationship
from ..cloud_infrastructure.geo_region import GeoRegion

class AaiResourceLinkToGeoRegionMixin:  # pylint: disable=too-few-public-methods
    """Link aai resource to geo region mixin."""

    def link_to_geo_region(self, geo_region: GeoRegion) -> None:
        """Create a relationship with geo region.

        As few resources create same relationship with geo region

        Args:
            geo_region (GeoRegion): Geo region object
        """
        relationship: Relationship = Relationship(
            related_to="geo-region",
            related_link=geo_region.url,
            relationship_data=[
                {
                    "relationship-key": "geo-region.geo-region-id",
                    "relationship-value": geo_region.geo_region_id,
                }
            ],
            relationship_label="org.onap.relationships.inventory.MemberOf",
        )
        self.add_relationship(relationship)