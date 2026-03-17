"""
Invoice Financing Schemas Package
"""

from app.modules.invoice_financing.schemas.invoice import (
    InvoiceFinancingBase,
    InvoiceFinancingCreate,
    InvoiceFinancingUpdate,
    InvoiceFinancingResponse,
    InvoiceFinancingListResponse,
    InvoiceStatusEnum,
    FinancingStatusEnum,
)

# Alias for backward compatibility
InvoiceStatus = InvoiceStatusEnum

__all__ = [
    "InvoiceFinancingBase",
    "InvoiceFinancingCreate",
    "InvoiceFinancingUpdate",
    "InvoiceFinancingResponse",
    "InvoiceFinancingListResponse",
    "InvoiceStatusEnum",
    "FinancingStatusEnum",
    "InvoiceStatus",
]
