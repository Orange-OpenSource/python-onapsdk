#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""VID module."""
from abc import ABC

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
from onapsdk.utils.jinja import jinja_env


class Vid(OnapService, ABC):
    """VID base class."""

    base_url = settings.VID_URL
    api_version = settings.VID_API_VERSION

    def __init__(self, name: str) -> None:
        """VID resource object initialization.

        Args:
            name (str): Resource name
        """
        super().__init__()
        self.name: str = name

    @classmethod
    def get_create_url(cls) -> str:
        """Resource url.

        Used to create resources

        Returns:
            str: Url used for resource creation

        """
        raise NotImplementedError

    @classmethod
    def create(cls, name: str) -> "Vid":
        """Create VID resource.

        Returns:
            Vid: Created VID resource

        """
        cls.send_message(
            "POST",
            f"Declare VID resource with {name} name",
            cls.get_create_url(),
            data=jinja_env().get_template("vid_declare_resource.json.j2").render(
                name=name
            )
        )
        return cls(name)


class OwningEntity(Vid):
    """VID owning entity class."""

    @classmethod
    def get_create_url(cls) -> str:
        """Owning entity creation url.

        Returns:
            str: Url used for ownint entity creation

        """
        return f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/owningEntity"


class Project(Vid):
    """VID project class."""

    @classmethod
    def get_create_url(cls) -> str:
        """Project creation url.

        Returns:
            str: Url used for project creation

        """
        return f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/project"


class LineOfBusiness(Vid):
    """VID line of business class."""

    @classmethod
    def get_create_url(cls) -> str:
        """Line of business creation url.

        Returns:
            str: Url used for line of business creation

        """
        return f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/lineOfBusiness"


class Platform(Vid):
    """VID platform class."""

    @classmethod
    def get_create_url(cls) -> str:
        """Platform creation url.

        Returns:
            str: Url used for platform creation

        """
        return f"{cls.base_url}{cls.api_version}/maintenance/category_parameter/platform"
