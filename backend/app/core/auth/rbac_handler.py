"""
Role-Based Access Control (RBAC) Handler for Trade Finance Platform

This module handles authorization based on roles and permissions.
"""

from typing import List, Dict, Set, Optional
from enum import Enum
from functools import wraps
from fastapi import HTTPException, status

from app.common.exceptions import InsufficientPermissionsException


class Permission(str, Enum):
    """
    Enumeration of all available permissions in the system.
    """

    # User Management
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Role Management
    ROLE_READ = "role:read"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"

    # Letter of Credit
    LC_READ = "lc:read"
    LC_CREATE = "lc:create"
    LC_UPDATE = "lc:update"
    LC_DELETE = "lc:delete"
    LC_APPROVE = "lc:approve"
    LC_AMEND = "lc:amend"
    LC_DOCUMENTS = "lc:documents"
    LC_PAYMENT = "lc:payment"

    # Bank Guarantee
    GUARANTEE_READ = "guarantee:read"
    GUARANTEE_CREATE = "guarantee:create"
    GUARANTEE_UPDATE = "guarantee:update"
    GUARANTEE_DELETE = "guarantee:delete"
    GUARANTEE_APPROVE = "guarantee:approve"
    GUARANTEE_CLAIM = "guarantee:claim"

    # Documentary Collection
    COLLECTION_READ = "collection:read"
    COLLECTION_CREATE = "collection:create"
    COLLECTION_UPDATE = "collection:update"
    COLLECTION_DISPATCH = "collection:dispatch"

    # Invoice Financing
    INVOICE_READ = "invoice:read"
    INVOICE_CREATE = "invoice:create"
    INVOICE_UPDATE = "invoice:update"
    INVOICE_FINANCE = "invoice:finance"

    # Trade Loan
    LOAN_READ = "loan:read"
    LOAN_CREATE = "loan:create"
    LOAN_UPDATE = "loan:update"
    LOAN_APPROVE = "loan:approve"
    LOAN_DISBURSE = "loan:disburse"
    LOAN_REPAY = "loan:repay"

    # Risk Management
    RISK_READ = "risk:read"
    RISK_ASSESS = "risk:assess"
    RISK_LIMIT = "risk:limit"

    # Compliance
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_KYC = "compliance:kyc"
    COMPLIANCE_SCREEN = "compliance:screen"
    COMPLIANCE_REPORT = "compliance:report"

    # Documents
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_DELETE = "document:delete"
    DOCUMENT_DOWNLOAD = "document:download"

    # Reports
    REPORT_READ = "report:read"
    REPORT_CREATE = "report:create"
    REPORT_EXPORT = "report:export"

    # Notifications
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_MANAGE = "notification:manage"

    # System
    SYSTEM_CONFIG = "system:config"
    SYSTEM_AUDIT = "system:audit"


