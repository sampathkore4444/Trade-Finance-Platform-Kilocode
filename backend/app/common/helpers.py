"""
Helper Utilities for Trade Finance Platform

This module provides common utility functions used across the application.
"""

import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict
from decimal import Decimal, ROUND_HALF_UP
import re


def generate_random_string(
    length: int = 32, include_digits: bool = True, include_special: bool = False
) -> str:
    """
    Generate a random string of specified length.

    Args:
        length: Length of the random string
        include_digits: Include digits in the string
        include_special: Include special characters

    Returns:
        Random string
    """
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation

    return "".join(random.choice(chars) for _ in range(length))


def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP of specified length.

    Args:
        length: Length of the OTP (default 6)

    Returns:
        OTP string
    """
    return "".join(random.choice(string.digits) for _ in range(length))


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm.

    Args:
        value: String to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)

    Returns:
        Hex digest of the hash
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(value.encode("utf-8"))
    return hash_obj.hexdigest()


def format_currency(
    amount: Decimal, currency: str = "USD", decimal_places: int = 2
) -> str:
    """
    Format a decimal amount as currency string.

    Args:
        amount: Decimal amount
        currency: Currency code
        decimal_places: Number of decimal places

    Returns:
        Formatted currency string
    """
    return f"{currency} {amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.{decimal_places}f}"


def parse_currency(value: str) -> Decimal:
    """
    Parse a currency string to Decimal.

    Args:
        value: Currency string (e.g., "USD 1,234.56")

    Returns:
        Decimal amount
    """
    # Remove currency code and formatting
    cleaned = re.sub(r"[^\d.-]", "", value)
    return Decimal(cleaned)


def calculate_percentage(
    value: Decimal, total: Decimal, decimal_places: int = 2
) -> Decimal:
    """
    Calculate percentage of value against total.

    Args:
        value: Numerator value
        total: Denominator value
        decimal_places: Number of decimal places

    Returns:
        Percentage value
    """
    if total == 0:
        return Decimal("0")

    percentage = (value / total) * 100
    return percentage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def add_business_days(start_date: datetime, days: int) -> datetime:
    """
    Add business days to a date (excluding weekends).

    Args:
        start_date: Starting date
        days: Number of business days to add

    Returns:
        Resulting datetime
    """
    current_date = start_date
    days_added = 0

    while days_added < days:
        current_date += timedelta(days=1)
        # Skip weekends (5=Saturday, 6=Sunday)
        if current_date.weekday() < 5:
            days_added += 1

    return current_date


def get_date_range(period: str) -> tuple[datetime, datetime]:
    """
    Get date range for common periods.

    Args:
        period: Period type (today, week, month, quarter, year)

    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "today":
        return today, today + timedelta(days=1)
    elif period == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=7)
    elif period == "month":
        start = today.replace(day=1)
        if today.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        return start, end
    elif period == "quarter":
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        end = start.replace(month=start.month + 3)
        return start, end
    elif period == "year":
        return today.replace(month=1, day=1), today.replace(
            year=today.year + 1, month=1, day=1
        )
    else:
        return today, today + timedelta(days=1)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing special characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Replace special characters with underscore
    sanitized = re.sub(r"[^\w\s.-]", "", filename)
    # Replace multiple spaces/underscores with single underscore
    sanitized = re.sub(r"[\s_]+", "_", sanitized)
    return sanitized


def truncate_string(value: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to specified length.

    Args:
        value: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(value) <= max_length:
        return value
    return value[: max_length - len(suffix)] + suffix


def paginate_list(
    items: List[Any], page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """
    Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Dictionary with pagination info and items
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """
    Mask sensitive data showing only last N characters.

    Args:
        data: Data to mask
        visible_chars: Number of characters to show
        mask_char: Character to use for masking

    Returns:
        Masked string
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)

    return mask_char * (len(data) - visible_chars) + data[-visible_chars:]


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove common formatting characters
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    return bool(re.match(r"^\d{10,15}$", cleaned))


def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate number of days between two dates.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Number of days
    """
    return (end_date - start_date).days
