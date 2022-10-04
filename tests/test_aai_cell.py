from unittest.mock import MagicMock, patch

from onapsdk.aai.network import Cell


CELL = {
    "cell-id":"1234",
    "cell-name": "test",
    "radio-access-technology": "5g",
    "resource-version": "123"
}

CELLS = {
    "cell":[
        {
            "cell-id":"1234",
            "cell-name": "test",
            "radio-access-technology": "5g",
            "resource-version": "123"
        },
        {
            "cell-id": "4321",
            "cell-name": "test",
            "radio-access-technology": "5g",
            "resource-version": "123"
        }
    ]
}


@patch("onapsdk.aai.network.cell.Cell.send_message_json")
def test_cell_get_all(mock_cell_send_message_json):
    mock_cell_send_message_json.return_value = {}
    assert len(list(Cell.get_all())) == 0
    mock_cell_send_message_json.return_value = CELLS
    assert len(list(Cell.get_all())) == 2

@patch("onapsdk.aai.network.cell.Cell.send_message_json")
def test_cell_get_by_cell_id(mock_send_message_json):
    mock_send_message_json.return_value = CELL
    cell = Cell.get_by_cell_id("1234")
    assert cell.cell_id == "1234"
    assert cell.cell_name == "test"
    assert cell.radio_access_technology == "5g"
    assert cell.resource_version == "123"

@patch("onapsdk.aai.network.cell.Cell.send_message")
@patch("onapsdk.aai.network.cell.Cell.get_by_cell_id")
def test_geo_region_create(mock_get_cell_by_cell_id, mock_send_message):
    Cell.create("123", "123", "5g")
    mock_send_message.assert_called_once()
    assert mock_get_cell_by_cell_id.called_once_with("123")

@patch("onapsdk.aai.network.cell.Cell.add_relationship")
def test_cell_link_to_complex(mock_add_relationship):
    cmplx = MagicMock(physical_location_id="test-complex-physical-location-id",
                      url="test-complex-url")
    cell = Cell("123", "123", "5g")
    cell.link_to_complex(cmplx)
    mock_add_relationship.assert_called_once()
    relationship = mock_add_relationship.call_args.args[0]
    assert relationship.related_to == "complex"
    assert relationship.related_link == "test-complex-url"
    assert relationship.relationship_label == "org.onap.relationships.inventory.LocatedIn"
    assert relationship.relationship_data == [{
        "relationship-key": "complex.physical-location-id",
        "relationship-value": "test-complex-physical-location-id",
    }]

@patch("onapsdk.aai.network.cell.Cell.add_relationship")
def test_cell_link_to_geo_region(mock_add_relationship):
    geo_region = MagicMock(geo_region_id="test-geo-region-id",
                           url="test-geo-region-url")
    cell = Cell("123", "123", "5g")
    cell.link_to_geo_region(geo_region)
    mock_add_relationship.assert_called_once()
    relationship = mock_add_relationship.call_args.args[0]
    assert relationship.related_to == "geo-region"
    assert relationship.related_link == "test-geo-region-url"
    assert relationship.relationship_label == "org.onap.relationships.inventory.MemberOf"
    assert relationship.relationship_data == [{
        "relationship-key": "geo-region.geo-region-id",
        "relationship-value": "test-geo-region-id",
    }]
