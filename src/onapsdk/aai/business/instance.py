"""Base instance module."""

from abc import ABC, abstractmethod

from ..aai_element import AaiElement


class Instance(AaiElement, ABC):
    """Abstract instance class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 resource_version: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 persona_model_version: str = None,
                 widget_model_id: str = None,
                 widget_model_version: str = None) -> None:
        """Instance initialization.

        Args:
            model_invariant_id (str, optional): The ASDC model id for this resource or
                service model. Defaults to None.
            model_version_id (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
            persona_model_version (str, optional): The ASDC model version for this resource or
                service model. Defaults to None.
            widget_model_id (str, optional): he ASDC data dictionary widget model. This maps
                directly to the A&AI widget. Defaults to None.
            widget_model_version (str, optional): The ASDC data dictionary version of the widget
                model. This maps directly to the A&AI version of the widget. Defaults to None.
        """
        super().__init__()
        self.resource_version: str = resource_version
        self.model_invariant_id: str = model_invariant_id
        self.model_version_id: str = model_version_id
        self.persona_model_version: str = persona_model_version
        self.widget_model_id: str = widget_model_id
        self.widget_model_version: str = widget_model_version

    @abstractmethod
    def delete(self) -> "DeletionRequest":
        """Create instance deletion request.

        Send request to delete instance

        Returns:
            DeletionRequest: Deletion request

        """
