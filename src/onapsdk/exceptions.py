#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP Exception module."""

from typing import Optional


class SDKException(Exception):
    """Generic exception for ONAP SDK."""


class RequestError(SDKException):
    """Request error occured."""


class ConnectionFailed(RequestError):
    """Unable to connect."""


class APIError(RequestError):
    """API error occured."""

    def __init__(self,
                 message: Optional[str] = None,
                 response_status_code: Optional[int] = None) -> None:
        """Init api error exception.

        Save message and optional response status code.

        Args:
            message (Optional[str]): Response error message. Defaults to None.
            response_status_code (Optional[int], optional): Response status code. Defaults to None.

        """
        if message:
            super().__init__(message)
        else:
            super().__init__()
        self._response_status_code: int = response_status_code if response_status_code else 0

    @property
    def response_status_code(self) -> int:
        """Response status code property.

        Returns:
            int: Response status code. If not set, returns 0

        """
        return self._response_status_code

    @response_status_code.setter
    def response_status_code(self, status_code: int) -> None:
        """Response status code property setter.

        Args:
            status_code (int): Response status code

        """
        self._response_status_code = status_code


class InvalidResponse(RequestError):
    """Unable to decode response."""


class ResourceNotFound(APIError):
    """Requested resource does not exist."""


class RelationshipNotFound(ResourceNotFound):
    """Required relationship is missing."""


class StatusError(SDKException):
    """Invalid status."""


class ParameterError(SDKException):
    """Parameter does not satisfy requirements."""

class ModuleError(SDKException):
    """Unable to import module."""


class ValidationError(SDKException):
    """Data validation failed."""


class FileError(ValidationError):
    """Reading in a file failed."""


class SettingsError(SDKException):
    """Some settings are wrong."""


class NoGuiError(SDKException):
    """No GUI available for this component."""
