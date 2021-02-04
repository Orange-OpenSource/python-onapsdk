"""AAI service-design-and-creation module."""
from typing import Iterator
from urllib.parse import urlencode

from onapsdk.utils.jinja import jinja_env

from .aai_element import AaiElement


class Service(AaiElement):
    """SDC service class."""

    def __init__(self, service_id: str, service_description: str, resource_version: str) -> None:
        """Service model initialization.

        Args:
            service_id (str): This gets defined by others to provide a unique ID for the service.
            service_description (str): Description of the service.
            resource_version (str): Used for optimistic concurrency.

        """
        super().__init__()
        self.service_id = service_id
        self.service_description = service_description
        self.resource_version = resource_version

    def __repr__(self) -> str:
        """Service object description.

        Returns:
            str: Service object description

        """
        return (
            f"Service(service_id={self.service_id}, "
            f"service_description={self.service_description}, "
            f"resource_version={self.resource_version})"
        )

    @property
    def url(self) -> str:
        """Service object url.

        Returns:
            str: Service object url address

        """
        return (f"{self.base_url}{self.api_version}/service-design-and-creation/services/service/"
                f"{self.service_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls,
                service_id: str = None,
                service_description: str = None) -> Iterator["Service"]:
        """Services iterator.

        Stand-in for service model definitions.

        Returns:
            Iterator[Service]: Service

        """
        filter_parameters: dict = cls.filter_none_key_values(
            {"service-id": service_id, "service-description": service_description}
        )
        url: str = (f"{cls.base_url}{cls.api_version}/service-design-and-creation/"
                    f"services?{urlencode(filter_parameters)}")
        for service in cls.send_message_json("GET", "get subscriptions", url).get("service", []):
            yield Service(
                service_id=service["service-id"],
                service_description=service["service-description"],
                resource_version=service["resource-version"],
            )

    @classmethod
    def create(cls,
               service_id: str,
               service_description: str) -> None:
        """Create service.

        Args:
            service_id (str): service ID
            service_description (str): service description

        """
        cls.send_message(
            "PUT",
            "Create A&AI service",
            f"{cls.base_url}{cls.api_version}/service-design-and-creation/"
            f"services/service/{service_id}",
            data=jinja_env()
            .get_template("aai_service_create.json.j2")
            .render(
                service_id=service_id,
                service_description=service_description
            )
        )


class Model(AaiElement):
    """Model resource class."""

    def __init__(self, invariant_id: str, model_type: str, resource_version: str) -> None:
        """Model object initialization.

        Args:
            invariant_id (str): invariant id
            model_type (str): model type
            resource_version (str): resource version

        """
        super().__init__()
        self.invariant_id: str = invariant_id
        self.model_type: str = model_type
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Model object representation.

        Returns:
            str: model object representation

        """
        return (f"Model(invatiant_id={self.invariant_id}, "
                f"model_type={self.model_type}, "
                f"resource_version={self.resource_version}")

    @property
    def url(self) -> str:
        """Model instance url.

        Returns:
            str: Model's url

        """
        return (f"{self.base_url}{self.api_version}/service-design-and-creation/models/"
                f"model/{self.invariant_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls) -> Iterator["Model"]:
        """Get all models.

        Yields:
            Model: Model object

        """
        for model in cls.send_message_json("GET",
                                           "Get A&AI sdc models",
                                           (f"{cls.base_url}{cls.api_version}/"
                                            "service-design-and-creation/models")).get("model",
                                                                                       []):
            yield Model(
                invariant_id=model.get("model-invariant-id"),
                model_type=model.get("model-type"),
                resource_version=model.get("resource-version")
            )
