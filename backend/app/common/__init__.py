"""
Common utilities package for Trade Finance Platform
"""

from app.common.exceptions import (
    TradeFinanceException,
    UnauthorizedException,
    InvalidCredentialsException,
    TokenExpiredException,
    InsufficientPermissionsException,
    NotFoundException,
    ValidationException,
    DuplicateResourceException,
    ResourceLockedException,
    BusinessRuleViolationException,
    ExternalServiceException,
    RateLimitException,
)

from app.common.helpers import (
    generate_random_string,
    generate_otp,
    hash_string,
    format_currency,
    parse_currency,
    calculate_percentage,
    add_business_days,
    get_date_range,
    sanitize_filename,
    truncate_string,
    paginate_list,
    mask_sensitive_data,
    validate_email,
    validate_phone,
    calculate_days_between,
)

from app.common.validators import (
    validate_email,
    validate_phone,
    validate_password,
    validate_amount,
    validate_currency_code,
    validate_bic_code,
    validate_iban,
    validate_date_range,
    validate_file_extension,
    validate_reference_number,
)

__all__ = [
    # Exceptions
    "TradeFinanceException",
    "UnauthorizedException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "InsufficientPermissionsException",
    "NotFoundException",
    "ValidationException",
    "DuplicateResourceException",
    "ResourceLockedException",
    "BusinessRuleViolationException",
    "ExternalServiceException",
    "RateLimitException",
    # Helpers
    "generate_random_string",
    "generate_otp",
    "hash_string",
    "format_currency",
    "parse_currency",
    "calculate_percentage",
    "add_business_days",
    "get_date_range",
    "sanitize_filename",
    "truncate_string",
    "paginate_list",
    "mask_sensitive_data",
    "validate_email",
    "validate_phone",
    "calculate_days_between",
    # Validators
    "validate_password",
    "validate_amount",
    "validate_currency_code",
    "validate_bic_code",
    "validate_iban",
    "validate_date_range",
    "validate_file_extension",
    "validate_reference_number",
]
