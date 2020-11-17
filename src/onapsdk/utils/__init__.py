#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK utils package."""
import json
from datetime import datetime


def get_zulu_time_isoformat() -> str:
    """Get zulu time in accepted by ONAP modules format.

    Returns:
        str: Actual Zulu time.

    """
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def load_json_file(path_to_json_file: str) -> str:
    """
    Return json as string from selected file.

    Args:
        path_to_json_file: (str) path to file with json
    Returns:
        File content as string (str)
    """
    with open(path_to_json_file) as json_file:
        data = json.load(json_file)
        return json.dumps(data)
