

from unittest.mock import patch

from onapsdk.vid import (
    OwningEntity,
    Project,
    LineOfBusiness,
    Platform
)


@patch.object(LineOfBusiness, "send_message")
def test_line_of_business(send_message_mock):
    assert LineOfBusiness.get_create_url() == "https://vid.api.simpledemo.onap.org:30200/vid/maintenance/category_parameter/lineOfBusiness"

    line_of_businnes = LineOfBusiness.create("test")
    assert line_of_businnes.name == "test"


@patch.object(OwningEntity, "send_message")
def test_owning_entity(send_message_mock):
    assert OwningEntity.get_create_url() == "https://vid.api.simpledemo.onap.org:30200/vid/maintenance/category_parameter/owningEntity"

    owning_entity = OwningEntity.create("test")
    assert owning_entity.name == "test"


@patch.object(Project, "send_message")
def test_project(send_message_mock):
    assert Project.get_create_url() == "https://vid.api.simpledemo.onap.org:30200/vid/maintenance/category_parameter/project"

    project = Project.create("test")
    assert project.name == "test"


@patch.object(Platform, "send_message")
def test_platform(send_message_mock):
    assert Platform.get_create_url() == "https://vid.api.simpledemo.onap.org:30200/vid/maintenance/category_parameter/platform"

    platform = Platform.create("test")
    assert platform.name == "test"