# Role definitions with associated permissions
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    "system_admin": {
        # All permissions
        Permission.USER_READ,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.ROLE_READ,
        Permission.ROLE_CREATE,
        Permission.ROLE_UPDATE,
        Permission.ROLE_DELETE,
        Permission.LC_READ,
        Permission.LC_CREATE,
        Permission.LC_UPDATE,
        Permission.LC_DELETE,
        Permission.LC_APPROVE,
        Permission.LC_AMEND,
        Permission.LC_DOCUMENTS,
        Permission.LC_PAYMENT,
        Permission.GUARANTEE_READ,
        Permission.GUARANTEE_CREATE,
        Permission.GUARANTEE_UPDATE,
        Permission.GUARANTEE_DELETE,
        Permission.GUARANTEE_APPROVE,
        Permission.GUARANTEE_CLAIM,
        Permission.COLLECTION_READ,
        Permission.COLLECTION_CREATE,
        Permission.COLLECTION_UPDATE,
        Permission.COLLECTION_DISPATCH,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.INVOICE_UPDATE,
        Permission.INVOICE_FINANCE,
        Permission.LOAN_READ,
        Permission.LOAN_CREATE,
        Permission.LOAN_UPDATE,
        Permission.LOAN_APPROVE,
        Permission.LOAN_DISBURSE,
        Permission.LOAN_REPAY,
        Permission.RISK_READ,
        Permission.RISK_ASSESS,
        Permission.RISK_LIMIT,
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_KYC,
        Permission.COMPLIANCE_SCREEN,
        Permission.COMPLIANCE_REPORT,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DELETE,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.REPORT_READ,
        Permission.REPORT_CREATE,
        Permission.REPORT_EXPORT,
        Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_MANAGE,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_AUDIT,
    },
    "trade_finance_manager": {
        Permission.LC_READ,
        Permission.LC_CREATE,
        Permission.LC_UPDATE,
        Permission.LC_APPROVE,
        Permission.LC_AMEND,
        Permission.LC_DOCUMENTS,
        Permission.LC_PAYMENT,
        Permission.GUARANTEE_READ,
        Permission.GUARANTEE_CREATE,
        Permission.GUARANTEE_UPDATE,
        Permission.GUARANTEE_APPROVE,
        Permission.GUARANTEE_CLAIM,
        Permission.COLLECTION_READ,
        Permission.COLLECTION_CREATE,
        Permission.COLLECTION_UPDATE,
        Permission.COLLECTION_DISPATCH,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.INVOICE_FINANCE,
        Permission.LOAN_READ,
        Permission.LOAN_CREATE,
        Permission.LOAN_APPROVE,
        Permission.LOAN_DISBURSE,
        Permission.RISK_READ,
        Permission.RISK_ASSESS,
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_REPORT,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.REPORT_READ,
        Permission.REPORT_CREATE,
        Permission.REPORT_EXPORT,
        Permission.NOTIFICATION_READ,
    },
    "relationship_manager": {
        Permission.LC_READ,
        Permission.LC_CREATE,
        Permission.GUARANTEE_READ,
        Permission.GUARANTEE_CREATE,
        Permission.COLLECTION_READ,
        Permission.COLLECTION_CREATE,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.LOAN_READ,
        Permission.LOAN_CREATE,
        Permission.RISK_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.REPORT_READ,
        Permission.NOTIFICATION_READ,
    },
    "operations_officer": {
        Permission.LC_READ,
        Permission.LC_UPDATE,
        Permission.LC_DOCUMENTS,
        Permission.LC_PAYMENT,
        Permission.GUARANTEE_READ,
        Permission.GUARANTEE_UPDATE,
        Permission.COLLECTION_READ,
        Permission.COLLECTION_UPDATE,
        Permission.COLLECTION_DISPATCH,
        Permission.INVOICE_READ,
        Permission.INVOICE_UPDATE,
        Permission.LOAN_READ,
        Permission.LOAN_UPDATE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.NOTIFICATION_READ,
    },
    "credit_officer": {
        Permission.LC_READ,
        Permission.LC_APPROVE,
        Permission.GUARANTEE_READ,
        Permission.GUARANTEE_APPROVE,
        Permission.LOAN_READ,
        Permission.LOAN_CREATE,
        Permission.LOAN_APPROVE,
        Permission.RISK_READ,
        Permission.RISK_ASSESS,
        Permission.RISK_LIMIT,
        Permission.REPORT_READ,
        Permission.NOTIFICATION_READ,
    },
    "compliance_officer": {
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_KYC,
        Permission.COMPLIANCE_SCREEN,
        Permission.COMPLIANCE_REPORT,
        Permission.LC_READ,
        Permission.GUARANTEE_READ,
        Permission.LOAN_READ,
        Permission.RISK_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
        Permission.SYSTEM_AUDIT,
        Permission.NOTIFICATION_READ,
    },
    "auditor": {
        Permission.LC_READ,
        Permission.GUARANTEE_READ,
        Permission.COLLECTION_READ,
        Permission.INVOICE_READ,
        Permission.LOAN_READ,
        Permission.RISK_READ,
        Permission.COMPLIANCE_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
        Permission.SYSTEM_AUDIT,
    },
    "corporate_client": {
        Permission.LC_READ,
        Permission.LC_CREATE,
        Permission.GUARANTEE_READ,
        Permission.GUARANTEE_CREATE,
        Permission.COLLECTION_READ,
        Permission.COLLECTION_CREATE,
        Permission.INVOICE_READ,
        Permission.INVOICE_CREATE,
        Permission.LOAN_READ,
        Permission.LOAN_CREATE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DOWNLOAD,
        Permission.NOTIFICATION_READ,
    },
}


class RBACHandler:
    """
    Handler for Role-Based Access Control operations.
    """

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def get_role_permissions(self, role: str) -> Set[Permission]:
        """
        Get all permissions for a role.

        Args:
            role: Role name

        Returns:
            Set of permissions
        """
        return self.role_permissions.get(role, set())

    def get_user_permissions(self, roles: List[str]) -> Set[Permission]:
        """
        Get all permissions for a list of roles.

        Args:
            roles: List of role names

        Returns:
            Set of permissions
        """
        permissions = set()
        for role in roles:
            permissions.update(self.get_role_permissions(role))
        return permissions

    def has_permission(self, roles: List[str], permission: Permission) -> bool:
        """
        Check if user has a specific permission.

        Args:
            roles: List of user roles
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user_permissions = self.get_user_permissions(roles)
        return permission in user_permissions

    def has_any_permission(
        self, roles: List[str], permissions: List[Permission]
    ) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            roles: List of user roles
            permissions: List of permissions to check

        Returns:
            True if user has any permission
        """
        user_permissions = self.get_user_permissions(roles)
        return any(p in user_permissions for p in permissions)

    def has_all_permissions(
        self, roles: List[str], permissions: List[Permission]
    ) -> bool:
        """
        Check if user has all of the specified permissions.

        Args:
            roles: List of user roles
            permissions: List of permissions to check

        Returns:
            True if user has all permissions
        """
        user_permissions = self.get_user_permissions(roles)
        return all(p in user_permissions for p in permissions)

    def validate_role(self, role: str) -> bool:
        """
        Validate if a role exists.

        Args:
            role: Role name

        Returns:
            True if role exists
        """
        return role in self.role_permissions

    def get_all_roles(self) -> List[str]:
        """
        Get list of all available roles.

        Returns:
            List of role names
        """
        return list(self.role_permissions.keys())


def require_permissions(*permissions: Permission):
    """
    Decorator to require specific permissions for an endpoint.

    Usage:
        @require_permissions(Permission.LC_CREATE, Permission.LC_APPROVE)
        async def create_lc(...):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from request context
            request = kwargs.get("request")
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found",
                )

            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check permissions
            rbac = RBACHandler()
            user_roles = user.get("roles", [])

            if not rbac.has_all_permissions(user_roles, list(permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_roles(*roles: str):
    """
    Decorator to require specific roles for an endpoint.

    Usage:
        @require_roles("admin", "manager")
        async def some_endpoint(...):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found",
                )

            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            user_roles = user.get("roles", [])

            if not any(r in user_roles for r in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role privileges",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Singleton instance
rbac_handler = RBACHandler()
