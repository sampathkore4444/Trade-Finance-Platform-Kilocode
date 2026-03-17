"""
Audit Logger for Trade Finance Platform

This module handles audit logging for all system operations.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum


class AuditAction(str, Enum):
    """
    Enumeration of auditable actions.
    """

    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
    MFA_ENABLED = "MFA_ENABLED"
    MFA_DISABLED = "MFA_DISABLED"

    # User Management
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"

    # Letter of Credit
    LC_CREATED = "LC_CREATED"
    LC_UPDATED = "LC_UPDATED"
    LC_DELETED = "LC_DELETED"
    LC_APPROVED = "LC_APPROVED"
    LC_REJECTED = "LC_REJECTED"
    LC_AMENDED = "LC_AMENDED"
    LC_DOCUMENTS_RECEIVED = "LC_DOCUMENTS_RECEIVED"
    LC_PAYMENT_PROCESSED = "LC_PAYMENT_PROCESSED"
    LC_CLOSED = "LC_CLOSED"

    # Bank Guarantee
    GUARANTEE_CREATED = "GUARANTEE_CREATED"
    GUARANTEE_UPDATED = "GUARANTEE_UPDATED"
    GUARANTEE_APPROVED = "GUARANTEE_APPROVED"
    GUARANTEE_ISSUED = "GUARANTEE_ISSUED"
    GUARANTEE_CLAIMED = "GUARANTEE_CLAIMED"
    GUARANTEE_EXPIRED = "GUARANTEE_EXPIRED"

    # Trade Loan
    LOAN_CREATED = "LOAN_CREATED"
    LOAN_APPROVED = "LOAN_APPROVED"
    LOAN_REJECTED = "LOAN_REJECTED"
    LOAN_DISBURSED = "LOAN_DISBURSED"
    LOAN_REPAID = "LOAN_REPAID"
    LOAN_DEFAULTED = "LOAN_DEFAULTED"

    # Documents
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_DOWNLOADED = "DOCUMENT_DOWNLOADED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"

    # Compliance
    KYC_PERFORMED = "KYC_PERFORMED"
    SANCTIONS_SCREENED = "SANCTIONS_SCREENED"
    COMPLIANCE_ALERT = "COMPLIANCE_ALERT"

    # System
    CONFIG_CHANGED = "CONFIG_CHANGED"
    API_KEY_CREATED = "API_KEY_CREATED"
    API_KEY_REVOKED = "API_KEY_REVOKED"


class AuditLogger:
    """
    Handler for audit logging operations.
    """

    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def log(
        self,
        action: AuditAction,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS",
    ):
        """
        Log an audit event.

        Args:
            action: Action being audited
            user_id: ID of user performing action
            username: Username
            resource_type: Type of resource being accessed
            resource_id: ID of resource
            details: Additional details
            ip_address: Client IP address
            user_agent: Client user agent
            status: Operation status
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "user_id": user_id,
            "username": username,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status,
        }

        # Log as JSON
        self.logger.info(json.dumps(audit_entry))

        # TODO: Store in database for querying
        # TODO: Send to SIEM if critical

    def log_login(
        self,
        user_id: int,
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ):
        """
        Log authentication attempt.
        """
        action = AuditAction.LOGIN if success else AuditAction.LOGIN_FAILED
        details = {"failure_reason": failure_reason} if failure_reason else None

        self.log(
            action=action,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            details=details,
            status="SUCCESS" if success else "FAILED",
        )

    def log_transaction(
        self,
        action: AuditAction,
        user_id: int,
        username: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ):
        """
        Log transaction-related action.
        """
        self.log(
            action=action,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )

    def log_document_access(
        self,
        action: AuditAction,
        user_id: int,
        document_id: str,
        document_name: str,
        ip_address: Optional[str] = None,
    ):
        """
        Log document access.
        """
        self.log(
            action=action,
            user_id=user_id,
            resource_type="DOCUMENT",
            resource_id=document_id,
            details={"document_name": document_name},
            ip_address=ip_address,
        )

    def log_compliance_event(
        self,
        action: AuditAction,
        user_id: int,
        entity_type: str,
        entity_id: str,
        details: Dict[str, Any],
    ):
        """
        Log compliance-related event.
        """
        self.log(
            action=action,
            user_id=user_id,
            resource_type=entity_type,
            resource_id=entity_id,
            details=details,
            status="ALERT" if action == AuditAction.COMPLIANCE_ALERT else "SUCCESS",
        )

    def get_audit_trail(
        self,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail with filters.

        Note: This is a placeholder implementation.
        In production, this would query a database.
        """
        # TODO: Implement database query
        return []


# Singleton instance
audit_logger = AuditLogger()
