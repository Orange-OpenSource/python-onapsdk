"""Definition module."""
from typing import Iterator
from dataclasses import dataclass

from onapsdk.utils.jinja import jinja_env
from ..msb_service import MSB


# pylint: disable=too-many-arguments, too-few-public-methods
class DefinitionBase(MSB):
    """DefinitionBase class."""

    base_url = f"{MSB.base_url}/api/multicloud-k8s/v1/v1/rb/definition"

    def __init__(self, rb_name: str,
                 rb_version: str) -> None:
        """Definition-Base object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
        """
        super().__init__()
        self.rb_name: str = rb_name
        self.rb_version: str = rb_version

    @property
    def url(self) -> str:
        """URL address for Definition Based calls.

        Returns:
            str: URL to RB Definition

        """
        return f"{self.base_url}/{self.rb_name}/{self.rb_version}"

    def delete(self) -> None:
        """Delete Definition Based object.

        Raises:
            ValueError: request response with HTTP error code

        """
        self.send_message(
            "DELETE",
            f"Delete {self.__class__.__name__}",
            self.url,
            exception=ValueError
        )

    def upload_artifact(self, package: bytes = None):
        """Upload artifact.

        Args:
            package (bytes): Artifact to be uploaded to multicloud-k8s plugin

        Raises:
            ValueError: request response with HTTP error code

        """
        url: str = f"{self.url}/content"
        self.send_message(
            "POST",
            "Upload Artifact content",
            url,
            data=package,
            headers={},
            exception=ValueError
        )


class Definition(DefinitionBase):
    """Definition class."""

    def __init__(self, rb_name: str,
                 rb_version: str,
                 chart_name: str,
                 description: str,
                 labels: dict) -> None:
        """Definition object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            chart_name (str): Chart name, optional field, will be detected if it is not provided
            description (str): Definition description
            labels (str): Labels
        """
        super().__init__(rb_name, rb_version)
        self.rb_name: str = rb_name
        self.rb_version: str = rb_version
        self.chart_name: str = chart_name
        self.description: str = description
        self.labels: dict = labels

    @classmethod
    def get_all(cls):
        """Get all definitions.

        Raises:
            ValueError: request response with HTTP error code

        Yields:
            Definition: Definition object

        """
        for definition in cls.send_message_json("GET",
                                                "Get definitions",
                                                cls.base_url,
                                                exception=ValueError):
            yield cls(
                definition["rb-name"],
                definition["rb-version"],
                definition.get("chart-name"),
                definition.get("description"),
                definition.get("labels")
            )

    @classmethod
    def get_definition_by_name_version(cls, rb_name: str, rb_version: str) -> "Definition":
        """Get definition by it's name and version.

        Args:
            rb_name (str): definition name
            rb_version (str): definition version

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            Definition: Definition object

        """
        url: str = f"{cls.base_url}/{rb_name}/{rb_version}"
        definition: dict = cls.send_message_json(
            "GET",
            "Get definition",
            url,
            exception=ValueError
        )
        return cls(
            definition["rb-name"],
            definition["rb-version"],
            definition.get("chart-name"),
            definition.get("description"),
            definition.get("labels")
        )

    @classmethod
    def create(cls, rb_name: str,
               rb_version: str,
               chart_name: str = "",
               description: str = "",
               labels=None) -> "Definition":
        """Create Definition.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            chart_name (str): Chart name, optional field, will be detected if it is not provided
            description (str): Definition description
            labels (str): Labels

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            Definition: Created object

        """
        if labels is None:
            labels = {}
        url: str = f"{cls.base_url}"
        cls.send_message(
            "POST",
            "Create definition",
            url,
            data=jinja_env().get_template("multicloud_k8s_add_definition.json.j2").render(
                rb_name=rb_name,
                rb_version=rb_version,
                chart_name=chart_name,
                description=description,
                labels=labels
            ),
            exception=ValueError
        )
        return cls.get_definition_by_name_version(rb_name, rb_version)

    def create_profile(self, profile_name: str,
                       namespace: str,
                       kubernetes_version: str,
                       release_name=None) -> "Profile":
        """Create Profile for Definition.

        Args:
            profile_name (str): Name of profile
            namespace (str): Namespace that service is created in
            kubernetes_version (str): Required Kubernetes version
            release_name (str): Release name

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            Profile: Created object

        """
        url: str = f"{self.url}/profile"
        if release_name is None:
            release_name = profile_name
        self.send_message(
            "POST",
            "Create profile for definition",
            url,
            data=jinja_env().get_template("multicloud_k8s_create_profile_"
                                          "for_definition.json.j2").render(
                                              rb_name=self.rb_name,
                                              rb_version=self.rb_version,
                                              profile_name=profile_name,
                                              release_name=release_name,
                                              namespace=namespace,
                                              kubernetes_version=kubernetes_version
                                          ),
            exception=ValueError
        )
        return self.get_profile_by_name(profile_name)

    def get_all_profiles(self) -> Iterator["Profile"]:
        """Get all profiles.

        Raises:
            ValueError: request response with HTTP error code

        Yields:
            Profile: Profile object

        """
        url: str = f"{self.url}/profile"

        for profile in self.send_message_json("GET",
                                              "Get profiles",
                                              url,
                                              exception=ValueError):
            yield Profile(
                profile["rb-name"],
                profile["rb-version"],
                profile["profile-name"],
                profile["namespace"],
                profile.get("kubernetes-version"),
                profile.get("labels"),
                profile.get("release-name")
            )

    def get_profile_by_name(self, profile_name: str) -> "Profile":
        """Get profile by it's name.

        Args:
            profile_name (str): profile name

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            Profile: Profile object

        """
        url: str = f"{self.url}/profile/{profile_name}"

        profile: dict = self.send_message_json(
            "GET",
            "Get profile",
            url,
            exception=ValueError
        )
        return Profile(
            profile["rb-name"],
            profile["rb-version"],
            profile["profile-name"],
            profile["namespace"],
            profile.get("kubernetes-version"),
            profile.get("labels"),
            profile.get("release-name")
        )

    def get_all_configuration_templates(self):
        """Get all configuration templates.

        Raises:
            ValueError: request response with HTTP error code

        Yields:
            ConfigurationTemplate: ConfigurationTemplate object

        """
        url: str = f"{self.url}/config-template"

        for template in self.send_message_json("GET",
                                               "Get configuration templates",
                                               url,
                                               exception=ValueError):
            yield ConfigurationTemplate(
                self.rb_name,
                self.rb_version,
                template["template-name"],
                template.get("description")
            )

    def create_configuration_template(self, template_name: str,
                                      description="") -> "ConfigurationTemplate":
        """Create configuration template.

        Args:
            template_name (str): Name of the template
            description (str): Description

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            ConfigurationTemplate: Created object

        """
        url: str = f"{self.url}/config-template"

        self.send_message(
            "POST",
            "Create configuration template",
            url,
            data=jinja_env().get_template("multicloud_k8s_create_configuration_"
                                          "template.json.j2").render(
                                              template_name=template_name,
                                              description=description
                                          ),
            exception=ValueError
        )

        return self.get_configuration_template_by_name(template_name)

    def get_configuration_template_by_name(self, template_name: str) -> "ConfigurationTemplate":
        """Get configuration template.

        Args:
            template_name (str): Name of the template

        Raises:
            ValueError: request response with HTTP error code

        Returns:
            ConfigurationTemplate: object

        """
        url: str = f"{self.url}/config-template/{template_name}"

        template: dict = self.send_message_json(
            "GET",
            "Get Configuration template",
            url,
            exception=ValueError
        )
        return ConfigurationTemplate(
            self.rb_name,
            self.rb_version,
            template["template-name"],
            template.get("description")
        )


