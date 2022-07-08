# SPDX-License-Identifier: Apache-2.0
import json
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch, PropertyMock, mock_open

from pytest import raises

from onapsdk.cds.blueprint import Blueprint, Mapping, MappingSet, ResolvedTemplate, Workflow
from onapsdk.cds.blueprint_processor import Blueprintprocessor
from onapsdk.cds.cds_element import CdsElement
from onapsdk.cds.data_dictionary import DataDictionary, DataDictionarySet
from onapsdk.exceptions import FileError, ParameterError, RequestError, ValidationError
from onapsdk.utils.gui import GuiItem, GuiList

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


RAW_DD = {
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


vLB_CBA_Python_meta_bytes = b'TOSCA-Meta-File-Version: 1.0.0\nCSAR-Version: 1.0\nCreated-By: PLATANIA, MARCO <platania@research.att.com>\nEntry-Definitions: Definitions/vLB_CDS.json\nTemplate-Tags: vDNS-CDS-test1\nContent-Type: application/vnd.oasis.bpmn\nTemplate-Name: vDNS-CDS-test1\nTemplate-Version: 1.0'

vLB_CBA_Python_base_template_mapping_bytes = b'[\n  {\n    "name": "service-instance-id",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "service-instance-id",\n    "dictionary-source": "input",\n    "dependencies": [],\n    "version": 0\n  },\n  {\n    "name": "vnf-id",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vnf-id",\n    "dictionary-source": "input",\n    "dependencies": [],\n    "version": 0\n  },\n  {\n    "name": "vdns_vf_module_id",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vdns_vf_module_id",\n    "dictionary-source": "sdnc",\n    "dependencies": [\n\t  "service-instance-id",\n      "vnf-id"\n    ],\n    "version": 0\n  },\n  {\n    "name": "vdns_int_private_ip_0",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vdns_int_private_ip_0",\n    "dictionary-source": "sdnc",\n    "dependencies": [\n      "service-instance-id",\n      "vnf-id",\n      "vdns_vf_module_id"\n    ],\n    "version": 0\n  },\n  {\n    "name": "vdns_onap_private_ip_0",\n    "property": {\n      "description": "",\n      "required": false,\n      "type": "string",\n      "status": "",\n      "constraints": [\n        {}\n      ],\n      "entry_schema": {\n        "type": ""\n      }\n    },\n    "input-param": false,\n    "dictionary-name": "vdns_onap_private_ip_0",\n    "dictionary-source": "sdnc",\n    "dependencies": [\n      "service-instance-id",\n      "vnf-id",\n      "vdns_vf_module_id"\n    ],\n    "version": 0\n  }\n]'


@patch.object(Blueprint, "send_message")
def test_blueprint_enrichment(send_message_mock):
    blueprint = Blueprint(b"test cba - it will never work")
    blueprint.enrich()
    send_message_mock.assert_called_once()
    send_message_mock.reset_mock()
    send_message_mock.side_effect = RequestError
    with raises(RequestError):
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


def test_blueprint_load_from_file():
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test.zip")
        with open(path, "wb") as f:
            f.write(b"test cba - it will never work")
        blueprint = Blueprint.load_from_file(path)
        assert blueprint.cba_file_bytes == b"test cba - it will never work"

def test_blueprint_load_from_file_file_error():

    with TemporaryDirectory() as tmpdirname, \
        patch("__main__.open", new_callable=mock_open) as mo, \
        raises(FileError) as exc:

        path = os.path.join(tmpdirname, "nonexistent_file.zip")
        mo.side_effect = FileNotFoundError

        Blueprint.load_from_file(path)

    assert exc.type == FileError


def test_blueprint_save():
    blueprint = Blueprint(b"test cba - it will never work")
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test.zip")
        blueprint.save(path)
        with open(path, "rb") as f:
            assert f.read() == b"test cba - it will never work"


def test_blueprint_read_cba_metadata():
    b = Blueprint(b"test cba - it will never work")
    with raises(ValidationError) as exc:
        b.get_cba_metadata(b"Invalid")
        b.get_cba_metadata(b"123: 456")
    assert exc.type is ValidationError

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

    with raises(ValidationError) as exc:
        DataDictionary({})
    assert exc.type is ValidationError

    dd = DataDictionary({}, fix_schema=False)
    assert dd.url == "http://127.0.0.1/api/v1/dictionary"
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

    dd_set.add(DataDictionary({"name": "test"}, fix_schema=False))
    assert dd_set.length == 2

    dd_set.upload()
    assert send_message_mock.call_count == 2


def test_data_dictionary_set_save_to_file_load_from_file():
    dd = DataDictionarySet()
    dd.add(DataDictionary(DD_1))
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "dd.json")
        dd.save_to_file(path)
        with open(path, "r") as f:
            assert f.read() == json.dumps([dd.data_dictionary_json for dd in dd.dd_set], indent=4)
        dd_2 = DataDictionarySet.load_from_file(path)
        assert dd.dd_set == dd_2.dd_set

