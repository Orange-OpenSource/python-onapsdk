import os
import pytest
import requests

from tempfile import TemporaryDirectory

from onapsdk.configuration import settings
from onapsdk.cds.blueprint import Blueprint
from onapsdk.cds.data_dictionary import DataDictionary, DataDictionarySet


@pytest.mark.integration
def test_cds_connection():

    TEST_DD_PATH = os.path.join(os.getcwd(), "integration_tests/test_files/test_dd.json")
    TEST_CBA_PATH = os.path.join(os.getcwd(), "integration_tests/test_files/test_vLB_CBA_Python.zip")


    # Endpoint availability
    response = requests.post("{}/api/v1/dictionary".format(settings.CDS_URL))
    assert response.status_code == 200

    response = requests.post("{}/api/v1/blueprint-model/enrich".format(settings.CDS_URL))
    assert response.status_code == 200

    response = requests.post("{}/api/v1/blueprint-model/publish".format(settings.CDS_URL))
    assert response.status_code == 200


    # Reads from the file system
    dd_set = DataDictionarySet.load_from_file(TEST_DD_PATH, True)
    blueprint = Blueprint.load_from_file(TEST_CBA_PATH)


    # Connection availability between CDS API and Blueprint/DataDictionarySet
    dd_set.upload()
    assert type(blueprint.cba_file_bytes) == bytes

    for dd in dd_set.dd_set:
        dd_obj = DataDictionary.get_by_name(dd.name)
        assert dd_obj == dd

    blueprint = blueprint.enrich()
    assert type(blueprint.cba_file_bytes) == bytes

    blueprint.publish()


    # Writes to the file system
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test-CBA-enriched.zip")
        blueprint.save(path)
