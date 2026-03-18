"""
Event Generator Schemas
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ActorType(str, Enum):
    """Event actor types"""
    USER = "user"
    SYSTEM = "system"
    EXTERNAL = "external"


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


class AccountingStatus(str, Enum):
    """Accounting status"""
    PENDING = "PENDING"
    POSTED = "POSTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Source Schema
class EventSourceSchema(BaseModel):
    """Event source information"""
    service: str = Field(..., description="Service that generated the event")
    actor: ActorType = Field(default=ActorType.SYSTEM, description="Type of actor")
    actor_id: Optional[str] = Field(None, description="ID of the actor")
    
    model_config = ConfigDict(from_attributes=True)


# Metadata Schema
class EventMetadataSchema(BaseModel):
    """Event metadata"""
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    span_id: Optional[str] = Field(None, description="Span ID for tracing")
    tenant_id: Optional[str] = Field(None, description="Tenant identifier")
    
    model_config = ConfigDict(from_attributes=True)


# Account Schema
class AccountSchema(BaseModel):
    """GL Account information"""
    type: str = Field(..., description="Account type: GL, NOSTRO, VOSTRO, DORMANT")
    account_code: Optional[str] = Field(None, description="GL account code")
    branch_code: Optional[str] = Field(None, description="Branch code")
    currency: Optional[str] = Field(None, description="Currency code")
    party_id: Optional[str] = Field(None, description="Party ID for dormant accounts")
    
    model_config = ConfigDict(from_attributes=True)


# Accounting Entry Schema
class AccountingEntrySchema(BaseModel):
    """Accounting entry for CBS"""
    entry_type: str = Field(..., description="Type of accounting entry")
    debit_account: Optional[AccountSchema] = Field(None, description="Debit account")
    credit_account: Optional[AccountSchema] = Field(None, description="Credit account")
    amount: str = Field(default="0", description="Entry amount")
    currency: str = Field(default="USD", description="Currency code")
    narrative: str = Field(default="", description="Entry narrative")
    value_date: Optional[str] = Field(None, description="Value date")
    
    model_config = ConfigDict(from_attributes=True)


# Accounting Schema
class AccountingSchema(BaseModel):
    """Accounting section in event"""
    enabled: bool = Field(default=False, description="Whether accounting is enabled")
    entries: List[AccountingEntrySchema] = Field(default_factory=list, description="Accounting entries")
    
    model_config = ConfigDict(from_attributes=True)


# Event Create Schema
class EventCreate(BaseModel):
    """Schema for creating an event"""
    event_type: EventType = Field(..., description="Type of event")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")
    causation_id: Optional[UUID] = Field(None, description="Causation event ID")
    
    source: EventSourceSchema = Field(..., description="Event source")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    metadata: Optional[EventMetadataSchema] = Field(None, description="Event metadata")
    
    accounting: Optional[AccountingSchema] = Field(None, description="Accounting entries")
    tenant_id: Optional[str] = Field(None, description="Tenant identifier")
    
    model_config = ConfigDict(from_attributes=True)


# Event Response Schema
class EventResponse(BaseModel):
    """Schema for event response"""
    event_id: UUID
    event_type: str
    event_version: str
    timestamp: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[UUID] = None
    
    source: EventSourceSchema
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    accounting_enabled: bool = False
    accounting_entries: Optional[List[Dict[str, Any]]] = None
    
    tenant_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Event List Response
class EventListResponse(BaseModel):
    """Schema for paginated event list"""
    events: List[EventResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Event Query Parameters
class EventQueryParams(BaseModel):
    """Query parameters for events"""
    event_type: Optional[EventType] = None
    correlation_id: Optional[str] = None
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    tenant_id: Optional[str] = None
    source_service: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


# Accounting Status Response
class EventAccountingStatusResponse(BaseModel):
    """Schema for accounting status response"""
    event_id: UUID
    event_type: str
    accounting_enabled: bool
    status: AccountingStatus
    cbs_reference: Optional[str] = None
    entry_count: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Delivery Type
class DeliveryType(str, Enum):
    """Event delivery types"""
    WEBHOOK = "webhook"
    QUEUE = "queue"
    EMAIL = "email"


# Event Subscription Create
class EventSubscriptionCreate(BaseModel):
    """Schema for creating event subscription"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    
    event_types: Optional[List[EventType]] = Field(None, description="Event types to subscribe")
    tenant_id: Optional[str] = None
    
    delivery_type: DeliveryType = Field(..., description="Delivery mechanism")
    endpoint: Optional[str] = Field(None, description="Webhook URL")
    queue_name: Optional[str] = Field(None, description="Queue name")
    
    webhook_secret: Optional[str] = None
    webhook_format: str = Field(default="json")
    
    is_active: bool = Field(default=True)
    
    model_config = ConfigDict(from_attributes=True)


# Event Subscription Response
class EventSubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    subscription_id: UUID
    name: str
    description: Optional[str] = None
    
    event_types: Optional[List[str]] = None
    tenant_id: Optional[str] = None
    
    delivery_type: str
    endpoint: Optional[str] = None
    queue_name: Optional[str] = None
    
    is_active: bool
    events_delivered: int = 0
    last_delivered_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Health Check Response
class EventHealthResponse(BaseModel):
    """Health check response for event system"""
    status: str
    event_store: str
    message_queue: str
    event_generator: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
