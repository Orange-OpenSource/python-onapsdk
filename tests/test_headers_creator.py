# SPDX-License-Identifier: Apache-2.0

from onapsdk.utils.headers_creator import headers_sdc_creator


def test_headers_sdc_creator():
    base_header = {}
    sdc_headers_creator = headers_sdc_creator(base_header)
    assert base_header != sdc_headers_creator
    assert sdc_headers_creator["USER_ID"] == "cs0008"
    assert sdc_headers_creator["Authorization"]
