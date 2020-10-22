#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test Vnf module."""

from onapsdk.sdc.service import Vnf


def test_tosca_groups_parsed_name():

    vnf = Vnf(
        name="vFWCL_vPKG-vf 0",
        node_template_type=None,
        metadata=None,
        properties=None,
        capabilities=None
    )
    assert vnf.tosca_groups_parsed_name == "vfwcl_vpkgvf0"

    vnf = Vnf(
        name="vFWCL_vFWSNK-vf 0",
        node_template_type=None,
        metadata=None,
        properties=None,
        capabilities=None
    )
    assert vnf.tosca_groups_parsed_name == "vfwcl_vfwsnkvf0"

    vnf = Vnf(
        name="vfwcds_VF 0",
        node_template_type=None,
        metadata=None,
        properties=None,
        capabilities=None
    )
    assert vnf.tosca_groups_parsed_name == "vfwcds_vf0"

    vnf = Vnf(
        name="ubuntu16_VF 0",
        node_template_type=None,
        metadata=None,
        properties=None,
        capabilities=None
    )
    assert vnf.tosca_groups_parsed_name == "ubuntu16_vf0"
