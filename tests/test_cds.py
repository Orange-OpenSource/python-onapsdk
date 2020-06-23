# SPDX-License-Identifier: Apache-2.0
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch, PropertyMock

from pytest import raises

from onapsdk.cds.blueprint import Blueprint, CbaMetadata, Mapping, MappingSet, Workflow
from onapsdk.cds.cds_element import CdsElement
from onapsdk.cds.data_dictionary import DataDictionary, DataDictionarySet


DD_1 = {
    "name": "vf-module-name",
    "tags": "vf-module-name",
    "data_type": "string",
    "description": "vf-module-name",
    "entry_schema": "string",
    "updatedBy": "Singal, Kapil <ks220y@att.com>",
    "definition": {
        "tags": "vf-module-name",
        "name": "vf-module-name",
        "property": {
            "description": "vf-module-name",
            "type": "string"
        },
        "updated-by": "Singal, Kapil <ks220y@att.com>",
        "sources": {
            "input": {
                "type": "source-input"
            },
            "default": {
                "type": "source-default",
                "properties": {}
            }
        }
    }
}


vLB_CBA_Python_meta_bytes = b'TOSCA-Meta-File-Version: 1.0.0\nCSAR-Version: 1.0\nCreated-By: PLATANIA, MARCO <platania@research.att.com>\nEntry-Definitions: Definitions/vLB_CDS.json\nTemplate-Tags: vDNS-CDS-test1\nContent-Type: application/vnd.oasis.bpmn\nTemplate-Name: vDNS-CDS-test1\nTemplate-Version: 1.0'

vLB_CBA_Python_base_template_mapping_bytes = b'[\n  {\n    "name": "service-instance-id",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "service-instance-id",\n    "dictionary-source": "input",\n    "dependencies": [],\n    "version": 0\n  },\n  {\n    "name": "vnf-id",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vnf-id",\n    "dictionary-source": "input",\n    "dependencies": [],\n    "version": 0\n  },\n  {\n    "name": "vdns_vf_module_id",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vdns_vf_module_id",\n    "dictionary-source": "sdnc",\n    "dependencies": [\n\t  "service-instance-id",\n      "vnf-id"\n    ],\n    "version": 0\n  },\n  {\n    "name": "vdns_int_private_ip_0",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vdns_int_private_ip_0",\n    "dictionary-source": "sdnc",\n    "dependencies": [\n      "service-instance-id",\n      "vnf-id",\n      "vdns_vf_module_id"\n    ],\n    "version": 0\n  },\n  {\n    "name": "vdns_onap_private_ip_0",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vdns_onap_private_ip_0",\n    "dictionary-source": "sdnc",\n    "dependencies": [\n      "service-instance-id",\n      "vnf-id",\n      "vdns_vf_module_id"\n    ],\n    "version": 0\n  }\n]'