def test_data_dictionary_load_from_file_file_error():

    with TemporaryDirectory() as tmpdirname, \
        patch("__main__.open", new_callable=mock_open) as mo, \
        raises(FileError) as exc:

        path = os.path.join(tmpdirname, "nonexistent_file.zip")
        mo.side_effect = FileNotFoundError

        DataDictionarySet.load_from_file(path)

    assert exc.type == FileError


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


def test_blueprint_get_workflow_by_name():
    with open(Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip"), "rb") as cba_file:
        b = Blueprint(cba_file.read())
    workflow = b.get_workflow_by_name("resource-assignment")
    assert workflow.name == "resource-assignment"
    workflow = b.get_workflow_by_name("config-assign")
    assert workflow.name == "config-assign"
    workflow = b.get_workflow_by_name("config-deploy")
    assert workflow.name == "config-deploy"
    with raises(ParameterError):
        b.get_workflow_by_name("non-existing-workflow")


@patch.object(Workflow, "send_message")
def test_workflow_execute(send_message_mock):
    metadata = MagicMock(template_name="test", template_version="test")
    blueprint = MagicMock(metadata=metadata)
    workflow = Workflow("test_workflow", {}, blueprint)
    assert len(workflow.steps) == 0
    assert len(workflow.inputs) == 0
    assert len(workflow.outputs) == 0
    workflow.execute({})
    send_message_mock.assert_called_once()


def test_data_dictionary_validation():
    assert DataDictionary(DD_1).has_valid_schema()
    raw_dd = DataDictionary(RAW_DD, fix_schema=False)
    assert not raw_dd.has_valid_schema()
    raw_dd = DataDictionary(RAW_DD, fix_schema=True)
    assert raw_dd.has_valid_schema()


@patch.object(Blueprintprocessor, "send_message")
def test_blueprintprocessor_bootstrap(mock_send_message):

    Blueprintprocessor.bootstrap()
    assert mock_send_message.called_once()
    assert mock_send_message.call_args[1]["data"] == '{\n    "loadModelType" : true,\n    "loadResourceDictionary" : true,\n    "loadCBA" : true\n}'
    mock_send_message.reset_mock()

    Blueprintprocessor.bootstrap(load_cba=False, load_model_type=False, load_resource_dictionary=False)
    assert mock_send_message.called_once()
    assert mock_send_message.call_args[1]["data"] == '{\n    "loadModelType" : false,\n    "loadResourceDictionary" : false,\n    "loadCBA" : false\n}'


@patch.object(DataDictionary, "send_message_json")
def test_data_dictionary_get_by_name(mock_send_message_json):

    DataDictionary.get_by_name("test_name")
    mock_send_message_json.assert_called_once()
    assert "test_name" in mock_send_message_json.call_args[0][2]


@patch.object(CdsElement, "send_message")
def test_get_guis(send_message_mock):
    component = CdsElement()
    send_message_mock.return_value.status_code = 200
    send_message_mock.return_value.url = "http://portal.api.simpledemo.onap.org:30449/"
    gui_results = component.get_guis()
    assert type(gui_results) == GuiList
    assert gui_results.guilist[0].url == send_message_mock.return_value.url
    assert gui_results.guilist[0].status == send_message_mock.return_value.status_code


@patch.object(ResolvedTemplate, "send_message_json")
@patch.object(CdsElement, "_url", new_callable=PropertyMock)
def test_blueprint_get_resolved_template(cds_element_url_property_mock, mock_send_message_json):
    cds_element_url_property_mock.return_value = "http://127.0.0.1"

    with open(Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip"), "rb") as cba_file:
        b = Blueprint(cba_file.read())
    b.get_resolved_template("test_artifact")
    assert mock_send_message_json.called_once()
    assert mock_send_message_json.call_args[0][2] == 'http://127.0.0.1/api/v1/template?bpName=vDNS-CDS-test1&bpVersion=1.0&artifactName=test_artifact&format=application%2Fjson'


@patch.object(ResolvedTemplate, "send_message")
@patch.object(CdsElement, "_url", new_callable=PropertyMock)
def test_blueprint_store_resolved_template(cds_element_url_property_mock, mock_send_message):
    cds_element_url_property_mock.return_value = "http://127.0.0.1"

    with open(Path(Path(__file__).resolve().parent, "data/vLB_CBA_Python.zip"), "rb") as cba_file:
        b = Blueprint(cba_file.read())
    b.store_resolved_template("test_artifact", resolution_key="resolution_key", data={"a": "b"})
    assert mock_send_message.called_once()
    assert mock_send_message.call_args[0][2] == 'http://127.0.0.1/api/v1/template/vDNS-CDS-test1/1.0/test_artifact/resolution_key'


@patch.object(ResolvedTemplate, "send_message_json")
@patch.object(CdsElement, "_url", new_callable=PropertyMock)
def test_resolved_template_get_template_url(cds_element_url_property_mock, mock_send_message_json):
    cds_element_url_property_mock.return_value = "http://127.0.0.1"
    blueprint = MagicMock()
    blueprint.metadata.template_name = "test_blueprint"
    blueprint.metadata.template_version = "v1.0.0"
    rt = ResolvedTemplate(blueprint, "test_artifact")
    rt.get_resolved_template()
    assert mock_send_message_json.called_once()
    assert mock_send_message_json.call_args[0][2] == 'http://127.0.0.1/api/v1/template?bpName=test_blueprint&bpVersion=v1.0.0&artifactName=test_artifact&format=application%2Fjson'

    mock_send_message_json.reset_mock()
    blueprint = MagicMock()
    blueprint.metadata.template_name = "test_blueprint"
    blueprint.metadata.template_version = "v1.0.0"
    rt = ResolvedTemplate(blueprint, resolution_key="test_rk")
    rt.get_resolved_template()
    assert mock_send_message_json.called_once()
    assert mock_send_message_json.call_args[0][2] == 'http://127.0.0.1/api/v1/template?bpName=test_blueprint&bpVersion=v1.0.0&resolutionKey=test_rk&format=application%2Fjson'

    mock_send_message_json.reset_mock()
    blueprint = MagicMock()
    blueprint.metadata.template_name = "test_blueprint"
    blueprint.metadata.template_version = "v1.0.0"
    rt = ResolvedTemplate(blueprint, resource_id="r_id", resource_type="r_type")
    rt.get_resolved_template()
    assert mock_send_message_json.called_once()
    assert mock_send_message_json.call_args[0][2] == 'http://127.0.0.1/api/v1/template?bpName=test_blueprint&bpVersion=v1.0.0&resourceType=r_type&resourceId=r_id&format=application%2Fjson'


@patch.object(ResolvedTemplate, "send_message")
@patch.object(CdsElement, "_url", new_callable=PropertyMock)
def test_resolved_template_store_template_url(cds_element_url_property_mock, mock_send_message):
    cds_element_url_property_mock.return_value = "http://127.0.0.1"

    blueprint = MagicMock()
    blueprint.metadata.template_name = "test_blueprint"
    blueprint.metadata.template_version = "v1.0.0"
    rt = ResolvedTemplate(blueprint, "test_artifact", resolution_key="resolution_key")
    rt.store_resolved_template({"a": "b"})
    assert mock_send_message.called_once()
    assert mock_send_message.call_args[0][2] == 'http://127.0.0.1/api/v1/template/test_blueprint/v1.0.0/test_artifact/resolution_key'

    mock_send_message.reset_mock()
    rt = ResolvedTemplate(blueprint, "test_artifact", resource_id="resource_id", resource_type="resource_type")
    rt.store_resolved_template({"a": "b"})
    assert mock_send_message.called_once()
    assert mock_send_message.call_args[0][2] == 'http://127.0.0.1/api/v1/template/test_blueprint/v1.0.0/test_artifact/resource_type/resource_id'

    mock_send_message.reset_mock()
    rt = ResolvedTemplate(blueprint, "test_artifact")
    with raises(ParameterError):
        rt.store_resolved_template({"a": "b"})
