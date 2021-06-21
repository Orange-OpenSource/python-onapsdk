"""A&AI line of business module."""

from typing import Any, Dict, Iterator

from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiElement


class LineOfBusiness(AaiElement):
    """Line of business class."""

    def __init__(self, name: str, resource_version: str) -> None:
        """Line of business object initialization.

        Args:
            name (str): Line of business name
            resource_version (str): resource version
        """
        super().__init__()
        self.name: str = name
        self.resource_version: str = resource_version

    @property
    def url(self) -> str:
        """Line of business's url.

        Returns:
            str: Resource's url

        """
        return (f"{self.base_url}{self.api_version}/business/lines-of-business/"
                f"line-of-business/{self.name}")

    def __repr__(self) -> str:
        """Line of business object representation.

        Returns:
            str: Line of business object representation

        """
        return f"LineOfBusiness(name={self.name})"

    @classmethod
    def get_all(cls) -> Iterator["LineOfBusiness"]:
        """Get all line of business.

        Yields:
            LineOfBusiness: LineOfBusiness object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/lines-of-business"
        for line_of_business in cls.send_message_json("GET",
                                                      "Get A&AI lines of business",
                                                      url).get("line-of-business", []):
            yield cls(
                line_of_business.get("line-of-business-name"),
                line_of_business.get("resource-version")
            )

    @classmethod
    def create(cls, name: str) -> "LineOfBusiness":
        """Create line of business A&AI resource.

        Args:
            name (str): line of business name

        Returns:
            LineOfBusiness: Created LineOfBusiness object

        """
        cls.send_message(
            "PUT",
            "Declare A&AI line of business",
            (f"{cls.base_url}{cls.api_version}/business/lines-of-business/"
             f"line-of-business/{name}"),
            data=jinja_env().get_template("aai_line_of_business_create.json.j2").render(
                line_of_business_name=name
            )
        )
        return cls.get_by_name(name)

    @classmethod
    def get_by_name(cls, name: str) -> "LineOfBusiness":
        """Get line of business resource by it's name.

        Raises:
            ResourceNotFound: Line of business requested by a name does not exist.

        Returns:
            LineOfBusiness: Line of business requested by a name.

        """
        url = (f"{cls.base_url}{cls.api_version}/business/lines-of-business/"
               f"line-of-business/{name}")
        response: Dict[str, Any] = \
            cls.send_message_json("GET",
                                  f"Get {name} line of business",
                                  url)
        return cls(response["line-of-business-name"], response["resource-version"])
