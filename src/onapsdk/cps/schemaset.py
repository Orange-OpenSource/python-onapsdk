# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK CPS schemaset module."""

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from .cps_element import CpsElement

if TYPE_CHECKING:
    from .dataspace import Dataspace  # pylint: disable=cyclic-import


@dataclass
class SchemaSetModuleReference:
    """Schema set module reference dataclass.

    Stores all information about module reference.
    """

    name: str
    namespace: str
    revision: str


class SchemaSet(CpsElement):
    """Schema set class."""

    def __init__(self,
                 name: str,
                 dataspace: "Dataspace",
                 module_references: Optional[List[SchemaSetModuleReference]] = None) -> None:
        """Initialize schema set class object.

        Args:
            name (str): Schema set name
            dataspace (Dataspace): Dataspace on which schema set was created.
            module_references (Optional[List[SchemaSetModuleReference]], optional):
                List of module references. Defaults to None.
        """
        super().__init__()
        self.name: str = name
        self.dataspace: "Dataspace" = dataspace
        self.module_refences: List[SchemaSetModuleReference] = module_references \
            if module_references else []

    def __repr__(self) -> str:
        """Human readable representation of the object.

        Returns:
            str: Human readable string

        """
        return f"SchemaSet(name={self.name}, dataspace={self.dataspace.name})"

    def delete(self) -> None:
        """Delete schema set."""
        self.send_message(
            "DELETE",
            f"Delete {self.name} schema set",
            f"{self._url}/cps/api/v1/dataspaces/{self.dataspace.name}/schema-sets/{self.name}"
        )
