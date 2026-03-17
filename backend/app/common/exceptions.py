"""
Custom Exceptions for Trade Finance Platform

This module defines all custom exceptions used across the application
with appropriate HTTP status codes and error messages.
"""

from typing import Optional, Any


class TradeFinanceException(Exception):
    """
    Base exception for all trade finance application errors.
    """

    status_code: int = 500
    message: str = "An unexpected error occurred"
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class UnauthorizedException(TradeFinanceException):
    """
    Exception raised when authentication fails or token is invalid.
    """

    status_code = 401
    message = "Authentication required"
    error_code = "UNAUTHORIZED"


class InvalidCredentialsException(UnauthorizedException):
    """
    Exception raised when login credentials are invalid.
    """

    message = "Invalid username or password"
    error_code = "INVALID_CREDENTIALS"


class TokenExpiredException(UnauthorizedException):
    """
    Exception raised when JWT token has expired.
    """

    message = "Token has expired"
    error_code = "TOKEN_EXPIRED"


class InsufficientPermissionsException(TradeFinanceException):
    """
    Exception raised when user lacks required permissions.
    """

    status_code = 403
    message = "You don't have permission to perform this action"
    error_code = "INSUFFICIENT_PERMISSIONS"


class ForbiddenException(TradeFinanceException):
    """
    Exception raised when access to a resource is forbidden.
    """

    status_code = 403
    message = "Access forbidden"
    error_code = "FORBIDDEN"


class NotFoundException(TradeFinanceException):
    """
    Exception raised when requested resource is not found.
    """

    status_code = 404
    message = "Resource not found"
    error_code = "NOT_FOUND"


class ValidationException(TradeFinanceException):
    """
    Exception raised when input validation fails.
    """

    status_code = 422
    message = "Validation error"
    error_code = "VALIDATION_ERROR"


class DuplicateResourceException(TradeFinanceException):
    """
    Exception raised when trying to create a duplicate resource.
    """

    status_code = 409
    message = "Resource already exists"
    error_code = "DUPLICATE_RESOURCE"


class ResourceLockedException(TradeFinanceException):
    """
    Exception raised when resource is locked for editing.
    """

    status_code = 423
    message = "Resource is locked"
    error_code = "RESOURCE_LOCKED"


class BusinessRuleViolationException(TradeFinanceException):
    """
    Exception raised when a business rule is violated.
    """

    status_code = 400
    message = "Business rule violation"
    error_code = "BUSINESS_RULE_VIOLATION"


class ExternalServiceException(TradeFinanceException):
    """
    Exception raised when external service call fails.
    """

    status_code = 502
    message = "External service unavailable"
    error_code = "EXTERNAL_SERVICE_ERROR"


class RateLimitException(TradeFinanceException):
    """
    Exception raised when rate limit is exceeded.
    """

    status_code = 429
    message = "Rate limit exceeded"
    error_code = "RATE_LIMIT_EXCEEDED"


# Module-specific exceptions


class LCException(TradeFinanceException):
    """
    Base exception for Letter of Credit operations.
    """

    error_code = "LC_ERROR"


class LCNotFoundException(LCException, NotFoundException):
    """
    Exception raised when LC is not found.
    """

    message = "Letter of Credit not found"


class LCInvalidStateException(LCException, BusinessRuleViolationException):
    """
    Exception raised when LC is in invalid state for operation.
    """

    message = "Letter of Credit is in invalid state for this operation"


class GuaranteeException(TradeFinanceException):
    """
    Base exception for Bank Guarantee operations.
    """

    error_code = "GUARANTEE_ERROR"


class GuaranteeNotFoundException(GuaranteeException, NotFoundException):
    """
    Exception raised when Guarantee is not found.
    """

    message = "Bank Guarantee not found"


class LoanException(TradeFinanceException):
    """
    Base exception for Trade Loan operations.
    """

    error_code = "LOAN_ERROR"


class LoanNotFoundException(LoanException, NotFoundException):
    """
    Exception raised when Loan is not found.
    """

    message = "Trade Loan not found"


class ComplianceException(TradeFinanceException):
    """
    Base exception for Compliance operations.
    """

    status_code = 400
    error_code = "COMPLIANCE_ERROR"


class KYCFailedException(ComplianceException):
    """
    Exception raised when KYC verification fails.
    """

    message = "KYC verification failed"
    error_code = "KYC_FAILED"


class SanctionsMatchException(ComplianceException):
    """
    Exception raised when sanctions match is found.
    """

    message = "Sanctions list match found"
    error_code = "SANCTIONS_MATCH"
