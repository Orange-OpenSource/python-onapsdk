#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP Exception module."""

class SDKException(Exception):
    """Generic exception for ONAP SDK."""


class RequestError(SDKException):
    """Request error occured."""


class ConnectionFailed(RequestError):
    """Unable to connect."""


class APIError(RequestError):
    """API error occured."""


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
