class DomainError(Exception):
    """Base class for domain-level errors."""


class ValidationError(DomainError):
    """Raised when a value object cannot be instantiated."""


class NotFoundError(DomainError):
    """Raised when an aggregate cannot be located."""


class PermissionError(DomainError):
    """Raised when an operation is not allowed for a principal."""
