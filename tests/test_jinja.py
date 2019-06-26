# SPDX-License-Identifier: Apache-2.0
"""Test Jinja module."""
from jinja2 import Environment

from onapsdk.utils.jinja import jinja_env

def test_jinja_env():
    """test jinja_env function."""
    test_jinja_env = jinja_env()
    assert isinstance(test_jinja_env, Environment)
    assert 'sdc_element_action.json.j2' in test_jinja_env.list_templates()
    assert 'vendor_create.json.j2' in test_jinja_env.list_templates()
    assert 'vsp_create.json.j2' in test_jinja_env.list_templates()
    assert test_jinja_env.autoescape != None
