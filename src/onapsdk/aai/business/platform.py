"""A&AI platform module."""

from typing import Any, Dict, Iterator

from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiElement


class Platform(AaiElement):
    """Platform class."""

    def __init__(self, name: str, resource_version: str) -> None:
        """Platform object initialization.

        Args:
            name (str): Platform name
            resource_version (str): resource version
        """
        super().__init__()
        self.name: str = name
        self.resource_version: str = resource_version

    def __repr__(self) -> str:
        """Platform object representation.

        Returns:
            str: Platform object representation

        """
        return f"Platform(name={self.name})"

    @property
    def url(self) -> str:
        """Platform's url.

        Returns:
            str: Resource's url

        """
        return (f"{self.base_url}{self.api_version}/business/platforms/"
                f"platform/{self.name}")

    @classmethod
    def get_all(cls) -> Iterator["Platform"]:
        """Get all platform.

        Yields:
            Platform: Platform object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/platforms"
        for platform in cls.send_message_json("GET",
                                              "Get A&AI platforms",
                                              url).get("platform", []):
            yield cls(
                platform.get("platform-name"),
                platform.get("resource-version")
            )

    @classmethod
    def create(cls, name: str) -> "Platform":
        """Create platform A&AI resource.

        Args:
            name (str): platform name

        Returns:
            Platform: Created Platform object

        """
        cls.send_message(
            "PUT",
            "Declare A&AI platform",
            (f"{cls.base_url}{cls.api_version}/business/platforms/"
             f"platform/{name}"),
            data=jinja_env().get_template("aai_platform_create.json.j2").render(
                platform_name=name
            )
        )
        return cls.get_by_name(name)

    @classmethod
    def get_by_name(cls, name: str) -> "Platform":
        """Get platform resource by it's name.

        Raises:
            ResourceNotFound: Platform requested by a name does not exist.

        Returns:
            Platform: Platform requested by a name.

        """
        url = (f"{cls.base_url}{cls.api_version}/business/platforms/"
               f"platform/{name}")
        response: Dict[str, Any] = \
            cls.send_message_json("GET",
                                  f"Get {name} platform",
                                  url)
        return cls(response["platform-name"], response["resource-version"])
