
from unittest import mock

from onapsdk.aai.business.project import Project


PROJECTS = {
    "project": [
        {
            "project-name": "test-name",
            "resource-version": "1234"
        },
        {
            "project-name": "test-name2",
            "resource-version": "4321"
        }
    ]
}


@mock.patch("onapsdk.aai.business.project.Project.send_message_json")
def test_project_get_all(mock_send_message_json):
    mock_send_message_json.return_value = {}
    assert len(list(Project.get_all())) == 0

    mock_send_message_json.return_value = PROJECTS
    projects = list(Project.get_all())
    assert len(projects) == 2
    lob1, lob2 = projects
    assert lob1.name == "test-name"
    assert lob1.resource_version == "1234"
    assert lob2.name == "test-name2"
    assert lob2.resource_version == "4321"


@mock.patch("onapsdk.aai.business.project.Project.send_message_json")
def test_project_get_by_name(mock_send):
    Project.get_by_name(name="test-name")
    mock_send.assert_called_once_with("GET",
                                      "Get test-name project",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v20/business/projects/project/test-name")


@mock.patch("onapsdk.aai.business.project.Project.send_message")
@mock.patch("onapsdk.aai.business.project.Project.get_by_name")
def test_project_create(_, mock_send):
    Project.create(name="test-name")
    mock_send.assert_called_once_with("PUT",
                                      "Declare A&AI project",
                                      "https://aai.api.sparky.simpledemo.onap.org:30233/aai/v20/business/projects/project/test-name",
                                      data='{\n    "project-name": "test-name"\n}')
