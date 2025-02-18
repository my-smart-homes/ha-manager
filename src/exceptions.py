from typing import Any

from fastapi import HTTPException, status


class DetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class NotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND


class NotAuthenticated(DetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})


class BadRequest(Exception):
    """The custom error that is raised when validation fail."""

    def __init__(self, message: str = None) -> None:
        self.message = message
        self.code = "VALIDATION_ERROR"
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(message)


class AuthenticationError(Exception):
    """The custom error that is raised when authentication fails."""

    def __init__(self, message: str = None) -> None:
        self.message = message
        self.code = "AUTHENTICATION_ERROR"
        self.status_code = status.HTTP_401_UNAUTHORIZED
        super().__init__(message)


class InternalServerError(Exception):
    """The custom error that is raised when internal server error occurs."""

    def __init__(self, message: str = None) -> None:
        self.message = message
        self.code = "INTERNAL_SERVER_ERROR"
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(message)
