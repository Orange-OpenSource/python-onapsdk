#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Configuration package."""
from typing import List


def tosca_path() -> str:
    """Return tosca file paths."""
    return '/tmp/tosca_files/'


def components_needing_distribution() -> List[str]:
    """Return the list of components needing distribution."""
    return ["SO", "sdnc", "aai"]
