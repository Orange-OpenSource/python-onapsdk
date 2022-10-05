# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK CPS dataspace module."""

from functools import wraps
from glob import glob
import inspect
import types
from typing import Any, Dict, Iterable
from onapsdk.exceptions import (APIError, ResourceNotFound, SDKException)
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

    def exception_handler(function): # pylint: disable= no-self-argument
        """Exception handler.
        Handling APIError and throwing ResourceNotFound if Data space does not exist and throwing 
        SDKException if Generic exception for ONAP SDK occures for
        create_anchor(), get_anchors(), get_anchor(), get_schema_set(), create_schema_set()
        """
        @wraps(function)
        def wrapper(*args):
            try:
                ret = function(*args) # pylint: disable= not-callable
                if isinstance(ret, types.GeneratorType):
                    yield from ret
                else:
                    return ret
            #   return function(*args) # pylint: disable= not-callable
            except APIError as error:
                if (error.response_status_code == 400 and 'Dataspace not found' in str(error)):
                    raise ResourceNotFound(error) from error
                raise
        return wrapper

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

    @exception_handler
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

    @exception_handler
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

    @exception_handler
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

    @exception_handler
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

    @exception_handler
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
