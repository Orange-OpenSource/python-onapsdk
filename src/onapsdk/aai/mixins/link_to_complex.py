"""A&AI link to complex module."""
from ..aai_element import Relationship, RelationshipLabelEnum
from ..cloud_infrastructure.complex import Complex


class AaiResourceLinkToComplexMixin:  # pylint: disable=too-few-public-methods
    """Link aai resource to complex mixin."""

    def link_to_complex(self, cmplx: Complex,
                        relationship_label: RelationshipLabelEnum =\
                            RelationshipLabelEnum.LOCATED_IN) -> None:
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
            relationship_label=relationship_label.value,
        )
        self.add_relationship(relationship)
