from unittest.mock import patch

from onapsdk.aai.cloud_infrastructure.geo_region import GeoRegion

GEO_REGIONS = {
    "geo-region": [
        {
            "geo-region-id": "123"
        },
        {
            "geo-region-id": "321"
        }
    ]
}

GEO_REGION = {
    "geo-region-id": "123",
    "resource-version": "123"
}

@patch("onapsdk.aai.cloud_infrastructure.geo_region.GeoRegion.send_message_json")
def test_geo_region_get_all(mock_send_message_json):
    mock_send_message_json.return_value = {}
    assert len(list(GeoRegion.get_all())) == 0

    mock_send_message_json.return_value = GEO_REGIONS
    assert len(list(GeoRegion.get_all())) == 2

@patch("onapsdk.aai.cloud_infrastructure.geo_region.GeoRegion.send_message_json")
def test_geo_region_get_by_region_id(mock_send_message_json):
    mock_send_message_json.return_value = GEO_REGION
    geo_region = GeoRegion.get_by_geo_region_id("123")
    assert geo_region.geo_region_id == "123"
    assert geo_region.resource_version == "123"

@patch("onapsdk.aai.cloud_infrastructure.geo_region.GeoRegion.send_message")
@patch("onapsdk.aai.cloud_infrastructure.geo_region.GeoRegion.get_by_geo_region_id")
def test_geo_region_create(mock_get_geo_region_by_id, mock_send_message):
    GeoRegion.create("123")
    mock_send_message.assert_called_once()
    assert mock_get_geo_region_by_id.called_once_with("123")

def test_geo_region_url():
    geo_region = GeoRegion("test-geo-region")
    assert geo_region.url == "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v26/cloud-infrastructure/geo-regions/geo-region/test-geo-region"
