"""This modules contains custom Myst exceptions."""


class BaseMystError(Exception):
    """Base class for any exceptions raised in this library."""


class MystClientError(BaseMystError):
    """Generic errors in the Myst client."""


class UnauthenticatedError(MystClientError):
    """Raised when authentication is missing or fails."""

    def __init__(self, message: str) -> None:
        """An `UnauthenticatedError` is initialized with a message."""
        super().__init__(message)
        self.message = message


class NotFound(MystClientError):
    """The requested resource was not found."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MystAPIError(BaseMystError):
    """Generic Myst API error."""

    def __init__(self, status_code: int, message: str) -> None:
        """A `MystAPIError` is initialized with an HTTP status code and a message."""
        super().__init__(message)
        self.status_code = status_code
        self.message = message
