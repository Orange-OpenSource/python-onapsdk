"""A&AI sp-partner module."""

from typing import Iterator, Optional

from onapsdk.utils.jinja import jinja_env

from ..aai_element import AaiElement


class SpPartner(AaiElement):  # pylint: disable=too-many-instance-attributes
    """Sp partner class."""

    def __init__(self, sp_partner_id: str, resource_version: str, url: str = None,  # pylint: disable=too-many-arguments, too-many-locals
                 callsource: str = None, operational_status: str = None,
                 model_customization_id: str = None, model_invariant_id: str = None,
                 model_version_id: str = None) -> None:
        """Sp partner object initialization.

        Args:
            sp_partner_id (str): Uniquely identifies this sp-partner by id
            resource_version (str): resource version
            url (str, optional): Store the URL of this sp-partner. Defaults to None
            callsource (str, optional): Store the callsource of this sp-partner. Defaults to None
            operational_status (str, optional): Store the operational-status of this sp-partner.
                Defaults to None
            model_customization_id (str, optional): Store the model-customization-id
                of this sp-partner. Defaults to None
            model_invariant_id (str, optional): The ASDC model id for this sp-partner model.
                Defaults to None
            model_version_id (str, optional): The ASDC model version for this sp-partner model.
                Defaults to None

        """
        super().__init__()
        self.sp_partner_id: str = sp_partner_id
        self.resource_version: str = resource_version
        self.sp_partner_url: Optional[str] = url
        self.callsource: Optional[str] = callsource
        self.operational_status: Optional[str] = operational_status
        self.model_customization_id: Optional[str] = model_customization_id
        self.model_invariant_id: Optional[str] = model_invariant_id
        self.model_version_id: Optional[str] = model_version_id

    def __repr__(self) -> str:
        """Sp partner object representation.

        Returns:
            str: SpPartner object representation

        """
        return f"SpPartner(sp_partner_id={self.sp_partner_id})"

    @property
    def url(self) -> str:
        """Sp partner's url.

        Returns:
            str: Resource's url

        """
        return (f"{self.base_url}{self.api_version}/business/sp-partners/"
                f"sp-partner/{self.sp_partner_id}")

    @classmethod
    def get_all(cls) -> Iterator["SpPartner"]:
        """Get all sp partners.

        Yields:
            SpPartner: SpPartner object

        """
        url: str = f"{cls.base_url}{cls.api_version}/business/sp-partners"
        for sp_partner in cls.send_message_json("GET",
                                                "Get A&AI sp-partners",
                                                url).get("sp-partner", []):
            yield cls(
                sp_partner["sp-partner-id"],
                sp_partner["resource-version"],
                sp_partner.get("url"),
                sp_partner.get("callsource"),
                sp_partner.get("operational-status"),
                sp_partner.get("model-customization-id"),
                sp_partner.get("model-invariant-id"),
                sp_partner.get("model-version-id"),
            )

    @classmethod
    def create(cls, sp_partner_id: str, url: str = "", callsource: str = "",  # pylint: disable=too-many-arguments
               operational_status: str = "", model_customization_id: str = "",
               model_invariant_id: str = "", model_version_id: str = "") -> "SpPartner":
        """Create sp partner A&AI resource.

        Args:
            sp_partner_id (str): sp partner unique ID
            url (str, optional): Store the URL of this sp-partner. Defaults to None
            callsource (str, optional): Store the callsource of this sp-partner. Defaults to None
            operational_status (str, optional): Store the operational-status of this sp-partner.
                Defaults to None
            model_customization_id (str, optional): Store the model-customization-id
                of this sp-partner. Defaults to None
            model_invariant_id (str, optional): The ASDC model id for this sp-partner model.
                Defaults to None
            model_version_id (str, optional): The ASDC model version for this sp-partner model.
                Defaults to None

        Returns:
            SpPartner: Created SpPartner object

        """
        cls.send_message(
            "PUT",
            "Declare A&AI sp partner",
            (f"{cls.base_url}{cls.api_version}/business/sp-partners/"
             f"sp-partner/{sp_partner_id}"),
            data=jinja_env().get_template("aai_sp_partner_create.json.j2").render(
                sp_partner_id=sp_partner_id,
                url=url,
                callsource=callsource,
                operational_status=operational_status,
                model_customization_id=model_customization_id,
                model_invariant_id=model_invariant_id,
                model_version_id=model_version_id
            )
        )
        return cls.get_by_sp_partner_id(sp_partner_id)

    @classmethod
    def get_by_sp_partner_id(cls, sp_partner_id: str) -> "SpPartner":
        """Get sp partner by it's ID.

        Args:
            sp_partner_id (str): sp partner object id

        Returns:
            SpPartner: SpPartner object

        """
        response: dict = cls.send_message_json(
            "GET",
            "Get A&AI sp partner",
            (f"{cls.base_url}{cls.api_version}/business/sp-partners/"
             f"sp-partner/{sp_partner_id}")
        )
        return cls(
            response["sp-partner-id"],
            response["resource-version"],
            response.get("url"),
            response.get("callsource"),
            response.get("operational-status"),
            response.get("model-customization-id"),
            response.get("model-invariant-id"),
            response.get("model-version-id")
        )
