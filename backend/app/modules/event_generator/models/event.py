"""
Event Models for Trade Finance Platform
This module defines the core event structures used across the platform.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Import Base from core database
from app.core.database import Base


class EventType(str, Enum):
    """Trade Finance Event Types"""
    # Letter of Credit Events
    LC_CREATED = "LC_CREATED"
    LC_AMENDED = "LC_AMENDED"
    LC_APPROVED = "LC_APPROVED"
    LC_ISSUED = "LC_ISSUED"
    LC_AMENDED_AFTER_ISSUE = "LC_AMENDED_AFTER_ISSUE"
    LC_UTILISED = "LC_UTILISED"
    LC_SETTLED = "LC_SETTLED"
    LC_EXPIRED = "LC_EXPIRED"
    LC_TERMINATED = "LC_TERMINATED"
    
    # Guarantee/Bond Events
    GUARANTEE_CREATED = "GUARANTEE_CREATED"
    GUARANTEE_ISSUED = "GUARANTEE_ISSUED"
    GUARANTEE_CLAIMED = "GUARANTEE_CLAIMED"
    GUARANTEE_PAID = "GUARANTEE_PAID"
    GUARANTEE_RELEASED = "GUARANTEE_RELEASED"
    
    # Trade Loan Events
    TRADE_LOAN_DISBURSED = "TRADE_LOAN_DISBURSED"
    TRADE_LOAN_REPAID = "TRADE_LOAN_REPAID"
    TRADE_LOAN_DEFAULTED = "TRADE_LOAN_DEFAULTED"
    TRADE_LOAN_RESTUCTURED = "TRADE_LOAN_RESTUCTURED"
    
    # Documentary Collection Events
    COLLECTION_CREATED = "COLLECTION_CREATED"
    COLLECTION_SENT = "COLLECTION_SENT"
    COLLECTION_RECEIVED = "COLLECTION_RECEIVED"
    COLLECTION_ACCEPTED = "COLLECTION_ACCEPTED"
    COLLECTION_REJECTED = "COLLECTION_REJECTED"
    COLLECTION_PAID = "COLLECTION_PAID"
    
    # Invoice Financing Events
    INVOICE_CREATED = "INVOICE_CREATED"
    INVOICE_FINANCED = "INVOICE_FINANCED"
    INVOICE_REPAID = "INVOICE_REPAID"
    INVOICE_DEFAULTED = "INVOICE_DEFAULTED"
    
    # Document Events
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_VERIFIED = "DOCUMENT_VERIFIED"
    DOCUMENT_REJECTED = "DOCUMENT_REJECTED"
    DOCUMENT_RELEASED = "DOCUMENT_RELEASED"
    
    # Party Events
    PARTY_ONBOARDED = "PARTY_ONBOARDED"
    PARTY_KYC_UPDATED = "PARTY_KYC_UPDATED"
    PARTY_RISK_RATING_CHANGED = "PARTY_RISK_RATING_CHANGED"


class ActorType(str, Enum):
    """Event actor types"""
    USER = "user"
    SYSTEM = "system"
    EXTERNAL = "external"


class AccountingStatus(str, Enum):
    """Accounting entry status"""
    PENDING = "PENDING"
    POSTED = "POSTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class EventSource:
    """Event source information"""
    def __init__(
        self,
        service: str,
        actor: str,
        actor_id: Optional[str] = None
    ):
        self.service = service
        self.actor = actor
        self.actor_id = actor_id
    
    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "actor": self.actor,
            "actor_id": self.actor_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventSource":
        return cls(
            service=data.get("service", ""),
            actor=data.get("actor", "system"),
            actor_id=data.get("actor_id")
        )


class EventMetadata:
    """Event metadata"""
    def __init__(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = span_id
        self.tenant_id = tenant_id
        self.extra = kwargs
    
    def to_dict(self) -> dict:
        result = {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "tenantId": self.tenant_id
        }
        result.update(self.extra)
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventMetadata":
        if not data:
            return cls()
        known_fields = {"traceId", "spanId", "tenantId"}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        return cls(
            trace_id=data.get("traceId"),
            span_id=data.get("spanId"),
            tenant_id=data.get("tenantId"),
            **extra
        )


class AccountingEntry:
    """Accounting entry for Core Banking System"""
    def __init__(
        self,
        entry_type: str,
        debit_account: Optional[dict] = None,
        credit_account: Optional[dict] = None,
        amount: str = "0",
        currency: str = "USD",
        narrative: str = "",
        value_date: Optional[str] = None
    ):
        self.entry_type = entry_type
        self.debit_account = debit_account
        self.credit_account = credit_account
        self.amount = amount
        self.currency = currency
        self.narrative = narrative
        self.value_date = value_date
    
    def to_dict(self) -> dict:
        return {
            "entryType": self.entry_type,
            "debitAccount": self.debit_account,
            "creditAccount": self.credit_account,
            "amount": self.amount,
            "currency": self.currency,
            "narrative": self.narrative,
            "valueDate": self.value_date
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AccountingEntry":
        return cls(
            entry_type=data.get("entryType", ""),
            debit_account=data.get("debitAccount"),
            credit_account=data.get("creditAccount"),
            amount=data.get("amount", "0"),
            currency=data.get("currency", "USD"),
            narrative=data.get("narrative", ""),
            value_date=data.get("valueDate")
        )


class Event(Base):
    """Event model for storing events in the database"""
    __tablename__ = "events"
    
    # Primary key
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_type = Column(String(100), nullable=False, index=True)
    event_version = Column(String(20), nullable=False, default="1.0")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Correlation and causation
    correlation_id = Column(String(50), nullable=True, index=True)
    causation_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Source information
    source_service = Column(String(100), nullable=False)
    source_actor = Column(String(50), nullable=False)  # user, system, external
    source_actor_id = Column(String(100), nullable=True)
    
    # Payload and metadata
    payload = Column(JSONB, nullable=False)
    metadata = Column(JSONB, nullable=True)
    
    # Accounting information
    accounting_enabled = Column(Boolean, default=False)
    accounting_entries = Column(JSONB, nullable=True)
    
    # Tenant
    tenant_id = Column(String(50), nullable=True, index=True)
    
    # Hash for deduplication
    event_hash = Column(String(64), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_events_type_timestamp', 'event_type', 'timestamp'),
        Index('idx_events_correlation_timestamp', 'correlation_id', 'timestamp'),
        Index('idx_events_payload_gin', 'payload', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<Event {self.event_type} {self.event_id}>"
    
    def to_dict(self) -> dict:
        return {
            "eventId": str(self.event_id),
            "eventType": self.event_type,
            "eventVersion": self.event_version,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "correlationId": self.correlation_id,
            "causationId": str(self.causation_id) if self.causation_id else None,
            "source": {
                "service": self.source_service,
                "actor": self.source_actor,
                "actorId": self.source_actor_id
            },
            "payload": self.payload,
            "metadata": self.metadata,
            "accounting": {
                "enabled": self.accounting_enabled,
                "entries": self.accounting_entries
            } if self.accounting_enabled else None,
            "metadata_extended": {
                "tenantId": self.tenant_id,
                "eventHash": self.event_hash
            }
        }


class EventAccountingStatus(Base):
    """Track accounting status for each event"""
    __tablename__ = "event_accounting_status"
    
    # Primary key
    event_id = Column(UUID(as_uuid=True), primary=True)
    
    # Event info
    event_type = Column(String(100), nullable=False)
    
    # Accounting status
    accounting_enabled = Column(Boolean, default=True)
    status = Column(String(20), nullable=False, default=AccountingStatus.PENDING.value)
    cbs_reference = Column(String(50), nullable=True)
    entry_count = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_accounting_status_retry', 'status', 'retry_count'),
    )


class EventSubscription(Base):
    """Event subscription for external consumers"""
    __tablename__ = "event_subscriptions"
    
    # Primary key
    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Subscription details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Filter criteria
    event_types = Column(JSONB, nullable=True)  # List of event types to subscribe to
    tenant_id = Column(String(50), nullable=True)
    
    # Delivery configuration
    delivery_type = Column(String(20), nullable=False)  # webhook, queue, email
    endpoint = Column(String(500), nullable=True)  # URL for webhook
    queue_name = Column(String(100), nullable=True)  # Queue name
    
    # Webhook specific
    webhook_secret = Column(String(255), nullable=True)
    webhook_format = Column(String(20), default="json")  # json, xml
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Delivery stats
    events_delivered = Column(Integer, default=0)
    last_delivered_at = Column(DateTime(timezone=True), nullable=True)
