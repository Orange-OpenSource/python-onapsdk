"""Instantiation module."""
from typing import Iterator
from dataclasses import dataclass

from onapsdk.msb import MSB
from onapsdk.utils.jinja import jinja_env


# pylint: disable=too-many-arguments
@dataclass
class InstantiationRequest:
    """Instantiation Request class."""

    def __init__(self, request: dict) -> None:
        """Request object initialization.

        Args:
            cloud_region_id (str): Cloud region ID
            profile_name (str): Name of profile
            rb_name (str): Definition name
            rb_version (str): Definition version
            override_values (dict): Optional parameters
            labels (dict): Optional labels
        """
        super().__init__()
        self.cloud_region_id: str = request["cloud-region"]
        self.profile_name: str = request["profile-name"]
        self.rb_name: str = request["rb-name"]
        self.rb_version: str = request["rb-version"]
        self.override_values: dict = request["override-values"]
        self.labels: dict = request["labels"]


@dataclass
class InstantiationParameter:
    """Class to store instantiation parameters used to pass override_values and labels.

    Contains two values: name of parameter and it's value
    """

    name: str
    value: str


class Instance(MSB):
    """Instance class."""

    base_url = f"{MSB.base_url}/api/multicloud-k8s/v1/v1/instance"

    def __init__(self, instance_id: str,
                 namespace: str,
                 request: InstantiationRequest,
                 resources: dict = None,
                 override_values: dict = None) -> None:
        """Instance object initialization.

        Args:
            instance_id (str): instance ID
            namespace (str): namespace that instance is created in
            request (InstantiationRequest): datails of the instantiation request
            resources (dict): Created resources
            override_values (dict): Optional values
        """
        super().__init__()
        self.instance_id: str = instance_id
        self.namespace: str = namespace
        self.request: InstantiationRequest = request
        self.resources: dict = resources
        self.override_values: dict = override_values

    @property
    def url(self) -> str:
        """URL address.

        Returns:
            str: URL to Instance

        """
        return f"{self.base_url}/{self.instance_id}"

    @classmethod
    def get_all(cls) -> Iterator["Instance"]:
        """Get all instantiated Kubernetes resources.

        Yields:
            Instantiation: Instantiation object

        """
        for resource in cls.send_message_json("GET",
                                              "Get Kubernetes resources",
                                              cls.base_url):
            yield cls(
                instance_id=resource["id"],
                namespace=resource["namespace"],
                request=InstantiationRequest(resource["request"])
            )

    @classmethod
    def get_by_id(cls, instance_id: str) -> "Instance":
        """Get Kubernetes resource by id.

        Args:
            instance_id (str): instance ID

        Returns:
            Instantiation: Instantiation object

        """
        url: str = f"{cls.base_url}/{instance_id}"
        resource: dict = cls.send_message_json(
            "GET",
            "Get Kubernetes resource by id",
            url
        )
        return cls(
            instance_id=resource["id"],
            namespace=resource["namespace"],
            request=InstantiationRequest(resource["request"]),
            resources=resource["resources"],
            override_values=resource.get("override-values")
        )

    @classmethod
    def create(cls,
               cloud_region_id: str,
               profile_name: str,
               rb_name: str,
               rb_version: str,
               override_values: dict = None,
               labels: dict = None) -> "Instance":
        """Create Instance.

        Args:
            cloud_region_id (str): Cloud region ID
            profile_name (str): Name of profile to be instantiated
            rb_name: (bytes): Definition name
            rb_version (str): Definition version
            override_values (dict): List of optional override values
            labels (dict): List of optional labels

        Returns:
            Instance: Created object

        """
        if labels is None:
            labels = {}
        if override_values is None:
            override_values = {}
        url: str = f"{cls.base_url}"
        response: dict = cls.send_message_json(
            "POST",
            "Create Instance",
            url,
            data=jinja_env().get_template("multicloud_k8s_instantiate.json.j2").render(
                cloud_region_id=cloud_region_id,
                profile_name=profile_name,
                rb_name=rb_name,
                rb_version=rb_version,
                override_values=override_values,
                labels=labels),
            headers={}
        )
        return cls(
            instance_id=response["id"],
            namespace=response["namespace"],
            request=InstantiationRequest(response["request"]),
            resources=response["resources"],
            override_values=response.get("override-values")
        )

    def delete(self) -> None:
        """Delete Instance object."""
        self.send_message(
            "DELETE",
            f"Delete {self.instance_id} instance",
            self.url
        )
