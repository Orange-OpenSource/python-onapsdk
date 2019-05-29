#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import onapsdk.version as version

def test_version():
  assert version.__version__ == '0.0.1'
