"""A&AI owning entity module."""

from uuid import uuid4
from typing import Iterator

from onapsdk.utils.jinja import jinja_env
from onapsdk.exceptions import ResourceNotFound

from ..aai_element import AaiElement


class OwningEntity(AaiElement):
    """Owning entity class."""

    def __init__(self, name: str, owning_entity_id: str, resource_version: str) -> None:
        """Owning entity object initialization.

        Args:
            name (str): Owning entity name
            owning_entity_id (str): owning entity ID
            resource_version (str): resource version
        """
        super().__init__()
        self.name: str = name
        self.owning_entity_id: str = owning_entity_id
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Owning entity object representation.

        Returns:
            str: Owning entity object representation

        """
        return f"OwningEntity(name={self.name}, owning_entity_id={self.owning_entity_id})"

    @property
    def url(self) -> str:
        """Owning entity object url.

        Returns:
            str: Url

        """
        return (f"{self.base_url}{self.api_version}/business/owning-entities/owning-entity/"
                f"{self.owning_entity_id}?resource-version={self.resource_version}")

    @classmethod
    def get_all(cls) -> Iterator["OwningEntity"]:
        """Get all owning entities.

        Yields:
            OwningEntity: OwningEntity object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/owning-entities"
        for owning_entity in cls.send_message_json("GET",
                                                   "Get A&AI owning entities",
                                                   url).get("owning-entity", []):
            yield cls(
                owning_entity.get("owning-entity-name"),
                owning_entity.get("owning-entity-id"),
                owning_entity.get("resource-version")
            )

    @classmethod
    def get_by_owning_entity_id(cls, owning_entity_id: str) -> "OwningEntity":
        """Get owning entity by it's ID.

        Args:
            owning_entity_id (str): owning entity object id

        Returns:
            OwningEntity: OwningEntity object

        """
        response: dict = cls.send_message_json(
            "GET",
            "Get A&AI owning entity",
            (f"{cls.base_url}{cls.api_version}/business/owning-entities/"
             f"owning-entity/{owning_entity_id}")
        )
        return cls(
            response.get("owning-entity-name"),
            response.get("owning-entity-id"),
            response.get("resource-version")
        )

    @classmethod
    def get_by_owning_entity_name(cls, owning_entity_name: str) -> "OwningEntity":
        """Get owning entity resource by it's name.

        Raises:
            ResourceNotFound: Owning entity requested by a name does not exist.

        Returns:
            OwningEntity: Owning entity requested by a name.

        """
        for owning_entity in cls.get_all():
            if owning_entity.name == owning_entity_name:
                return owning_entity

        msg = f'Owning entity "{owning_entity_name}" does not exist.'
        raise ResourceNotFound(msg)

    @classmethod
    def create(cls, name: str, owning_entity_id: str = None) -> "OwningEntity":
        """Create owning entity A&AI resource.

        Args:
            name (str): owning entity name
            owning_entity_id (str): owning entity ID. Defaults to None.

        Returns:
            OwningEntity: Created OwningEntity object

        """
        if not owning_entity_id:
            owning_entity_id = str(uuid4())
        cls.send_message(
            "PUT",
            "Declare A&AI owning entity",
            (f"{cls.base_url}{cls.api_version}/business/owning-entities/"
             f"owning-entity/{owning_entity_id}"),
            data=jinja_env().get_template("aai_owning_entity_create.json.j2").render(
                owning_entity_name=name,
                owning_entity_id=owning_entity_id
            )
        )
        return cls.get_by_owning_entity_id(owning_entity_id)
