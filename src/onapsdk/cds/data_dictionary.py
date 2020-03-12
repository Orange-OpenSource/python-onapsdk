# SPDX-License-Identifier: Apache-2.0
"""CDS data dictionary module."""
from dataclasses import dataclass


@dataclass
class DataDictionary:
    """Data dictionary class."""

    data_dictionary: dict
