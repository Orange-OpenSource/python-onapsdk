"""A&AI project module."""

from typing import Any, Dict, Iterator

from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiElement


class Project(AaiElement):
    """Project class."""

    def __init__(self, name: str, resource_version: str) -> None:
        """Project object initialization.

        Args:
            name (str): Project name
            resource_version (str): resource version
        """
        super().__init__()
        self.name: str = name
        self.resource_version: str = resource_version

    @classmethod
    def get_all(cls) -> Iterator["Project"]:
        """Get all project.

        Yields:
            Project: Project object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/projects"
        for project in cls.send_message_json("GET",
                                             "Get A&AI projects",
                                             url).get("project", []):
            yield cls(
                project.get("project-name"),
                project.get("resource-version")
            )

    def __repr__(self) -> str:
        """Project object representation.

        Returns:
            str: Project object representation

        """
        return f"Project(name={self.name})"

    @property
    def url(self) -> str:
        """Project's url.

        Returns:
            str: Resource's url

        """
        return (f"{self.base_url}{self.api_version}/business/projects/"
                f"project/{self.name}")

    @classmethod
    def create(cls, name: str) -> "Project":
        """Create project A&AI resource.

        Args:
            name (str): project name

        Returns:
            Project: Created Project object

        """
        cls.send_message(
            "PUT",
            "Declare A&AI project",
            (f"{cls.base_url}{cls.api_version}/business/projects/"
             f"project/{name}"),
            data=jinja_env().get_template("aai_project_create.json.j2").render(
                project_name=name
            )
        )
        return cls.get_by_name(name)

    @classmethod
    def get_by_name(cls, name: str) -> "Project":
        """Get project resource by it's name.

        Raises:
            ResourceNotFound: Project requested by a name does not exist.

        Returns:
            Project: Project requested by a name.

        """
        url = (f"{cls.base_url}{cls.api_version}/business/projects/"
               f"project/{name}")
        response: Dict[str, Any] = \
            cls.send_message_json("GET",
                                  f"Get {name} project",
                                  url)
        return cls(response["project-name"], response["resource-version"])
