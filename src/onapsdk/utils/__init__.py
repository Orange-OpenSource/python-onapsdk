#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP SDK utils package."""

from datetime import datetime


def get_zulu_time_isoformat() -> str:
    """Get zulu time in accepted by ONAP modules format.

    Returns:
        str: Actual Zulu time.

    """
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
