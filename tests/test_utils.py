import pytest
import time

from onapsdk.onap_service import OnapService
from onapsdk.utils.mixins import WaitForFinishMixin


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
