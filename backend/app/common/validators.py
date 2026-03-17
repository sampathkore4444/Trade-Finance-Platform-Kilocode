"""
Input Validators for Trade Finance Platform

This module provides validation functions for common input types.
"""

import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional, List
from app.common.exceptions import ValidationException


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If email is invalid
    """
    if not email:
        raise ValidationException(message="Email is required")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationException(message="Invalid email format")
    
    return True


def validate_phone(phone: str, country_code: Optional[str] = None) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        country_code: Optional country code
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If phone is invalid
    """
    if not phone:
        raise ValidationException(message="Phone number is required")
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Basic validation - 10-15 digits
    if not re.match(r'^\d{10,15}$', cleaned):
        raise ValidationException(message="Invalid phone number format")
    
    return True


def validate_password(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = False,
) -> bool:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum length
        require_uppercase: Require uppercase letter
        require_lowercase: Require lowercase letter
        require_digit: Require digit
        require_special: Require special character
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If password is weak
    """
    if not password:
        raise ValidationException(message="Password is required")
    
    if len(password) < min_length:
        raise ValidationException(
            message=f"Password must be at least {min_length} characters"
        )
    
    if require_uppercase and not re.search(r'[A-Z]', password):
        raise ValidationException(
            message="Password must contain at least one uppercase letter"
        )
    
    if require_lowercase and not re.search(r'[a-z]', password):
        raise ValidationException(
            message="Password must contain at least one lowercase letter"
        )
    
    if require_digit and not re.search(r'\d', password):
        raise ValidationException(
            message="Password must contain at least one digit"
        )
    
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationException(
            message="Password must contain at least one special character"
        )
    
    return True


def validate_amount(amount: any, min_value: Decimal = Decimal('0'), max_value: Optional[Decimal] = None) -> Decimal:
    """
    Validate monetary amount.
    
    Args:
        amount: Amount to validate (can be string, int, float, Decimal)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated Decimal amount
        
    Raises:
        ValidationException: If amount is invalid
    """
    try:
        if isinstance(amount, str):
            # Remove currency symbols and formatting
            cleaned = re.sub(r'[^\d.-]', '', amount)
            decimal_amount = Decimal(cleaned)
        else:
            decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ValidationException(message="Invalid amount format")
    
    if decimal_amount < min_value:
        raise ValidationException(
            message=f"Amount must be at least {min_value}"
        )
    
    if max_value and decimal_amount > max_value:
        raise ValidationException(
            message=f"Amount must not exceed {max_value}"
        )
    
    return decimal_amount


def validate_currency_code(code: str) -> bool:
    """
    Validate ISO 4217 currency code.
    
    Args:
        code: Currency code to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If currency code is invalid
    """
    valid_currencies = {
        'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'HKD', 'SGD',
        'CNY', 'INR', 'KRW', 'MXN', 'BRL', 'ZAR', 'AED', 'THB', 'MYR', 'IDR',
        'PHP', 'VND', 'PKR', 'BDT', 'LKR', 'NPR', 'MMK', 'KWD', 'SAR', 'QAR',
        'BHD', 'OMR', 'JOD', 'EGP', 'TRY', 'PLN', 'SEK', 'NOK', 'DKK', 'NZD',
    }
    
    code = code.upper()
    if code not in valid_currencies:
        raise ValidationException(
            message=f"Invalid currency code: {code}"
        )
    
    return True


def validate_bic_code(bic: str) -> bool:
    """
    Validate SWIFT/BIC code format.
    
    Args:
        bic: BIC code to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If BIC is invalid
    """
    if not bic:
        raise ValidationException(message="BIC code is required")
    
    # Remove whitespace
    bic = bic.replace(' ', '')
    
    # BIC should be 8 or 11 characters
    if len(bic) not in [8, 11]:
        raise ValidationException(message="BIC code must be 8 or 11 characters")
    
    # First 4 letters (bank code)
    if not bic[:4].isalpha():
        raise ValidationException(
            message="BIC first 4 characters must be letters (bank code)"
        )
    
    # Next 2 characters (country code)
    if not bic[4:6].isalpha():
        raise ValidationException(
            message="BIC characters 5-6 must be letters (country code)"
        )
    
    # Next 2 characters (location code)
    if not bic[6:8].isalnum():
        raise ValidationException(
            message="BIC characters 7-8 must be alphanumeric (location code)"
        )
    
    return True


def validate_iban(iban: str) -> bool:
    """
    Validate International Bank Account Number.
    
    Args:
        iban: IBAN to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If IBAN is invalid
    """
    if not iban:
        raise ValidationException(message="IBAN is required")
    
    # Remove whitespace and uppercase
    iban = iban.replace(' ', '').upper()
    
    # Check format
    if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$', iban):
        raise ValidationException(message="Invalid IBAN format")
    
    # Validate checksum
    # Move first 4 chars to end
    rearranged = iban[4:] + iban[:4]
    # Convert letters to numbers (A=10, B=11, etc.)
    numeric = ''
    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(10 + ord(char) - ord('A'))
    
    # Check mod 97
    if int(numeric) % 97 != 1:
        raise ValidationException(message="Invalid IBAN checksum")
    
    return True


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    allow_same_day: bool = True
) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        allow_same_day: Allow same start and end date
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If date range is invalid
    """
    if start_date > end_date:
        raise ValidationException(
            message="Start date must be before end date"
        )
    
    if not allow_same_day and start_date.date() == end_date.date():
        raise ValidationException(
            message="Start and end date cannot be the same"
        )
    
    return True


def validate_file_extension(
    filename: str,
    allowed_extensions: Optional[List[str]] = None
) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If extension is not allowed
    """
    if not allowed_extensions:
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.xls', '.xlsx']
    
    # Get extension
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if ext not in allowed_extensions:
        raise ValidationException(
            message=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    return True


def validate_reference_number(reference: str, prefix: Optional[str] = None) -> bool:
    """
    Validate transaction reference number.
    
    Args:
        reference: Reference number to validate
        prefix: Optional prefix requirement
        
    Returns:
        True if valid
        
    Raises:
        ValidationException: If reference is invalid
    """
    if not reference:
        raise ValidationException(message="Reference number is required")
    
    # Remove whitespace
    reference = reference.strip().upper()
    
    # Check prefix if provided
    if prefix:
        prefix = prefix.upper()
        if not reference.startswith(prefix):
            raise ValidationException(
                message=f"Reference must start with {prefix}"
            )
    
    # Alphanumeric with optional dashes
    if not re.match(r'^[A-Z0-9\-]{5,30}$', reference):
        raise ValidationException(
            message="Reference must be 5-30 alphanumeric characters"
        )
    
    return True
