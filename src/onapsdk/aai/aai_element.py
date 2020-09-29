#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""AAI Element module."""
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_aai_creator
from onapsdk.utils.jinja import jinja_env


@dataclass
class Relationship:
    """Relationship class.

    A&AI elements could have relationship with other A&AI elements.
    Relationships are represented by this class objects.
    """

    related_to: str
    related_link: str
    relationship_data: List[Dict[str, str]]
    relationship_label: str = ""
    related_to_property: List[Dict[str, str]] = field(default_factory=list)


class AaiElement(OnapService):
    """Mother Class of all A&AI elements."""

    name: str = "AAI"
    server: str = "AAI"
    base_url = settings.AAI_URL
    api_version = "/aai/" + settings.AAI_API_VERSION
    headers = headers_aai_creator(OnapService.headers)

    @classmethod
    def filter_none_key_values(cls, dict_to_filter: Dict[str, Optional[str]]) -> Dict[str, str]:
        """Filter out None key values from dictionary.

        Iterate throught given dictionary and filter None values.

        Args:
            dict_to_filter (Dict): Dictionary to filter out None

        Returns:
            Dict[str, str]: Filtered dictionary

        """
        return dict(
            filter(lambda key_value_tuple: key_value_tuple[1] is not None, dict_to_filter.items(),)
        )

    @property
    def url(self) -> str:
        """Resource's url.

        Returns:
            str: Resource's url

        """
        raise NotImplementedError

    @property
    def relationships(self) -> Iterator[Relationship]:
        """Resource relationships iterator.

        Yields:
            Relationship: resource relationship

        """
        for relationship in self.send_message_json("GET",
                                                   "Get object relationships",
                                                   f"{self.url}/relationship-list")\
                                                       .get("relationship", []):
            yield Relationship(
                related_to=relationship.get("related-to"),
                relationship_label=relationship.get("relationship-label"),
                related_link=relationship.get("related-link"),
                relationship_data=relationship.get("relationship-data"),
            )

    def add_relationship(self, relationship: Relationship) -> None:
        """Add relationship to aai resource.

        Add relationship to resource using A&AI API

        Args:
            relationship (Relationship): Relationship to add

        """
        self.send_message(
            "PUT",
            "add relationship to cloud region",
            f"{self.url}/relationship-list/relationship",
            data=jinja_env()
            .get_template("aai_add_relationship.json.j2")
            .render(relationship=relationship),
        )
