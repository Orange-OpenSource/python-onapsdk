#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Mixins module."""
from abc import ABC, abstractmethod
from ctypes import c_bool
from multiprocessing import Process, Value
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

    def _wait_for_finish(self, return_value: Value) -> bool:
        """Wait until object task is finished.

        Method called in another process.

        Args:
            return_value(Value): value shared with main process to pass there
                if object task was completed or not

        """
        while not self.finished:
            sleep(self.WAIT_FOR_SLEEP_TIME)
        self._logger.info(f"{self.__class__.__name__} task finished")
        return_value.value = self.completed

    def wait_for_finish(self, timeout: float = None) -> bool:
        """Wait until object task is finished.

        It uses time.sleep with WAIT_FOR_SLEEP_TIME value as a parameter to
            wait unitl request is finished (object's finished property is
            equal to True).

        It runs another process to control time of the function. If process timed out
            TimeoutError is going to be raised.

        Args:
            timeout(float, optional): positive number, wait at most timeout seconds

        Raises:
            TimeoutError: Raised when function timed out

        Returns:
            bool: True if object's task is successfully completed, False otherwise

        """
        self._logger.debug(f"Wait until {self.__class__.__name__} task is not finished")
        return_value: Value = Value(c_bool)
        wait_for_process: Process = Process(target=self._wait_for_finish, args=(return_value,))
        try:
            wait_for_process.start()
            wait_for_process.join(timeout)
            return return_value.value
        finally:
            if wait_for_process.is_alive():
                wait_for_process.terminate()
                raise TimeoutError
