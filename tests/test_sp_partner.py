from unittest import mock

import pytest

from onapsdk.aai.business import SpPartner
from onapsdk.exceptions import ResourceNotFound


SP_PARTNERS = {
    "sp-partner":[
        {
            "sp-partner-id":"ff6c945f-89ab-4f14-bafd-0cdd6eac791a",
            "url":"http://127.0.0.1",
            "resource-version":"1588244348931",
        },
        {
            "sp-partner-id":"OE-generic",
            "callsource":"test-callsource",
            "resource-version":"1587388597761"
        },
        {
            "sp-partner-id":"b3dcdbb0-edae-4384-b91e-2f114472520c",
            "url":"http://127.0.0.1",
            "callsource":"test-callsource",
            "operational-status":"test-operational-status",
            "model-customization-id":"test-model-customization-id",
            "model-invariant-id":"test-model-invariant-id",
            "model-version-id":"test-model-version-id",
            "resource-version":"1588145971158"
        }
    ]
}


SP_PARTNER = {
    "sp-partner-id":"blablabla",
    "url":"http://127.0.0.1",
    "callsource":"test-callsource",
    "resource-version":"1587388597761"
}


@mock.patch.object(SpPartner, "send_message_json")
def test_sp_partner_get_all(mock_send):
    mock_send.return_value = SP_PARTNERS
    owning_entities = list(SpPartner.get_all())
    assert len(owning_entities) == 3
    sp_partner = owning_entities[0]
    assert sp_partner.sp_partner_id == "ff6c945f-89ab-4f14-bafd-0cdd6eac791a"
    assert sp_partner.sp_partner_url == "http://127.0.0.1"
    assert sp_partner.url == (f"{sp_partner.base_url}{sp_partner.api_version}/"
                                 "business/sp-partners/sp-partner/"
                                 f"{sp_partner.sp_partner_id}")


@mock.patch.object(SpPartner, "send_message_json")
def test_sp_partner_get_by_sp_partner_id(mock_send):
    mock_send.return_value = SP_PARTNER
    sp_partner = SpPartner.get_by_sp_partner_id("blablabla")
    assert sp_partner.sp_partner_id == "blablabla"


@mock.patch.object(SpPartner, "send_message")
@mock.patch.object(SpPartner, "get_by_sp_partner_id")
def test_sp_partner_create(_, mock_send):

    SpPartner.create(
        sp_partner_id="123"
    )
    mock_send.assert_called_once_with("PUT",
                                      "Declare A&AI sp partner",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v27/business/sp-partners/sp-partner/123",
                                      data='{\n    "sp-partner-id": "123"\n    \n    \n    \n    \n    \n    \n}')
