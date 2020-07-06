import pytest

from onapsdk.so.instantiation import Subnet


def test_dhcp_subnet():
    with pytest.raises(ValueError):
        Subnet(name="test",
               role="test",
               start_address="192.168.8.0",
               gateway_address="192.168.8.1",
               dhcp_enabled="sss"
        )
    with pytest.raises(ValueError):
        Subnet(name="test",
               role="test",
               start_address="192.168.8.0",
               gateway_address="192.168.8.1",
               dhcp_enabled="Y"
        )
    subnet = Subnet(name="test",
                    role="test",
                    start_address="192.168.8.0",
                    gateway_address="192.168.8.1",
                    dhcp_enabled="Y",
                    dhcp_start_address="10.8.1.0",
                    dhcp_end_address="10.8.1.1"
    )
    assert subnet.name == "test"
    assert subnet.role == "test"
    assert subnet.start_address == "192.168.8.0"
    assert subnet.gateway_address == "192.168.8.1"
    assert subnet.dhcp_enabled == "Y"
    assert subnet.dhcp_start_address == "10.8.1.0"
    assert subnet.dhcp_end_address == "10.8.1.1"
