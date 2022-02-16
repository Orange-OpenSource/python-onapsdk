
from unittest import mock

import pytest

from onapsdk.aai.business import PnfInstance, pnf
from onapsdk.exceptions import ResourceNotFound
# from onapsdk.so.deletion import NetworkDeletionRequest


PNF_INSTANCE = {
    "pnf-name": "blablabla",
    "pnf-id": "546b282b-2ff7-41a4-9329-55c9a2888477",
    "equip-type": "pnf",
    "equip-vendor": "PNF",
    "equip-model": "Simulated Device",
    "orchestration-status": "Active",
    "ipaddress-v4-oam": "172.30.1.6",
    "sw-version": "2.3.5",
    "in-maint":False,
    "serial-number": "123",
    "ipaddress-v6-oam": "0:0:0:0:0:ffff:a0a:011",
    "resource-version": "1610142659380",
    "nf-role": "sdn controller",
    "model-customization-id": "137ce8e8-bee9-465f-b7e1-0c006f10b443",
    "model-invariant-id": "2ca7ea68-cf61-449c-a733-8122bcac1f9a",
    "model-version-id": "da467f24-a26d-4620-b185-e1afa1d365ac",
    "relationship-list": {
        "relationship":[
            {
                "related-to":"service-instance",
                "relationship-label":"org.onap.relationships.inventory.ComposedOf",
                "related-link":"/aai/v21/business/customers/customer/test/service-subscriptions/service-subscription/test/service-instances/service-instance/4c3ab996-afdb-4956-9c4d-038b4eed3db1",
                "relationship-data":[
                    {
                        "relationship-key":"customer.global-customer-id",
                        "relationship-value":"test"
                    },
                    {
                        "relationship-key":"service-subscription.service-type",
                        "relationship-value":"test"
                    },
                    {
                        "relationship-key":"service-instance.service-instance-id",
                        "relationship-value":"4c3ab996-afdb-4956-9c4d-038b4eed3db1"
                    }
                ],
                "related-to-property":[
                    {
                        "property-key":"service-instance.service-instance-name",
                        "property-value":"blablabla"
                    }
                ]
            }
        ]
    }
}


def test_create_pnf_instance_from_api_response():
    service_instance = mock.MagicMock()
    pnf_instance = PnfInstance.create_from_api_response(
        PNF_INSTANCE,
        service_instance
    )
    assert pnf_instance.pnf_name == "blablabla"
    assert pnf_instance.pnf_id == "546b282b-2ff7-41a4-9329-55c9a2888477"
    assert pnf_instance.equip_type == "pnf"
    assert pnf_instance.equip_vendor == "PNF"
    assert pnf_instance.equip_model == "Simulated Device"
    assert pnf_instance.orchestration_status == "Active"
    assert pnf_instance.ipaddress_v4_oam == "172.30.1.6"
    assert pnf_instance.sw_version == "2.3.5"
    assert pnf_instance.in_maint == False
    assert pnf_instance.serial_number == "123"
    assert pnf_instance.ipaddress_v6_oam == "0:0:0:0:0:ffff:a0a:011"
    assert pnf_instance.resource_version == "1610142659380"
    assert pnf_instance.nf_role == "sdn controller"
    assert pnf_instance.model_customization_id == "137ce8e8-bee9-465f-b7e1-0c006f10b443"
    assert pnf_instance.model_invariant_id == "2ca7ea68-cf61-449c-a733-8122bcac1f9a"
    assert pnf_instance.model_version_id == "da467f24-a26d-4620-b185-e1afa1d365ac"

    assert pnf_instance.url.endswith(pnf_instance.pnf_name)


@mock.patch.object(PnfInstance, "send_message")
def test_delete_pnf_instance(mock_send_message):
    pnf = PnfInstance(mock.MagicMock, "test_pnf", False)
    pnf.delete()
    method, _, address = mock_send_message.call_args[0]
    assert method == "DELETE"
    assert address == f"{pnf.url}?resource-version={pnf.resource_version}"


def test_pnf_instance_pnf():
    service_instance = mock.MagicMock()
    pnf_instance = PnfInstance.create_from_api_response(
        PNF_INSTANCE,
        service_instance
    )

    assert pnf_instance._pnf is None
    service_instance.sdc_service.pnfs = []
    with pytest.raises(ResourceNotFound) as exc:
        pnf_instance.pnf
    assert exc.type == ResourceNotFound
    assert pnf_instance._pnf is None

    pnf = mock.MagicMock()
    pnf.model_version_id = "da467f24-a26d-4620-b185-e1afa1d365ac"
    service_instance.sdc_service.pnfs = [pnf]
    assert pnf == pnf_instance.pnf
    assert pnf_instance._pnf is not None
    assert pnf_instance.pnf == pnf_instance._pnf
