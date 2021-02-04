"""CDS Blueprint Models module."""

from typing import Iterator
from onapsdk.exceptions import ResourceNotFound  # for custom exceptions

from .blueprint import Blueprint
from .cds_element import CdsElement


class BlueprintModel(CdsElement):  # pylint: disable=too-many-instance-attributes
    """Blueprint Model class.

    Represents blueprint models in CDS
    """

    def __init__(self,  # pylint: disable=too-many-arguments
                 blueprint_model_id: str,
                 artifact_uuid: str = None,
                 artifact_type: str = None,
                 artifact_version: str = None,
                 artifact_description: str = None,
                 internal_version: str = None,
                 created_date: str = None,
                 artifact_name: str = None,
                 published: str = 'N',
                 updated_by: str = None,
                 tags: str = None):
        """Blueprint Model initialization.

        Args:
            blueprint_model_id (str): Blueprint model identifier
            artifact_uuid (str): Blueprint model uuid
            artifact_type (str): Blueprint artifact type
            artifact_version (str): Blueprint model version
            artifact_description (str): Blueprint model description
            internal_version (str): Blueprint model internal version
            created_date (str): Blueprint model created date
            artifact_name (str): Blueprint model name
            published (str): Blueprint model publish status - 'N' or 'Y'
            updated_by (str): Blueprint model author
            tags (str): Blueprint model tags

        """
        super().__init__()
        self.blueprint_model_id = blueprint_model_id
        self.artifact_uuid = artifact_uuid
        self.artifact_type = artifact_type
        self.artifact_version = artifact_version
        self.artifact_description = artifact_description
        self.internal_version = internal_version
        self.created_date = created_date
        self.artifact_name = artifact_name
        self.published = published
        self.updated_by = updated_by
        self.tags = tags

    def __repr__(self) -> str:
        """Representation of object.

        Returns:
           str: Object's string representation

        """
        return (f"BlueprintModel(artifact_name='{self.artifact_name}', "
                f"blueprint_model_id='{self.blueprint_model_id}')")

    @classmethod
    def get_by_id(cls, blueprint_model_id: str) -> "BlueprintModel":
        """Retrieve blueprint model with provided ID.

        Args: blueprint_model_id (str):

        Returns:
            BlueprintModel: Blueprint model object

        Raises:
            ResourceNotFound: Blueprint model with provided ID doesn't exist

        """
        try:
            blueprint_model = cls.send_message_json(
                "GET",
                "Retrieve blueprint",
                f"{cls._url}/api/v1/blueprint-model/{blueprint_model_id}",
                auth=cls.auth)

            return cls(
                blueprint_model_id=blueprint_model["blueprintModel"]['id'],
                artifact_uuid=blueprint_model["blueprintModel"]['artifactUUId'],
                artifact_type=blueprint_model["blueprintModel"]['artifactType'],
                artifact_version=blueprint_model["blueprintModel"]['artifactVersion'],
                internal_version=blueprint_model["blueprintModel"]['internalVersion'],
                created_date=blueprint_model["blueprintModel"]['createdDate'],
                artifact_name=blueprint_model["blueprintModel"]['artifactName'],
                published=blueprint_model["blueprintModel"]['published'],
                updated_by=blueprint_model["blueprintModel"]['updatedBy'],
                tags=blueprint_model["blueprintModel"]['tags']
            )

        except ResourceNotFound:
            raise ResourceNotFound(f"BlueprintModel blueprint_model_id='{blueprint_model_id}"
                                   f" not found")

    @classmethod
    def get_by_name_and_version(cls, blueprint_name: str,
                                blueprint_version: str) -> "BlueprintModel":
        """Retrieve blueprint model with provided name and version.

        Args:
            blueprint_name (str): Blueprint model name
            blueprint_version (str): Blueprint model version

        Returns:
            BlueprintModel: Blueprint model object

        Raises:
            ResourceNotFound: Blueprint model with provided name and version doesn't exist

        """
        try:
            blueprint_model = cls.send_message_json(
                "GET",
                "Retrieve blueprint",
                f"{cls._url}/api/v1/blueprint-model/by-name/{blueprint_name}"
                f"/version/{blueprint_version}",
                auth=cls.auth)

            return cls(
                blueprint_model_id=blueprint_model["blueprintModel"]['id'],
                artifact_uuid=blueprint_model["blueprintModel"]['artifactUUId'],
                artifact_type=blueprint_model["blueprintModel"]['artifactType'],
                artifact_version=blueprint_model["blueprintModel"]['artifactVersion'],
                internal_version=blueprint_model["blueprintModel"]['internalVersion'],
                created_date=blueprint_model["blueprintModel"]['createdDate'],
                artifact_name=blueprint_model["blueprintModel"]['artifactName'],
                published=blueprint_model["blueprintModel"]['published'],
                updated_by=blueprint_model["blueprintModel"]['updatedBy'],
                tags=blueprint_model["blueprintModel"]['tags']
            )

        except ResourceNotFound:
            raise ResourceNotFound(f"BlueprintModel blueprint_name='{blueprint_name}"
                                   f" and blueprint_version='{blueprint_version}' not found")

    @classmethod
    def get_all(cls) -> Iterator["BlueprintModel"]:
        """Get all blueprint models.

        Yields:
            BlueprintModel: BlueprintModel object.

        """
        for blueprint_model in cls.send_message_json(
                "GET",
                "Retrieve all blueprints",
                f"{cls._url}/api/v1/blueprint-model",
                auth=cls.auth):

            yield cls(
                blueprint_model_id=blueprint_model["blueprintModel"]['id'],
                artifact_uuid=blueprint_model["blueprintModel"]['artifactUUId'],
                artifact_type=blueprint_model["blueprintModel"]['artifactType'],
                artifact_version=blueprint_model["blueprintModel"]['artifactVersion'],
                internal_version=blueprint_model["blueprintModel"]['internalVersion'],
                created_date=blueprint_model["blueprintModel"]['createdDate'],
                artifact_name=blueprint_model["blueprintModel"]['artifactName'],
                published=blueprint_model["blueprintModel"]['published'],
                updated_by=blueprint_model["blueprintModel"]['updatedBy'],
                tags=blueprint_model["blueprintModel"]['tags']
            )

    def get_blueprint(self) -> Blueprint:
        """Get Blueprint object for selected blueprint model.

        Returns:
            Blueprint: Blueprint object

        """
        cba_package = self.send_message(
            "GET",
            "Retrieve selected blueprint object",
            f"{self._url}/api/v1/blueprint-model/download/{self.blueprint_model_id}",
            auth=self.auth)

        return Blueprint(cba_file_bytes=cba_package.content)

    def save(self, dst_file_path: str):
        """Save blueprint model to file.

        Args:
            dst_file_path (str): Path of file where blueprint is going to be saved
        """
        cba_package = self.send_message(
            "GET",
            "Retrieve and save selected blueprint",
            f"{self._url}/api/v1/blueprint-model/download/{self.blueprint_model_id}",
            auth=self.auth)

        with open(dst_file_path, "wb") as content:
            for chunk in cba_package.iter_content(chunk_size=128):
                content.write(chunk)

    def delete(self):
        """Delete blueprint model."""
        self.send_message(
            "DELETE",
            "Delete blueprint",
            f"{self._url}/api/v1/blueprint-model/{self.blueprint_model_id}",
            auth=self.auth)
