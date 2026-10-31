from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class IntegrationException(HTTPException):
    """Base exception for integration service errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class IntegrationItemNotFoundException(IntegrationException):
    """Raised when integration item is not found."""

    def __init__(self, detail: str = "Integration item not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="INTEGRATION_ITEM_NOT_FOUND",
        )


class IntegrationItemAlreadyExistsException(IntegrationException):
    """Raised when trying to create duplicate integration item."""

    def __init__(self, detail: str = "Integration item already exists"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INTEGRATION_ITEM_ALREADY_EXISTS",
        )


class InvalidIntegrationDataException(IntegrationException):
    """Raised when integration payload fails validation."""

    def __init__(self, detail: str = "Invalid integration data"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="INVALID_INTEGRATION_DATA",
        )


class IntegrationEditForbiddenException(IntegrationException):
    """Raised when user without rights tries to edit integration config."""

    def __init__(
        self, detail: str = "You are not allowed to edit this integration item"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="EDIT_INTEGRATION_FORBIDDEN",
        )


class IntegrationDeleteForbiddenException(IntegrationException):
    """Raised when user without rights tries to delete integration config."""

    def __init__(
        self, detail: str = "You are not allowed to delete this integration item"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="DELETE_INTEGRATION_FORBIDDEN",
        )


class IntegrationProcessingException(IntegrationException):
    """Raised when integration request processing fails."""

    def __init__(self, detail: str = "Error while processing integration payload"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="INTEGRATION_PROCESSING_ERROR",
        )


class ExternalServiceUnavailableException(IntegrationException):
    """Raised when downstream internal service is unavailable."""

    def __init__(self, detail: str = "Downstream service is unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="EXTERNAL_SERVICE_UNAVAILABLE",
        )


class InvalidApiKeyException(IntegrationException):
    """Raised when external client sends invalid API key."""

    def __init__(self, detail: str = "Invalid API key"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_API_KEY",
            headers={"WWW-Authenticate": "ApiKey"},
        )


class IntegrationAuthException(HTTPException):
    """Authentication / authorization exception for Integration service."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
