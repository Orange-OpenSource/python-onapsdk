class SdkException(Exception):
    """Generic exception for ONAP SDK."""


class RequestError(SdkException):
    """Request error occured."""


class ConnectionError(RequestError):
    """Unable to connect."""


class ApiError(RequestError):
    """API error occured."""


class InvalidResponse(RequestError):
    """Unable to decode response."""


class ResourceNotFound(ApiError):
    """Requested resource does not exist."""


class RelationshipNotFound(ResourceNotFound):
    """Required relationship is missing."""


class StatusError(SdkException):
    """Invalid status."""


class ParameterError(SdkException):
    """Parameter does not satisfy requirements."""


class PackageError(ParameterError):
    """Files uploading went wrong."""


class ModuleError(SdkException):
    """Unable to import module."""


class ValidationException(SdkException):
    """Data validation failed."""


class SettingsError(SdkException):
    """Some settings are wrong."""
