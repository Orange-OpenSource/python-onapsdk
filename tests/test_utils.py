import os

import pytest
import time

from onapsdk.onap_service import OnapService
from onapsdk.utils.mixins import WaitForFinishMixin
from onapsdk.utils import load_json_file


class TestWaitForFinish(WaitForFinishMixin, OnapService):

    @property
    def completed(self):
        return True

    @property
    def finished(self):
        time.sleep(0.1)
        return True


def test_wait_for_finish_timeout():
    t = TestWaitForFinish()
    with pytest.raises(TimeoutError):
        t.wait_for_finish(timeout=0.01)
    t.wait_for_finish()


def test_load_json_file():
    path_to_event: str = os.path.join(os.getcwd(), "tests/data/utils_load_json_file_test.json")
    test_json: str = load_json_file(path_to_event)
    assert test_json == '{"event": {"test1": "val1"}}'
