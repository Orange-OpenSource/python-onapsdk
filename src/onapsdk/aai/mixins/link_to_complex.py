
from ..aai_element import Relationship
from ..cloud_infrastructure.complex import Complex


class AaiResourceLinkToComplexMixin:  # pylint: disable=too-few-public-methods
    """Link aai resource to complex mixin."""

    def link_to_complex(self, cmplx: Complex) -> None:
        """Create a relationship with complex resource.

        Args:
            cmplx (Complex): Complex object ot create relationship with.

        """
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