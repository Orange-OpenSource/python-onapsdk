# SPDX-License-Identifier: Apache-2.0

from onapsdk.utils.headers_creator import headers_sdc_creator
from onapsdk.utils.headers_creator import headers_sdc_tester
from onapsdk.utils.headers_creator import headers_sdc_governor
from onapsdk.utils.headers_creator import headers_sdc_operator


def test_headers_sdc_creator():
    base_header = {}
    sdc_headers_creator = headers_sdc_creator(base_header)
    assert base_header != sdc_headers_creator
    assert sdc_headers_creator["USER_ID"] == "cs0008"
    assert sdc_headers_creator["Authorization"]

def test_headers_sdc_tester():
    base_header = {}
    sdc_headers_tester = headers_sdc_tester(base_header)
    assert base_header != sdc_headers_tester
    assert sdc_headers_tester["USER_ID"] == "jm0007"
    assert sdc_headers_tester["Authorization"]

def test_headers_sdc_governor():
    base_header = {}
    sdc_headers_governor = headers_sdc_governor(base_header)
    assert base_header != sdc_headers_governor
    assert sdc_headers_governor["USER_ID"] == "gv0001"
    assert sdc_headers_governor["Authorization"]

def test_headers_sdc_operator():
    base_header = {}
    sdc_headers_operator = headers_sdc_operator(base_header)
    assert base_header != sdc_headers_operator
    assert sdc_headers_operator["USER_ID"] == "op0001"
    assert sdc_headers_operator["Authorization"]
