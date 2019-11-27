# SPDX-License-Identifier: Apache-2.0

from onapsdk.utils.configuration import tosca_path
from onapsdk.utils.configuration import components_needing_distribution

def test_tosca_path():
    assert tosca_path() == "/tmp/tosca_files/"

def test_components_needing_distribution():
    assert "SO" in components_needing_distribution()
    assert "sdnc" in components_needing_distribution()
    assert "aai" in components_needing_distribution()