@patch.object(Blueprint, "send_message")
def test_blueprint_enrichment(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.enrich()
    send_message_mock.assert_called_once()
    send_message_mock.reset_mock()
    send_message_mock.return_value = None
    with raises(AttributeError):
        blueprint.enrich()


@patch.object(Blueprint, "send_message")
def test_blueprint_publish(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.publish()
    send_message_mock.assert_called_once()


@patch.object(Blueprint, "send_message")
def test_blueprint_deploy(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.deploy()
    send_message_mock.assert_called_once()


def test_blueprint_save():
    blueprint = Blueprint(b"test cba - it will never work")
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test.zip")
        blueprint.save(path)
        with open(path, "rb") as f:
            assert f.read() == b"test cba - it will never work"


def test_blueprint_read_cba_metadata():
    b = Blueprint(b"test cba - it will never work")
    with raises(ValueError):
        b.get_cba_metadata(b"Invalid")
        b.get_cba_metadata(b"123: 456")

    cba_metadata = b.get_cba_metadata(vLB_CBA_Python_meta_bytes)
    assert cba_metadata.tosca_meta_file_version == "1.0.0"
    assert cba_metadata.csar_version == 1.0
    assert cba_metadata.created_by == "PLATANIA, MARCO <platania@research.att.com>"
    assert cba_metadata.entry_definitions == "Definitions/vLB_CDS.json"
    assert cba_metadata.template_name == "vDNS-CDS-test1"
    assert cba_metadata.template_version == 1.0
    assert cba_metadata.template_tags == "vDNS-CDS-test1"

    with open(Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip"), "rb") as cba_file:
        b = Blueprint(cba_file.read())
    assert b.metadata.tosca_meta_file_version == "1.0.0"
    assert b.metadata.csar_version == 1.0
    assert b.metadata.created_by == "PLATANIA, MARCO <platania@research.att.com>"
    assert b.metadata.entry_definitions == "Definitions/vLB_CDS.json"
    assert b.metadata.template_name == "vDNS-CDS-test1"
    assert b.metadata.template_version == 1.0
    assert b.metadata.template_tags == "vDNS-CDS-test1"


def test_blueprint_get_mappings_from_mapping_file():
    b = Blueprint(b"test cba - it will never work")
    mappings = list(b.get_mappings_from_mapping_file(vLB_CBA_Python_base_template_mapping_bytes))
    assert len(mappings) == 5
    mapping = mappings[0]
    assert mapping.name == "service-instance-id"
    assert mapping.mapping_type == "string"
    assert mapping.dictionary_name == "service-instance-id"
    assert mapping.dictionary_sources == ["input"]


def test_blueprint_generate_data_dictionary_set():
    with open(Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip"), "rb") as cba_file:
        b = Blueprint(cba_file.read())
    dd_set = b.get_data_dictionaries()
    print(dd_set)


@patch.object(CdsElement, "_url", new_callable=PropertyMock)
def test_data_dictionary(cds_element_url_property_mock):
    cds_element_url_property_mock.return_value = "http://127.0.0.1"
    dd = DataDictionary({})
    assert dd.url == "http://127.0.0.1/resourcedictionary"
    assert dd.data_dictionary_json == {}

    dd = DataDictionary(DD_1)
    dd.name == DD_1["name"]


@patch.object(DataDictionary, "send_message")
def test_data_dictionary_upload(send_message_mock):
    dd = DataDictionary(DD_1)
    dd.upload()
    send_message_mock.assert_called_once()


@patch.object(DataDictionary, "send_message")
def test_data_dictionary_set(send_message_mock):
    dd_set = DataDictionarySet()

    dd_set.add(DataDictionary(DD_1))
    assert dd_set.length == 1

    dd_set.add(DataDictionary(DD_1))
    assert dd_set.length == 1

    dd_set.add(DataDictionary({"name": "test"}))
    assert dd_set.length == 2

    dd_set.upload()
    assert send_message_mock.call_count == 2


def test_mapping():
    m1 = Mapping(name="test",
                 mapping_type="string",
                 dictionary_name="test_dictionary_name", 
                 dictionary_sources=["dictionary_source_1"])

    m2 = Mapping(name="test", mapping_type="string", dictionary_name="test_dictionary_name", dictionary_sources=["dictionary_source_2"])

    assert m1 == m2
    m1.merge(m2)
    assert sorted(m1.dictionary_sources) == ["dictionary_source_1", "dictionary_source_2"]
    m1.merge(m2)
    assert sorted(m1.dictionary_sources) == ["dictionary_source_1", "dictionary_source_2"]


def test_mapping_set():
    ms = MappingSet()
    assert len(ms) == 0
    m1 = Mapping(name="test",
                 mapping_type="string",
                 dictionary_name="test_dictionary_name", 
                 dictionary_sources=["dictionary_source_1"])

    m2 = Mapping(name="test", mapping_type="string", dictionary_name="test_dictionary_name", dictionary_sources=["dictionary_source_2"])

    ms.add(m1)
    assert len(ms) == 1
    ms.add(m2)
    assert len(ms) == 1
    assert sorted(ms[0].dictionary_sources) == ["dictionary_source_1", "dictionary_source_2"]


def test_blueprint_get_workflows_from_entry_definitions_file():
    with open(Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip"), "rb") as cba_file:
        b = Blueprint(cba_file.read())
    assert len(b.workflows) == 3
    workflow = b.workflows[0]
    assert len(workflow.steps) == 1
    assert workflow.steps[0].name == "resource-assignment"
    assert workflow.steps[0].description == "Resource Assign Workflow"
    assert workflow.steps[0].target == "resource-assignment"
    assert len(workflow.inputs) == 2
    assert len(workflow.outputs) == 1


@patch.object(DataDictionary, "send_message")
def test_no_data_upload(send_message_mock):
    dd = DataDictionary(DD_1)
    send_message_mock.return_value = None 
    with raises(RuntimeError):
        dd.upload()
        send_message_mock.assert_called_once()



