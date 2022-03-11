# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK CPS anchor module."""

from typing import Any, Dict, TYPE_CHECKING

from .cps_element import CpsElement

if TYPE_CHECKING:
    from .schemaset import SchemaSet  # pylint: disable=cyclic-import


class Anchor(CpsElement):
    """CPS anchor class."""

    def __init__(self, name: str, schema_set: "SchemaSet") -> None:
        """Initialise CPS anchor object.

        Args:
            name (str): Anchor name
            schema_set (SchemaSet): Schema set

        """
        super().__init__()
        self.name: str = name
        self.schema_set: "SchemaSet" = schema_set

    def __repr__(self) -> str:
        """Human readable representation of the object.

        Returns:
            str: Human readable string

        """
        return f"Anchor(name={self.name}, "\
               f"schema set={self.schema_set.name}, "\
               f"dataspace={self.schema_set.dataspace.name})"

    @property
    def url(self) -> str:
        """Anchor url.

        Returns:
            str: Anchor url

        """
        return f"{self._url}/cps/api/v1/dataspaces/"\
               f"{self.schema_set.dataspace.name}/anchors/{self.name}"

    def delete(self) -> None:
        """Delete anchor."""
        self.send_message(
            "DELETE",
            f"Delete {self.name} anchor",
            self.url,
            auth=self.auth
        )

    def create_node(self, node_data: str) -> None:
        """Create anchor node.

        Fill CPS anchor with a data.

        Args:
            node_data (str): Node data. Should be JSON formatted.

        """
        self.send_message(
            "POST",
            f"Create {self.name} anchor node",
            f"{self.url}/nodes",
            data=node_data,
            auth=self.auth
        )

    def get_node(self, xpath: str, include_descendants: bool = False) -> Dict[Any, Any]:
        """Get anchor node data.

        Using XPATH get anchor's node data.

        Args:
            xpath (str): Anchor node xpath.
            include_descendants (bool, optional): Determies if descendants should be included in
                response. Defaults to False.

        Returns:
            Dict[Any, Any]: Anchor node data.

        """
        return self.send_message_json(
            "GET",
            f"Get {self.name} anchor node with {xpath} xpath",
            f"{self.url}/node?xpath={xpath}&include-descendants={include_descendants}",
            auth=self.auth
        )

    def update_node(self, xpath: str, node_data: str) -> None:
        """Update anchor node data.

        Using XPATH update anchor's node data.

        Args:
            xpath (str): Anchor node xpath.
            node_data (str): Node data.

        """
        self.send_message(
            "PATCH",
            f"Update {self.name} anchor node with {xpath} xpath",
            f"{self.url}/nodes?xpath={xpath}",
            data=node_data,
            auth=self.auth
        )

    def replace_node(self, xpath: str, node_data: str) -> None:
        """Replace anchor node data.

        Using XPATH replace anchor's node data.

        Args:
            xpath (str): Anchor node xpath.
            node_data (str): Node data.

        """
        self.send_message(
            "PUT",
            f"Replace {self.name} anchor node with {xpath} xpath",
            f"{self.url}/nodes?xpath={xpath}",
            data=node_data,
            auth=self.auth
        )

    def add_list_node(self, xpath: str, node_data: str) -> None:
        """Add an element to the list node of an anchor.

        Args:
            xpath (str): Xpath to the list node.
            node_data (str): Data to be added.

        """
        self.send_message(
            "POST",
            f"Add element to {self.name} anchor node with {xpath} xpath",
            f"{self.url}/list-nodes?xpath={xpath}",
            data=node_data,
            auth=self.auth
        )

    def query_node(self, query: str, include_descendants: bool = False) -> Dict[Any, Any]:
        """Query CPS anchor data.

        Args:
            query (str): Query
            include_descendants (bool, optional):  Determies if descendants should be included in
                response. Defaults to False.

        Returns:
            Dict[Any, Any]: Query return values.

        """
        return self.send_message_json(
            "GET",
            f"Get {self.name} anchor node with {query} query",
            f"{self.url}/nodes/query?cps-path={query}&include-descendants={include_descendants}",
            auth=self.auth
        )

    def delete_nodes(self, xpath: str) -> None:
        """Delete nodes.

        Use XPATH to delete Anchor nodes.

        Args:
            xpath (str): Nodes to delete

        """
        self.send_message(
            "DELETE",
            f"Delete {self.name} anchor nodes with {xpath} xpath",
            f"{self.url}/nodes?xpath={xpath}",
            auth=self.auth
        )
