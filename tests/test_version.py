#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test version module."""

import onapsdk.version as version

def test_version():
  """Check version is the right one."""
  assert version.__version__ == '0.0.1'
