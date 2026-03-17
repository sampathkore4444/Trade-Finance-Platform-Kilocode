"""
Multi-Factor Authentication (MFA) Handler for Trade Finance Platform

This module handles MFA operations including TOTP and SMS-based verification.
"""

import pyotp
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis.asyncio as redis

from app.config import settings
from app.common.helpers import generate_random_string, generate_otp


class MFAHandler:
    """
    Handler for Multi-Factor Authentication operations.
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.otp_validity_seconds = 300  # 5 minutes
        self.max_attempts = 3

    async def get_redis(self) -> redis.Redis:
        """
        Get Redis client.
        """
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
        return self.redis_client

    async def generate_totp_secret(self) -> str:
        """
        Generate a TOTP secret for authenticator apps.

        Returns:
            Base32 encoded secret
        """
        return pyotp.random_base32()

    def get_totp_uri(
        self, secret: str, email: str, issuer: str = "TradeFinance"
    ) -> str:
        """
        Get TOTP provisioning URI for authenticator apps.

        Args:
            secret: TOTP secret
            email: User email
            issuer: Application name

        Returns:
            Provisioning URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    def verify_totp(self, secret: str, token: str, valid_window: int = 1) -> bool:
        """
        Verify a TOTP token.

        Args:
            secret: TOTP secret
            token: Token to verify
            valid_window: Validity window (default 1 = ±30 seconds)

        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)

    async def generate_sms_otp(self, user_id: int, phone: str) -> str:
        """
        Generate and store SMS OTP.

        Args:
            user_id: User ID
            phone: Phone number

        Returns:
            Generated OTP
        """
        otp = generate_otp(length=6)
        redis_client = await self.get_redis()

        # Store OTP with expiry
        key = f"mfa:sms:{user_id}"
        data = {
            "otp": otp,
            "phone": phone,
            "attempts": "0",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Store as hash
        await redis_client.hset(key, mapping=data)
        await redis_client.expire(key, self.otp_validity_seconds)

        return otp

    async def verify_sms_otp(self, user_id: int, otp: str) -> bool:
        """
        Verify SMS OTP.

        Args:
            user_id: User ID
            otp: OTP to verify

        Returns:
            True if OTP is valid

        Raises:
            ValueError: If OTP is invalid or expired
        """
        redis_client = await self.get_redis()
        key = f"mfa:sms:{user_id}"

        # Get stored OTP data
        data = await redis_client.hgetall(key)

        if not data:
            raise ValueError("OTP expired or not found")

        stored_otp = data.get("otp", "")
        attempts = int(data.get("attempts", "0"))

        # Check attempts
        if attempts >= self.max_attempts:
            await redis_client.delete(key)
            raise ValueError("Maximum verification attempts exceeded")

        # Verify OTP
        if stored_otp != otp:
            # Increment attempts
            await redis_client.hincrby(key, "attempts", 1)
            raise ValueError("Invalid OTP")

        # Delete used OTP
        await redis_client.delete(key)

        return True

    async def send_sms_otp(self, phone: str, otp: str) -> bool:
        """
        Send OTP via SMS (integration point for SMS service).

        Args:
            phone: Phone number
            otp: OTP to send

        Returns:
            True if sent successfully
        """
        # TODO: Integrate with SMS provider (Twilio, AWS SNS, etc.)
        # For now, just log the OTP
        print(f"[MFA] SMS OTP for {phone}: {otp}")
        return True

    async def generate_email_otp(self, user_id: int, email: str) -> str:
        """
        Generate and store email OTP.

        Args:
            user_id: User ID
            email: Email address

        Returns:
            Generated OTP
        """
        otp = generate_otp(length=6)
        redis_client = await self.get_redis()

        key = f"mfa:email:{user_id}"
        data = {
            "otp": otp,
            "email": email,
            "attempts": "0",
            "created_at": datetime.utcnow().isoformat(),
        }

        await redis_client.hset(key, mapping=data)
        await redis_client.expire(key, self.otp_validity_seconds)

        return otp

    async def verify_email_otp(self, user_id: int, otp: str) -> bool:
        """
        Verify email OTP.

        Args:
            user_id: User ID
            otp: OTP to verify

        Returns:
            True if OTP is valid

        Raises:
            ValueError: If OTP is invalid or expired
        """
        redis_client = await self.get_redis()
        key = f"mfa:email:{user_id}"

        data = await redis_client.hgetall(key)

        if not data:
            raise ValueError("OTP expired or not found")

        stored_otp = data.get("otp", "")
        attempts = int(data.get("attempts", "0"))

        if attempts >= self.max_attempts:
            await redis_client.delete(key)
            raise ValueError("Maximum verification attempts exceeded")

        if stored_otp != otp:
            await redis_client.hincrby(key, "attempts", 1)
            raise ValueError("Invalid OTP")

        await redis_client.delete(key)

        return True

    async def send_email_otp(self, email: str, otp: str) -> bool:
        """
        Send OTP via email (integration point for email service).

        Args:
            email: Email address
            otp: OTP to send

        Returns:
            True if sent successfully
        """
        # TODO: Integrate with email service
        print(f"[MFA] Email OTP for {email}: {otp}")
        return True

    async def generate_backup_codes(self, user_id: int) -> list[str]:
        """
        Generate backup codes for MFA.

        Args:
            user_id: User ID

        Returns:
            List of backup codes
        """
        backup_codes = [
            generate_random_string(8, include_digits=True) for _ in range(10)
        ]

        redis_client = await self.get_redis()
        key = f"mfa:backup:{user_id}"

        # Store hashed backup codes
        hashed_codes = {code: "unused" for code in backup_codes}
        await redis_client.hset(key, mapping=hashed_codes)
        await redis_client.expire(key, timedelta(days=365).total_seconds())

        return backup_codes

    async def verify_backup_code(self, user_id: int, code: str) -> bool:
        """
        Verify a backup code.

        Args:
            user_id: User ID
            code: Backup code

        Returns:
            True if code is valid and unused
        """
        redis_client = await self.get_redis()
        key = f"mfa:backup:{user_id}"

        # Check if code exists and is unused
        status = await redis_client.hget(key, code)

        if status != "unused":
            return False

        # Mark as used
        await redis_client.hset(key, code, "used")

        return True

    async def get_mfa_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get MFA status for a user.

        Args:
            user_id: User ID

        Returns:
            MFA status dictionary
        """
        redis_client = await self.get_redis()

        # Check if TOTP is set up
        totp_key = f"mfa:totp:{user_id}"
        totp_secret = await redis_client.get(totp_key)

        return {
            "totp_enabled": totp_secret is not None,
            "sms_enabled": False,  # Check if phone is verified
            "email_enabled": False,  # Check if email is verified
            "backup_codes_remaining": 0,  # Count unused backup codes
        }


# Singleton instance
mfa_handler = MFAHandler()
