"""CDS Blueprint Models module."""
from typing import Iterator

from .blueprint import Blueprint
from .cds_element import CdsElement


class BlueprintModel(CdsElement):  # pylint: disable=too-many-instance-attributes
    """Blueprint Model class

    Represents blueprint models in CDS
    """

    def __init__(self,
                 blueprint_model_id,
                 artifact_uuid=None,
                 artifact_type=None,
                 artifact_version=None,
                 artifact_description=None,
                 internal_version=None,
                 created_date=None,
                 artifact_name=None,
                 published='N',
                 updated_by=None,
                 tags=None):

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
        """Retrieve blueprint model with provided ID

        Args: blueprint_model_id (str):

        Returns:
            BlueprintModel: Blueprint model object

        Raises:
            ValueError: Blueprint model with provided ID doesn't exist
        """

        try:
            blueprint_model = cls.send_message_json(
                    "GET",
                    "Retrieve all blueprints",
                    f"{cls._url}/api/v1/blueprint-model/{blueprint_model_id}",
                    headers={},
                    auth=cls.auth,
                    exception=ValueError)

            return BlueprintModel(
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

        except ValueError:
            raise ValueError(f"BlueprintModel blueprint_model_id='{blueprint_model_id} not found")

    @classmethod
    def get_by_name_and_version(cls, blueprint_name: str,
                                blueprint_version: str) -> "BlueprintModel":
        """Retrieve blueprint model with provided name and version

        Args:
            blueprint_name (str): Blueprint model name
            blueprint_version (str): Blueprint model version

        Returns:
            BlueprintModel: Blueprint model object

        Raises:
            ValueError: Blueprint model with provided name and version doesn't exist
        """

        try:
            blueprint_model = cls.send_message_json(
                    "GET",
                    "Retrieve all blueprints",
                    f"{cls._url}/api/v1/blueprint-model/by-name/{blueprint_name}"
                    f"/version/{blueprint_version}",
                    headers={},
                    auth=cls.auth,
                    exception=ValueError)

            return BlueprintModel(
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

        except ValueError:
            raise ValueError(f"BlueprintModel blueprint_name='{blueprint_name}"
                             f" and blueprint_version='{blueprint_version}' not found")

    @classmethod
    def get_all(cls) -> Iterator["BlueprintModel"]:
        """Get all blueprint models

        Yields:
            BlueprintModel: BlueprintModel object.
        """

        for blueprint_model in cls.send_message_json(
                "GET",
                "Retrieve all blueprints",
                f"{cls._url}/api/v1/blueprint-model",
                headers={},
                auth=cls.auth,
                exception=ValueError):

            yield BlueprintModel(
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
        """Get Blueprint object for selected blueprint model

        Returns:
            Blueprint: Blueprint object
        """

        cba_package = self.send_message(
            "GET",
            "Retrieve selected blueprints",
            f"{self._url}/api/v1/blueprint-model/download/{self.blueprint_model_id}",
            headers={},
            auth=self.auth,
            exception=ValueError)

        return Blueprint(cba_file_bytes=cba_package.content)

    def save(self, dst_file_path: str):
        """Save blueprint model to file

        Args:
            dst_file_path (str): Path of file where blueprint is going to be saved
        """

        cba_package = self.send_message(
            "GET",
            "Retrieve selected blueprints",
            f"{self._url}/api/v1/blueprint-model/download/{self.blueprint_model_id}",
            headers={},
            auth=self.auth,
            exception=ValueError)

        with open(dst_file_path, "wb") as content:
            for chunk in cba_package.iter_content(chunk_size=128):
                content.write(chunk)
        return

    def delete(self):
        """Delete blueprint model"""

        self.send_message(
            "DELETE",
            "Delete blueprint",
            f"{self._url}/api/v1/blueprint-model/{self.blueprint_model_id}",
            headers={},
            auth=self.auth,
            exception=ValueError)
        return
