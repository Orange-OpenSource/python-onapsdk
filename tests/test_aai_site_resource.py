from unittest.mock import MagicMock, patch

from onapsdk.aai.network.site_resource import SiteResource

SITE_RESOURCE = {
    "site-resource-id":"123",
    "resource-version":"213"
}

SITE_RESOURCES = {
    "site-resource":[
        SITE_RESOURCE,
        {
            "site-resource-id":"321",
            "resource-version":"312"
        }
    ]
}

@patch("onapsdk.aai.network.site_resource.SiteResource.send_message_json")
def test_site_resource_get_all(mock_send_message_json):
    assert len(list(SiteResource.get_all())) == 0
    mock_send_message_json.return_value = SITE_RESOURCES
    site_resources = list(SiteResource.get_all())
    assert len(site_resources) == 2
    sr1, sr2 = site_resources
    assert sr1.site_resource_id == "123"
    assert sr1.resource_version == "213"
    assert sr2.site_resource_id == "321"
    assert sr2.resource_version == "312"

@patch("onapsdk.aai.network.site_resource.SiteResource.send_message_json")
def test_site_resource_get_by_id(mock_send_message_json):
    mock_send_message_json.return_value = SITE_RESOURCE
    sr = SiteResource.get_by_site_resource_id("123")
    assert sr.site_resource_id == "123"
    assert sr.resource_version == "213"

@patch("onapsdk.aai.network.site_resource.SiteResource.send_message")
@patch("onapsdk.aai.network.site_resource.SiteResource.get_by_site_resource_id")
def test_site_resource_create(mock_get_by_site_resource_id, mock_send_message):
    SiteResource.create("123")
    mock_send_message.assert_called_once()
    assert mock_get_by_site_resource_id.called_once_with("123")

@patch("onapsdk.aai.network.site_resource.SiteResource.add_relationship")
def test_site_resource_link_to_complex(mock_add_relationship):
    cmplx = MagicMock(physical_location_id="test-complex-physical-location-id",
                      url="test-complex-url")
    site_resource = SiteResource("test-site-resource")
    site_resource.link_to_complex(cmplx)
    mock_add_relationship.assert_called_once()
    relationship = mock_add_relationship.call_args.args[0]
    assert relationship.related_to == "complex"
    assert relationship.related_link == "test-complex-url"
    assert relationship.relationship_label == "org.onap.relationships.inventory.Uses"
    assert relationship.relationship_data == [{
        "relationship-key": "complex.physical-location-id",
        "relationship-value": "test-complex-physical-location-id",
    }]


@patch("onapsdk.aai.network.site_resource.SiteResource.add_relationship")
def test_site_resource_link_to_cell(mock_add_relationship):
    cell = MagicMock(cell_id="test-cell-id",
                      url="test-cell-url")
    site_resource = SiteResource("test-site-resource")
    site_resource.link_to_cell(cell)
    mock_add_relationship.assert_called_once()
    relationship = mock_add_relationship.call_args.args[0]
    assert relationship.related_to == "cell"
    assert relationship.related_link == "test-cell-url"
    assert relationship.relationship_label == "org.onap.relationships.inventory.ControlledBy"
    assert relationship.relationship_data == [{
        "relationship-key": "cell.cell-id",
        "relationship-value": "test-cell-id",
    }]
