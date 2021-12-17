#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Definition of GUI objects."""
from dataclasses import dataclass
from typing import List

@dataclass
class GuiItem:
    """Class for keeping track of a GUI."""

    url: str
    status: int

@dataclass
class GuiList:
    """Class to list all the GUIs."""

    guilist: List[GuiItem]

    def add(self, element):
        """Add a GUi to GUI list."""
        if not isinstance(element, GuiItem):
            raise AttributeError
        self.guilist.append(element)
