
from collections import namedtuple
from unittest import mock

import pytest
from onapsdk.aai.cloud_infrastructure.cloud_region import CloudRegion, Tenant
from onapsdk.exceptions import ResourceNotFound


@mock.patch("onapsdk.aai.cloud_infrastructure.cloud_region.AaiElement.relationships", new_callable=mock.PropertyMock)
@mock.patch("onapsdk.aai.cloud_infrastructure.cloud_region.Complex.get_by_physical_location_id")
def test_cloud_region_complex_property(mock_complex_get, mock_relationships):
    cr = CloudRegion("test_cloud_owner", "test_cloud_region_id", False, False)

    mock_relationships.return_value = []
    assert cr.complex is None

    mock_relationships.return_value = [mock.MagicMock()]
    assert cr.complex is None

    relationship_mock = mock.MagicMock()
    relationship_mock.related_to = "complex"
    relationship_mock.get_relationship_data.return_value = None
    mock_relationships.return_value = [relationship_mock]
    assert cr.complex is None

    relationship_mock.get_relationship_data.return_value = "123"
    mock_complex_get.side_effect = ResourceNotFound
    assert cr.complex is None

    mock_complex_get.side_effect = None
    mock_complex_get.return_value = mock.MagicMock()
    assert cr.complex is not None

    mock_relationships.side_effect = ResourceNotFound
    assert cr.complex is None

@mock.patch("onapsdk.aai.cloud_infrastructure.cloud_region.CloudRegion.tenants", new_callable=mock.PropertyMock)
def test_cloud_region_get_tenant_by_name(mock_tenants):
    cr = CloudRegion("test_cloud_owner", "test_cloud_region_id", False, False)
    mock_tenants.return_value = iter([
        Tenant(cloud_region="test_cloud_region_id",tenant_id="test-tenant",tenant_name="test-tenant")
    ])
    assert cr.get_tenant_by_name(tenant_name="test-tenant") is not None
    with pytest.raises(ResourceNotFound) as exc:
        cr.get_tenant_by_name(tenant_name="test-tenant1")
    assert exc.type is ResourceNotFound
