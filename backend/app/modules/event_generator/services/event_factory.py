"""
Event Factory
Creates properly formatted events with appropriate metadata
"""

import uuid
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from ..models.event import Event, EventSource, EventMetadata, AccountingEntry


class EventFactory:
    """Factory for creating events"""
    
    def __init__(self):
        self.default_version = "1.0"
    
    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source_service: str,
        source_actor: str = "system",
        source_actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        accounting_entries: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None
    ) -> Event:
        """
        Create a new event with all required fields
        
        Args:
            event_type: Type of the event
            payload: Event payload data
            source_service: Service that generated the event
            source_actor: Type of actor (user, system, external)
            source_actor_id: ID of the actor
            correlation_id: Correlation ID for tracking
            causation_id: Causation event ID
            metadata: Additional metadata
            accounting_entries: Accounting entries for CBS
            tenant_id: Tenant identifier
        
        Returns:
            Event object
        """
        event_id = uuid.uuid4()
        timestamp = datetime.utcnow()
        
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = f"corr_{event_id.hex[:12]}"
        
        # Build source
        source = {
            "service": source_service,
            "actor": source_actor,
            "actor_id": source_actor_id
        }
        
        # Build metadata
        event_metadata = metadata or {}
        if tenant_id:
            event_metadata["tenantId"] = tenant_id
        
        # Check if accounting is enabled
        accounting_enabled = accounting_entries is not None and len(accounting_entries) > 0
        
        # Compute event hash for deduplication
        event_hash = self._compute_event_hash(event_type, payload, source)
        
        # Create event
        event = Event(
            event_id=event_id,
            event_type=event_type,
            event_version=self.default_version,
            timestamp=timestamp,
            correlation_id=correlation_id,
            causation_id=causation_id,
            source_service=source_service,
            source_actor=source_actor,
            source_actor_id=source_actor_id,
            payload=payload,
            metadata=event_metadata if event_metadata else None,
            accounting_enabled=accounting_enabled,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id,
            event_hash=event_hash
        )
        
        return event
    
    def create_lc_event(
        self,
        event_type: str,
        lc_data: Dict[str, Any],
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[UUID] = None,
        accounting_entries: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None
    ) -> Event:
        """Create a Letter of Credit event"""
        payload = {
            "lcReference": lc_data.get("reference"),
            "lcId": lc_data.get("id"),
            "applicantPartyId": lc_data.get("applicant_party_id"),
            "beneficiaryPartyId": lc_data.get("beneficiary_party_id"),
            "lcType": lc_data.get("type"),
            "currency": lc_data.get("currency"),
            "amount": str(lc_data.get("amount")),
            "expiryDate": lc_data.get("expiry_date"),
            "issueDate": lc_data.get("issue_date"),
            "issuingBank": lc_data.get("issuing_bank")
        }
        
        return self.create_event(
            event_type=event_type,
            payload=payload,
            source_service="lc_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id
        )
    
    def create_guarantee_event(
        self,
        event_type: str,
        guarantee_data: Dict[str, Any],
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[UUID] = None,
        accounting_entries: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None
    ) -> Event:
        """Create a Guarantee/Bond event"""
        payload = {
            "guaranteeReference": guarantee_data.get("reference"),
            "guaranteeId": guarantee_data.get("id"),
            "applicantPartyId": guarantee_data.get("applicant_party_id"),
            "beneficiaryPartyId": guarantee_data.get("beneficiary_party_id"),
            "guaranteeType": guarantee_data.get("type"),
            "currency": guarantee_data.get("currency"),
            "amount": str(guarantee_data.get("amount")),
            "expiryDate": guarantee_data.get("expiry_date"),
            "issueDate": guarantee_data.get("issue_date"),
            "issuingBank": guarantee_data.get("issuing_bank")
        }
        
        return self.create_event(
            event_type=event_type,
            payload=payload,
            source_service="guarantee_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id
        )
    
    def create_trade_loan_event(
        self,
        event_type: str,
        loan_data: Dict[str, Any],
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[UUID] = None,
        accounting_entries: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None
    ) -> Event:
        """Create a Trade Loan event"""
        payload = {
            "loanReference": loan_data.get("reference"),
            "loanId": loan_data.get("id"),
            "borrowerPartyId": loan_data.get("borrower_party_id"),
            "loanType": loan_data.get("type"),
            "currency": loan_data.get("currency"),
            "amount": str(loan_data.get("amount")),
            "disbursementDate": loan_data.get("disbursement_date"),
            "maturityDate": loan_data.get("maturity_date"),
            "lendingBank": loan_data.get("lending_bank")
        }
        
        return self.create_event(
            event_type=event_type,
            payload=payload,
            source_service="trade_loan_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id
        )
    
    def create_document_event(
        self,
        event_type: str,
        document_data: Dict[str, Any],
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[UUID] = None,
        tenant_id: Optional[str] = None
    ) -> Event:
        """Create a Document event"""
        payload = {
            "documentId": document_data.get("id"),
            "documentReference": document_data.get("reference"),
            "documentType": document_data.get("type"),
            "documentName": document_data.get("name"),
            "lcReference": document_data.get("lc_reference"),
            "guaranteeReference": document_data.get("guarantee_reference"),
            "uploadedBy": document_data.get("uploaded_by"),
            "verificationStatus": document_data.get("verification_status")
        }
        
        return self.create_event(
            event_type=event_type,
            payload=payload,
            source_service="document_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            tenant_id=tenant_id
        )
    
    def create_party_event(
        self,
        event_type: str,
        party_data: Dict[str, Any],
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[UUID] = None,
        tenant_id: Optional[str] = None
    ) -> Event:
        """Create a Party event"""
        payload = {
            "partyId": party_data.get("id"),
            "partyReference": party_data.get("reference"),
            "partyName": party_data.get("name"),
            "partyType": party_data.get("type"),
            "kycStatus": party_data.get("kyc_status"),
            "riskRating": party_data.get("risk_rating"),
            "previousRiskRating": party_data.get("previous_risk_rating")
        }
        
        return self.create_event(
            event_type=event_type,
            payload=payload,
            source_service="party_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            tenant_id=tenant_id
        )
    
    def _compute_event_hash(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: Dict[str, Any]
    ) -> str:
        """Compute hash for deduplication"""
        content = f"{event_type}:{json.dumps(payload, sort_keys=True)}:{json.dumps(source, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def generate_idempotency_key(
        self,
        event_type: str,
        entity_id: str,
        action: str
    ) -> str:
        """Generate idempotency key"""
        return f"idemp_{event_type}_{entity_id}_{action}"
