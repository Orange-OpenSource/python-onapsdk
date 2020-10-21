# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC category management module."""

import json
from abc import ABC

from onapsdk.configuration import settings
from onapsdk.onap_service import OnapService
from onapsdk.sdc import SDC
from onapsdk.utils.headers_creator import headers_sdc_generic


class BaseCategory(OnapService, ABC):
    """Base SDC category class.

    It's SDC admin resource, has no common properties with
        SDC resourcer or elements, so SDC class can't be it's
        base class.

    """

    SDC_ADMIN_USER = "demo"
    URL = f"{settings.SDC_FE_URL}/sdc1/feProxy/rest/v1/category"

    def __init__(self, name: str) -> None:
        """Service category initialization.

        Args:
            name (str): Service category name.

        """
        super().__init__()
        self.name: str = name

    @classmethod
    def create(cls, name: str) -> "BaseCategory":
        """Create category object.

        Sends request to SDC to create new category with given name.

        Args:
            name (str): New category name

        Raises:
            ValueError: Category with given name already exists
                or API returns response with error code.

        Returns:
            BaseCategory: Newly created category

        """
        cls.send_message_json("POST",
                              f"Create {name} {cls.__class__.__name__}",
                              cls.URL,
                              data=json.dumps({"name": name}),
                              headers=headers_sdc_generic(SDC.headers, user=cls.SDC_ADMIN_USER),
                              exception=ValueError)
        return cls(name=name)


class ResourceCategory(BaseCategory):
    """Resource category class."""

    URL = f"{BaseCategory.URL}/resources"


class ServiceCategory(BaseCategory):
    """Service category class."""

    URL = f"{BaseCategory.URL}/services"
