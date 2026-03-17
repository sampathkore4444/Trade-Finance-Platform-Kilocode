"""
Encryption Utilities for Trade Finance Platform

This module handles encryption and decryption of sensitive data.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from typing import Optional
from app.config import settings


class Encryption:
    """
    Handler for encryption operations using AES-256.
    """

    def __init__(self, key: Optional[bytes] = None):
        if key:
            self.fernet = Fernet(key)
        else:
            # Generate a key from a master password
            self.fernet = self._generate_fernet()

    def _generate_fernet(self) -> Fernet:
        """
        Generate a Fernet key from environment variable or random.
        """
        # Use a secret key from settings or generate random
        secret = settings.SECRET_KEY.encode() if settings.SECRET_KEY else os.urandom(32)

        # Derive a key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"trade_finance_salt",  # In production, use unique salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret))

        return Fernet(key)

    def encrypt(self, data: str) -> str:
        """
        Encrypt a string.

        Args:
            data: Plain text data

        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return ""

        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data.

        Args:
            encrypted_data: Encrypted string (base64 encoded)

        Returns:
            Decrypted plain text
        """
        if not encrypted_data:
            return ""

        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            raise ValueError("Failed to decrypt data")

    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt specific sensitive fields in a dictionary.

        Args:
            data: Dictionary with sensitive fields

        Returns:
            Dictionary with encrypted sensitive fields
        """
        sensitive_fields = [
            "national_id",
            "passport_number",
            "tax_id",
            "account_number",
            "iban",
            "credit_card",
        ]

        encrypted_data = data.copy()

        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))

        return encrypted_data

    def decrypt_dict(self, data: dict) -> dict:
        """
        Decrypt specific sensitive fields in a dictionary.

        Args:
            data: Dictionary with encrypted fields

        Returns:
            Dictionary with decrypted sensitive fields
        """
        sensitive_fields = [
            "national_id",
            "passport_number",
            "tax_id",
            "account_number",
            "iban",
            "credit_card",
        ]

        decrypted_data = data.copy()

        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(str(decrypted_data[field]))
                except ValueError:
                    # Keep original if decryption fails
                    pass

        return decrypted_data

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key.

        Returns:
            Base64 encoded key
        """
        return Fernet.generate_key().decode()


# Singleton instance
encryption = Encryption()
