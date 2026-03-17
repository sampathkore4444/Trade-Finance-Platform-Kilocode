"""
JWT Token Handler for Trade Finance Platform

This module handles JWT token creation, validation, and refresh.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.common.exceptions import TokenExpiredException, InvalidCredentialsException


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTHandler:
    """
    Handler for JWT token operations.
    """

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self,
        subject: str,
        user_id: int,
        roles: List[str],
        permissions: List[str],
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a JWT access token.

        Args:
            subject: Subject identifier (username/email)
            user_id: User ID
            roles: User roles
            permissions: User permissions
            additional_claims: Additional claims to include

        Returns:
            Encoded JWT token
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        claims = {
            "sub": subject,
            "user_id": user_id,
            "roles": roles,
            "permissions": permissions,
            "iat": now,
            "exp": expire,
            "type": "access",
        }

        if additional_claims:
            claims.update(additional_claims)

        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, subject: str, user_id: int) -> str:
        """
        Create a JWT refresh token.

        Args:
            subject: Subject identifier
            user_id: User ID

        Returns:
            Encoded JWT refresh token
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)

        claims = {
            "sub": subject,
            "user_id": user_id,
            "iat": now,
            "exp": expire,
            "type": "refresh",
        }

        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Token payload

        Raises:
            TokenExpiredException: If token has expired
            JWTError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except JWTError as e:
            raise InvalidCredentialsException(message=str(e))

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Verify an access token.

        Args:
            token: Access token

        Returns:
            Token payload

        Raises:
            TokenExpiredException: If token has expired
            InvalidCredentialsException: If token is invalid
        """
        payload = self.decode_token(token)

        if payload.get("type") != "access":
            raise InvalidCredentialsException(message="Invalid token type")

        return payload

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a refresh token.

        Args:
            token: Refresh token

        Returns:
            Token payload

        Raises:
            TokenExpiredException: If token has expired
            InvalidCredentialsException: If token is invalid
        """
        payload = self.decode_token(token)

        if payload.get("type") != "refresh":
            raise InvalidCredentialsException(message="Invalid token type")

        return payload

    def get_token_expiry(self, token: str) -> datetime:
        """
        Get token expiry datetime.

        Args:
            token: JWT token

        Returns:
            Expiry datetime
        """
        payload = self.decode_token(token)
        return datetime.fromtimestamp(payload.get("exp", 0))

    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired.

        Args:
            token: JWT token

        Returns:
            True if expired
        """
        try:
            payload = self.decode_token(token)
            return False
        except TokenExpiredException:
            return True

    def create_password_reset_token(self, user_id: int, email: str) -> str:
        """
        Create a password reset token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            Password reset token
        """
        now = datetime.utcnow()
        expire = now + timedelta(hours=1)  # 1 hour validity

        claims = {
            "user_id": user_id,
            "email": email,
            "type": "password_reset",
            "iat": now,
            "exp": expire,
        }

        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def create_email_verification_token(self, user_id: int, email: str) -> str:
        """
        Create an email verification token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            Email verification token
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=7)  # 7 days validity

        claims = {
            "user_id": user_id,
            "email": email,
            "type": "email_verification",
            "iat": now,
            "exp": expire,
        }

        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)


# Singleton instance
jwt_handler = JWTHandler()
