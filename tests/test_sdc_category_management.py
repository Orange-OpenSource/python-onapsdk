#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcElement module."""
from unittest import mock

import pytest

from onapsdk.sdc.category_management import ResourceCategory, ServiceCategory


CATEGORIES = {
    "categories": {
        'resourceCategories': [
            {
                'name': 'Network L4+', 
                'normalizedName': 'network l4+', 
                'uniqueId': 'resourceNewCategory.network l4+', 
                'icons': None, 
                'subcategories': [
                    {
                        'name': 'Common Network Resources', 
                        'normalizedName': 'common network resources', 
                        'uniqueId': 'resourceNewCategory.network l4+.common network resources', 
                        'icons': ['network'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }
                ], 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Network L2-3', 
                'normalizedName': 'network l2-3', 
                'uniqueId': 'resourceNewCategory.network l2-3', 
                'icons': None, 
                'subcategories': [
                    {
                        'name': 'Router', 
                        'normalizedName': 'router', 
                        'uniqueId': 'resourceNewCategory.network l2-3.router', 
                        'icons': ['router', 'vRouter'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }, 
                    {
                        'name': 'LAN Connectors', 
                        'normalizedName': 'lan connectors', 
                        'uniqueId': 'resourceNewCategory.network l2-3.lan connectors', 
                        'icons': ['network', 'connector', 'port'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }, 
                    {
                        'name': 'Infrastructure', 
                        'normalizedName': 'infrastructure', 
                        'uniqueId': 'resourceNewCategory.network l2-3.infrastructure', 
                        'icons': ['ucpe'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    },
                    {
                        'name': 'Gateway', 
                        'normalizedName': 'gateway', 
                        'uniqueId': 'resourceNewCategory.network l2-3.gateway', 
                        'icons': ['gateway'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }, 
                    {
                        'name': 'WAN Connectors', 
                        'normalizedName': 'wan connectors', 
                        'uniqueId': 'resourceNewCategory.network l2-3.wan connectors', 
                        'icons': ['network', 'connector', 'port'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }
                ],
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Network Connectivity', 
                'normalizedName': 'network connectivity', 
                'uniqueId': 'resourceNewCategory.network connectivity', 
                'icons': None, 
                'subcategories': [
                    {
                        'name': 'Connection Points', 
                        'normalizedName': 'connection points', 
                        'uniqueId': 'resourceNewCategory.network connectivity.connection points', 
                        'icons': ['cp'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }, 
                    {
                        'name': 'Virtual Links', 
                        'normalizedName': 'virtual links', 
                        'uniqueId': 'resourceNewCategory.network connectivity.virtual links', 
                        'icons': ['vl'], 
                        'groupings': None, 
                        'version': None, 
                        'ownerId': None, 
                        'empty': False, 
                        'type': None
                    }
                ], 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Configuration', 
                'normalizedName': 'configuration', 
                'uniqueId': 'resourceNewCategory.configuration', 
                'icons': None, 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            },     
        ], 
        'serviceCategories': [
            {
                'name': 'Partner Domain Service', 
                'normalizedName': 'partner domain service', 
                'uniqueId': 'serviceNewCategory.partner domain service', 
                'icons': ['partner_domain_service'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Mobility', 
                'normalizedName': 'mobility', 
                'uniqueId': 'serviceNewCategory.mobility', 
                'icons': ['mobility'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'VoIP Call Control', 
                'normalizedName': 'voip call control', 
                'uniqueId': 'serviceNewCategory.voip call control', 
                'icons': ['call_controll'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'E2E Service', 
                'normalizedName': 'e2e service', 
                'uniqueId': 'serviceNewCategory.e2e service', 
                'icons': ['network_l_1-3'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Network L4+', 
                'normalizedName': 'network l4+', 
                'uniqueId': 'serviceNewCategory.network l4+', 
                'icons': ['network_l_4'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Network L1-3', 
                'normalizedName': 'network l1-3', 
                'uniqueId': 'serviceNewCategory.network l1-3', 
                'icons': ['network_l_1-3'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
            {
                'name': 'Network Service', 
                'normalizedName': 'network service', 
                'uniqueId': 'serviceNewCategory.network service', 
                'icons': ['network_l_1-3'], 
                'subcategories': None, 
                'version': None, 
                'ownerId': None, 
                'empty': False, 
                'type': None
            }, 
        ], 
        'productCategories': []
    }
}


@mock.patch.object(ResourceCategory, "send_message_json")
def test_resource_category_exists(mock_send_message_json):

    rc = ResourceCategory(name="test_name")
    mock_send_message_json.return_value = {}
    assert not rc.exists()
    mock_send_message_json.return_value = CATEGORIES
    assert not rc.exists()
    rc = ResourceCategory(name="Network Connectivity")
    assert rc.exists()

@mock.patch.object(ResourceCategory, "send_message_json")
def test_resource_category_get(mock_send_message_json):
    
    mock_send_message_json.return_value = {}
    with pytest.raises(ValueError):
        ResourceCategory.get(name="Network Connectivity")
    mock_send_message_json.return_value = CATEGORIES
    rc = ResourceCategory.get(name="Network Connectivity")
    assert rc.name == "Network Connectivity"
    assert rc.normalized_name == "network connectivity"
    assert rc.unique_id == "resourceNewCategory.network connectivity"
    assert not rc.icons
    assert not rc.version
    assert not rc.owner_id
    assert not rc.empty
    assert not rc.type

@mock.patch.object(ResourceCategory, "send_message_json")
def test_resource_category_create(mock_send_message_json):

    mock_send_message_json.return_value = CATEGORIES
    rc = ResourceCategory.create(name="Network Connectivity")
    assert rc.name == "Network Connectivity"
    assert rc.normalized_name == "network connectivity"
    assert rc.unique_id == "resourceNewCategory.network connectivity"
    assert not rc.icons
    assert not rc.version
    assert not rc.owner_id
    assert not rc.empty
    assert not rc.type
    ResourceCategory.create(name="New category")

@mock.patch.object(ServiceCategory, "send_message_json")
def test_service_category_exists(mock_send_message_json):

    sc = ServiceCategory(name="test_name")
    mock_send_message_json.return_value = {}
    assert not sc.exists()
    mock_send_message_json.return_value = CATEGORIES
    assert not sc.exists()
    sc = ServiceCategory(name="Partner Domain Service")
    assert sc.exists()

@mock.patch.object(ServiceCategory, "send_message_json")
def test_service_category_get(mock_send_message_json):
    
    mock_send_message_json.return_value = {}
    with pytest.raises(ValueError):
        ServiceCategory.get(name="Partner Domain Service")
    mock_send_message_json.return_value = CATEGORIES
    sc = ServiceCategory.get(name="Partner Domain Service")
    assert sc.name == "Partner Domain Service"
    assert sc.normalized_name == "partner domain service"
    assert sc.unique_id == "serviceNewCategory.partner domain service"
    assert not sc.version
    assert not sc.owner_id
    assert not sc.empty
    assert not sc.type

@mock.patch.object(ServiceCategory, "send_message_json")
def test_service_category_create(mock_send_message_json):

    mock_send_message_json.return_value = CATEGORIES
    sc = ServiceCategory.create(name="Partner Domain Service")
    assert sc.name == "Partner Domain Service"
    assert sc.normalized_name == "partner domain service"
    assert sc.unique_id == "serviceNewCategory.partner domain service"
    assert not sc.version
    assert not sc.owner_id
    assert not sc.empty
    assert not sc.type
    ServiceCategory.create(name="New category")