#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Mixins module."""
from abc import ABC, abstractmethod
from time import sleep


class WaitForFinishMixin(ABC):
    """Wait for finish mixin.

    Mixin with wait_for_finish method and two properties:
     - completed,
     - finished.

    Can be used to wait for result of asynchronous tasks.

    """

    WAIT_FOR_SLEEP_TIME = 10

    @property
    @abstractmethod
    def completed(self) -> bool:
        """Store an information if object task is completed or not.

        Returns:
            bool: True if object task is completed, False otherwise.

        """

    @property
    @abstractmethod
    def finished(self) -> bool:
        """Store an information if object task is finished or not.

        Returns:
            bool: True if object task is finished, False otherwise.

        """

    def wait_for_finish(self) -> bool:
        """Wait until object task is finished.

        It uses time.sleep with WAIT_FOR_SLEEP_TIME value as a parameter to
            wait unitl request is finished (object's finished property is
            equal to True).

        Returns:
            bool: True if object's task is successfully completed, False otherwise

        """
        self._logger.debug(f"Wait until {self.__class__.__name__} task is not finished")
        while not self.finished:
            sleep(self.WAIT_FOR_SLEEP_TIME)
        self._logger.info(f"{self.__class__.__name__} task finished")
        return self.completed
