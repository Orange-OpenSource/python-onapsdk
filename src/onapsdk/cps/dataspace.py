# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK CPS dataspace module."""

from typing import Any, Dict, Iterable

from .anchor import Anchor
from .cps_element import CpsElement
from .schemaset import SchemaSet, SchemaSetModuleReference


class Dataspace(CpsElement):
    """CPS dataspace class."""

    def __init__(self, name: str) -> None:
        """Initialize dataspace object.

        Args:
            name (str): Dataspace name

        """
        super().__init__()
        self.name: str = name

    def __repr__(self) -> str:
        """Human readable representation of the object.

        Returns:
            str: Human readable string

        """
        return f"Dataspace(name={self.name})"

    @property
    def url(self) -> str:
        """Dataspace url.

        Returns:
            str: Dataspace url

        """
        return f"{self._url}/cps/api/v1/dataspaces/{self.name}"

    @classmethod
    def create(cls, dataspace_name: str) -> "Dataspace":
        """Create dataspace with given name.

        Args:
            dataspace_name (str): Dataspace name

        Returns:
            Dataspace: Newly created dataspace

        """
        cls.send_message(
            "POST",
            f"Create {dataspace_name} dataspace",
            f"{cls._url}/cps/api/v1/dataspaces?dataspace-name={dataspace_name}",
            auth=cls.auth
        )
        return Dataspace(dataspace_name)

    def create_anchor(self, schema_set: SchemaSet, anchor_name: str) -> Anchor:
        """Create anchor.

        Args:
            schema_set (SchemaSet): Schema set object which is going to be used to create anchor.
            anchor_name (str): Anchor name

        Returns:
            Anchor: Created anchor

        """
        self.send_message(
            "POST",
            "Get all CPS dataspace schemasets",
            f"{self.url}/anchors/?schema-set-name={schema_set.name}&anchor-name={anchor_name}",
            auth=self.auth
        )
        return Anchor(name=anchor_name, schema_set=schema_set)

    def get_anchors(self) -> Iterable[Anchor]:
        """Get all dataspace's anchors.

        Iterable of related with dataspace anchors.

        Yields:
            Iterator[Anchor]: Anchor object

        """
        for anchor_data in self.send_message_json(\
            "GET",\
            "Get all CPS dataspace anchors",\
            f"{self.url}/anchors",\
            auth=self.auth\
        ):
            yield Anchor(name=anchor_data["name"],
                         schema_set=SchemaSet(name=anchor_data["schemaSetName"],
                                              dataspace=self))

    def get_anchor(self, anchor_name: str) -> Anchor:
        """Get dataspace anchor by name.

        To get anchor there is no need to use `SchemaSet` object, but to create anchor it it.

        Args:
            anchor_name (str): Anchor name.

        Returns:
            Anchor: Anchor object

        """
        anchor_data: Dict[str, Any] = self.send_message_json(
            "GET",
            f"Get {anchor_name} anchor",
            f"{self.url}/anchors/{anchor_name}",
            auth=self.auth
        )
        return Anchor(name=anchor_data["name"],
                      schema_set=SchemaSet(name=anchor_data["schemaSetName"],
                                           dataspace=self))

    def get_schema_set(self, schema_set_name: str) -> SchemaSet:
        """Get schema set by name.

        Args:
            schema_set_name (str): Schema set name

        Returns:
            SchemaSet: Schema set object

        """
        schema_set_data: Dict[str, Any] = self.send_message_json(
            "GET",
            "Get all CPS dataspace schemasets",
            f"{self._url}/cps/api/v1/dataspaces/{self.name}/schema-sets/{schema_set_name}",
            auth=self.auth
        )
        return SchemaSet(
            name=schema_set_data["name"],
            dataspace=self,
            module_references=[
                SchemaSetModuleReference(
                    name=module_reference_data["name"],
                    namespace=module_reference_data["namespace"],
                    revision=module_reference_data["revision"]
                ) for module_reference_data in schema_set_data["moduleReferences"]
            ]
        )

    def create_schema_set(self, schema_set_name: str, schema_set: bytes) -> SchemaSet:
        """Create schema set.

        Create CPS schema set in dataspace

        Args:
            schema_set_name (str): Schema set name
            schema_set (bytes): Schema set YANG

        Returns:
            SchemaSet: Created schema set object

        """
        self.send_message(
            "POST",
            "Create schema set",
            f"{self._url}/cps/api/v1/dataspaces/{self.name}/schema-sets/",
            files={"file": schema_set},
            data={"schema-set-name": schema_set_name},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth
        )
        return self.get_schema_set(schema_set_name)

    def delete(self) -> None:
        """Delete dataspace."""
        self.send_message(
            "DELETE",
            f"Delete {self.name} dataspace",
            f"{self._url}/cps/api/v1/dataspaces/{self.name}",
            auth=self.auth
        )