class ProfileBase(DefinitionBase):
    """ProfileBase class."""

    def __init__(self, rb_name: str,
                 rb_version: str,
                 profile_name: str) -> None:
        """Profile-Base object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            profile_name (str): Name of profile
        """
        super().__init__(rb_name, rb_version)
        self.rb_name: str = rb_name
        self.rb_version: str = rb_version
        self.profile_name: str = profile_name

    @property
    def url(self) -> str:
        """URL address for Profile calls.

        Returns:
            str: URL to RB Profile

        """
        return f"{super().url}/profile/{self.profile_name}"


@dataclass
class Profile(ProfileBase):
    """Profile class."""

    def __init__(self, rb_name: str,
                 rb_version: str,
                 profile_name: str,
                 namespace: str,
                 kubernetes_version: str,
                 labels=None,
                 release_name=None) -> None:
        """Profile object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            profile_name (str): Name of profile
            release_name (str): Release name, if release_name is not provided,
            namespace (str): Namespace that service is created in
            kubernetes_version (str): Required Kubernetes version
            labels (dict): Labels
        """
        super().__init__(rb_name, rb_version, profile_name)
        if release_name is None:
            release_name = profile_name
        self.release_name: str = release_name
        self.namespace: str = namespace
        self.kubernetes_version: str = kubernetes_version
        self.labels: dict = labels
        if self.labels is None:
            self.labels = dict()


class ConfigurationTemplate(DefinitionBase):
    """ConfigurationTemplate class."""

    @property
    def url(self) -> str:
        """URL address for ConfigurationTemplate calls.

        Returns:
            str: URL to Configuration template in Multicloud-k8s API.

        """
        return f"{super().url}/config-template/{self.template_name}"

    def __init__(self, rb_name: str,
                 rb_version: str,
                 template_name: str,
                 description="") -> None:
        """Configuration-Template object initialization.

        Args:
            rb_name (str): Definition name
            rb_version (str): Definition version
            template_name (str): Configuration template name
            description (str): Namespace that service is created in
        """
        super().__init__(rb_name, rb_version)
        self.template_name: str = template_name
        self.description: str = description
