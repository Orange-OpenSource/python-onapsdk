"""Base instance module."""

from abc import ABC, abstractmethod

from ..aai_element import AaiElement


class Instance(AaiElement, ABC):
    """Abstract instance class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 resource_version: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None) -> None:
        """Instance initialization.

        Args:
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to None.
            model_invariant_id (str, optional): The ASDC model id for this resource or
                service model. Defaults to None.
            model_version_id (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
        """
        super().__init__()
        self.resource_version: str = resource_version
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id

    @abstractmethod
    def delete(self) -> "DeletionRequest":
        """Create instance deletion request.

        Send request to delete instance

        Returns:
            DeletionRequest: Deletion request

        """
