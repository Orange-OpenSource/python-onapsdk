"""Pnf instance module."""

from typing import Optional, TYPE_CHECKING

from .instance import Instance

if TYPE_CHECKING:
    from .service import ServiceInstance  # pylint: disable=cyclic-import

class PnfInstance(Instance):  # pylint: disable=too-many-instance-attributes
    """Pnf instance class."""

    def __init__(self,  # pylint: disable=too-many-arguments, too-many-locals
                 service_instance: "ServiceInstance",
                 pnf_name: str,
                 in_maint: bool,
                 selflink: str = None,
                 pnf_id: str = None,
                 equip_type: str = None,
                 equip_vendor: str = None,
                 equip_model: str = None,
                 management_option: str = None,
                 orchestration_status: str = None,
                 ipaddress_v4_oam: str = None,
                 sw_version: str = None,
                 frame_id: str = None,
                 serial_number: str = None,
                 ipaddress_v4_loopback_0: str = None,
                 ipaddress_v6_loopback_0: str = None,
                 ipaddress_v4_aim: str = None,
                 ipaddress_v6_aim: str = None,
                 ipaddress_v6_oam: str = None,
                 inv_status: str = None,
                 resource_version: str = None,
                 prov_status: str = None,
                 nf_role: str = None,
                 admin_status: str = None,
                 operational_status: str = None,
                 model_customization_id: str = None,
                 model_invariant_id: str = None,
                 model_version_id: str = None,
                 pnf_ipv4_address: str = None,
                 pnf_ipv6_address: str = None) -> None:
        """Pnf instance object initialization.

        Args:
            service_instance (ServiceInstance):  Service instance object
            pnf_name (str): unique name of Physical Network Function
            in_maint (bool): Used to indicate whether or not this object is in maintenance mode
                (maintenance mode = True). This field (in conjunction with prov_status)
                is used to suppress alarms and vSCL on VNFs/VMs.
            selflink (str, optional): URL to endpoint where AAI can get more details.
                Defaults to None.
            pnf_id (str, optional): id of pnf. Defaults to None.
            equip_type (str, optional): Equipment type. Source of truth should define valid values.
                Defaults to None.
            equip_vendor (str, optional): Equipment vendor. Source of truth should define
                valid values. Defaults to None.
            equip_model (str, optional): Equipment model. Source of truth should define
                valid values. Defaults to None.
            management_option (str, optional): identifier of managed customer. Defaults to None.
            orchestration_status (str, optional): Orchestration status of this pnf.
                Defaults to None.
            ipaddress_v4_oam (str, optional): ipv4-oam-address with new naming
                convention for IP addresses. Defaults to None.
            sw_version (str, optional): sw-version is the version of SW for the hosted
                application on the PNF. Defaults to None.
            frame_id (str, optional): ID of the physical frame (relay rack) where pnf is installed.
                Defaults to None.
            serial_number (str, optional): Serial number of the device. Defaults to None.
            ipaddress_v4_loopback_0 (str, optional): IPV4 Loopback 0 address. Defaults to None.
            ipaddress_v6_loopback_0 (str, optional): IPV6 Loopback 0 address. Defaults to None.
            ipaddress_v4_aim (str, optional): IPV4 AIM address. Defaults to None.
            ipaddress_v6_aim (str, optional): IPV6 AIM address. Defaults to None.
            ipaddress_v6_oam (str, optional): IPV6 OAM address. Defaults to None.
            inv_status (str, optional): CANOPI's inventory status. Only set with values exactly
                as defined by CANOPI. Defaults to None.
            resource_version (str, optional): Used for optimistic concurrency.
                Must be empty on create, valid on update and delete. Defaults to None.
            prov_status (str, optional): Prov Status of this device (not under canopi control)
                Valid values [PREPROV/NVTPROV/PROV]. Defaults to None.
            nf_role (str, optional): Nf Role is the role performed by this instance in the network.
                Defaults to None.
            admin_status (str, optional): admin Status of this PNF. Defaults to None.
            operational_status (str, optional): Store the operational-status for this object.
                Defaults to None.
            model_customization_id (str, optional): Store the model-customization-id
                for this object. Defaults to None.
            model_invariant_id (str, optional): The ASDC model id for this resource model.
                Defaults to None.
            model_version_id (str, optional): The ASDC model version for this resource model.
                Defaults to None.
            pnf_ipv4_address (str, optional): This is the IP address (IPv4) for the PNF itself.
                This is the IPv4 address that the PNF iself can be accessed at. Defaults to None.
            pnf_ipv6_address (str, optional): This is the IP address (IPv6) for the PNF itself.
                This is the IPv6 address that the PNF iself can be accessed at. Defaults to None.
        """
        super().__init__(resource_version=resource_version,
                         model_invariant_id=model_invariant_id,
                         model_version_id=model_version_id)
        self.service_instance: "ServiceInstance" = service_instance
        self.pnf_name: str = pnf_name
        self.in_maint: bool = in_maint
        self.selflink: Optional[str] = selflink
        self.pnf_id: Optional[str] = pnf_id
        self.equip_type: Optional[str] = equip_type
        self.equip_vendor: Optional[str] = equip_vendor
        self.equip_model: Optional[str] = equip_model
        self.management_option: Optional[str] = management_option
        self.orchestration_status: Optional[str] = orchestration_status
        self.ipaddress_v4_oam: Optional[str] = ipaddress_v4_oam
        self.sw_version: Optional[str] = sw_version
        self.frame_id: Optional[str] = frame_id
        self.serial_number: Optional[str] = serial_number
        self.ipaddress_v4_loopback_0: Optional[str] = ipaddress_v4_loopback_0
        self.ipaddress_v6_loopback_0: Optional[str] = ipaddress_v6_loopback_0
        self.ipaddress_v4_aim: Optional[str] = ipaddress_v4_aim
        self.ipaddress_v6_aim: Optional[str] = ipaddress_v6_aim
        self.ipaddress_v6_oam: Optional[str] = ipaddress_v6_oam
        self.inv_status: Optional[str] = inv_status
        self.prov_status: Optional[str] = prov_status
        self.nf_role: Optional[str] = nf_role
        self.admin_status: Optional[str] = admin_status
        self.operational_status: Optional[str] = operational_status
        self.model_customization_id: Optional[str] = model_customization_id
        self.pnf_ipv4_address: Optional[str] = pnf_ipv4_address
        self.pnf_ipv6_address: Optional[str] = pnf_ipv6_address

    def __repr__(self) -> str:
        """Pnf instance object representation.

        Returns:
            str: Human readable pnf instance representation

        """
        return f"PnfInstance(pnf_name={self.pnf_name})"

    @property
    def url(self) -> str:
        """Network instance url.

        Returns:
            str: NetworkInstance url

        """
        return f"{self.base_url}{self.api_version}/network/pnfs/pnf/{self.pnf_name}"

    @classmethod
    def create_from_api_response(cls, api_response: dict,
                                 service_instance: "ServiceInstance") -> "PnfInstance":
        """Create pnf instance object using HTTP API response dictionary.

        Args:
            api_response (dict): A&AI API response dictionary
            service_instance (ServiceInstance): Service instance with which network is related

        Returns:
            PnfInstance: PnfInstance object

        """
        return cls(service_instance=service_instance,
                   pnf_name=api_response["pnf-name"],
                   in_maint=api_response["in-maint"],
                   selflink=api_response.get("selflink"),
                   pnf_id=api_response.get("pnf-id"),
                   equip_type=api_response.get("equip-type"),
                   equip_vendor=api_response.get("equip-vendor"),
                   equip_model=api_response.get("equip-model"),
                   management_option=api_response.get("management-option"),
                   orchestration_status=api_response.get("orchestration-status"),
                   ipaddress_v4_oam=api_response.get("ipaddress-v4-oam"),
                   sw_version=api_response.get("sw-version"),
                   frame_id=api_response.get("frame-id"),
                   serial_number=api_response.get("serial-number"),
                   ipaddress_v4_loopback_0=api_response.get("ipaddress-v4-loopback-0"),
                   ipaddress_v6_loopback_0=api_response.get("ipaddress-v6-loopback-0"),
                   ipaddress_v4_aim=api_response.get("ipaddress-v4-aim"),
                   ipaddress_v6_aim=api_response.get("ipaddress-v6-aim"),
                   ipaddress_v6_oam=api_response.get("ipaddress-v6-oam"),
                   inv_status=api_response.get("inv-status"),
                   resource_version=api_response.get("resource-version"),
                   prov_status=api_response.get("prov-status"),
                   nf_role=api_response.get("nf-role"),
                   admin_status=api_response.get("admin-status"),
                   operational_status=api_response.get("operational-status"),
                   model_customization_id=api_response.get("model-customization-id"),
                   model_invariant_id=api_response.get("model-invariant-id"),
                   model_version_id=api_response.get("model-version-id"),
                   pnf_ipv4_address=api_response.get("pnf-ipv4-address"),
                   pnf_ipv6_address=api_response.get("pnf-ipv6-address"))

    def delete(self) -> None:
        """Delete Pnf instance.

        PNF deletion it's just A&AI resource deletion. That's difference between another instances.
        You don't have to wait for that task finish, because it's not async task.

        """
        self._logger.debug("Delete %s pnf", self.pnf_name)
        self.send_message("DELETE",
                          f"Delete {self.pnf_name} PNF",
                          f"{self.url}?resource-version={self.resource_version}")
