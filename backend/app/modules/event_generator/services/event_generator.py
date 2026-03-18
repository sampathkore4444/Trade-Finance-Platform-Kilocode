"""
Event Generator Service
Main service for generating, validating, and publishing events
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from .event_factory import EventFactory
from .event_repository import EventRepository
from .event_publisher import EventPublisher
from ..models.event import Event, EventAccountingStatus, AccountingStatus

logger = logging.getLogger(__name__)


class EventGenerator:
    """
    Main event generator service
    Handles event creation, validation, persistence, and publishing
    """
    
    # Events that should trigger accounting entries
    ACCOUNTING_EVENTS = {
        "LC_ISSUED",
        "LC_UTILISED",
        "LC_SETTLED",
        "LC_EXPIRED",
        "GUARANTEE_ISSUED",
        "GUARANTEE_CLAIMED",
        "GUARANTEE_PAID",
        "GUARANTEE_RELEASED",
        "TRADE_LOAN_DISBURSED",
        "TRADE_LOAN_REPAID",
        "TRADE_LOAN_DEFAULTED",
    }
    
    def __init__(
        self,
        db: Session,
        event_factory: Optional[EventFactory] = None,
        event_repository: Optional[EventRepository] = None,
        event_publisher: Optional[EventPublisher] = None
    ):
        self.db = db
        self.event_factory = event_factory or EventFactory()
        self.event_repository = event_repository or EventRepository(db)
        self.event_publisher = event_publisher
    
    def generate_event(
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
        tenant_id: Optional[str] = None,
        skip_persistence: bool = False,
        skip_publishing: bool = False
    ) -> Event:
        """
        Generate and process an event
        
        Args:
            event_type: Type of event
            payload: Event data
            source_service: Service generating the event
            source_actor: Actor type
            source_actor_id: Actor ID
            correlation_id: Correlation ID
            causation_id: Causation event ID
            metadata: Additional metadata
            accounting_entries: Accounting entries for CBS
            tenant_id: Tenant ID
            skip_persistence: Skip saving to database
            skip_publishing: Skip publishing to message queue
        
        Returns:
            Created Event
        """
        logger.info(f"Generating event: {event_type}")
        
        # Create event
        event = self.event_factory.create_event(
            event_type=event_type,
            payload=payload,
            source_service=source_service,
            source_actor=source_actor,
            source_actor_id=source_actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            metadata=metadata,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id
        )
        
        # Check for duplicates
        if self.event_repository.is_duplicate(event.event_hash):
            logger.warning(f"Duplicate event detected: {event.event_id}")
            raise ValueError(f"Duplicate event detected")
        
        # Validate event
        self._validate_event(event)
        
        # Persist event
        if not skip_persistence:
            event = self.event_repository.create(event)
            logger.info(f"Event persisted: {event.event_id}")
            
            # Create accounting status record if needed
            if event.accounting_enabled:
                self._create_accounting_status(event)
        
        # Publish event
        if not skip_publishing and self.event_publisher:
            try:
                self.event_publisher.publish(event)
                logger.info(f"Event published: {event.event_id}")
            except Exception as e:
                logger.error(f"Failed to publish event {event.event_id}: {str(e)}")
                # Don't raise - event is already persisted
        
        return event
    
    def generate_lc_event(
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
        """Generate a Letter of Credit event"""
        return self.generate_event(
            event_type=event_type,
            payload={},
            source_service="lc_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id,
            skip_persistence=False,
            skip_publishing=False
        )
    
    def generate_guarantee_event(
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
        """Generate a Guarantee event"""
        return self.generate_event(
            event_type=event_type,
            payload={},
            source_service="guarantee_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id
        )
    
    def generate_trade_loan_event(
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
        """Generate a Trade Loan event"""
        return self.generate_event(
            event_type=event_type,
            payload={},
            source_service="trade_loan_service",
            source_actor=actor,
            source_actor_id=actor_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            accounting_entries=accounting_entries,
            tenant_id=tenant_id
        )
    
    def _validate_event(self, event: Event) -> None:
        """Validate event data"""
        if not event.event_type:
            raise ValueError("Event type is required")
        
        if not event.payload:
            logger.warning(f"Event {event.event_id} has empty payload")
        
        # Check if accounting is required but not provided
        if event.event_type in self.ACCOUNTING_EVENTS and not event.accounting_enabled:
            logger.warning(
                f"Event {event.event_type} requires accounting but no entries provided"
            )
    
    def _create_accounting_status(self, event: Event) -> EventAccountingStatus:
        """Create accounting status record"""
        status = EventAccountingStatus(
            event_id=event.event_id,
            event_type=event.event_type,
            accounting_enabled=event.accounting_enabled,
            status=AccountingStatus.PENDING.value,
            entry_count=len(event.accounting_entries) if event.accounting_entries else 0
        )
        
        self.db.add(status)
        self.db.commit()
        
        return status
    
    def replay_events(
        self,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Event]:
        """
        Replay events for recovery or reprocessing
        """
        events = self.event_repository.get_events(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            event_types=event_types
        )
        
        if not self.event_publisher:
            raise ValueError("Event publisher not configured")
        
        republished = []
        for event in events:
            try:
                self.event_publisher.publish(event)
                republished.append(event)
            except Exception as e:
                logger.error(f"Failed to republish event {event.event_id}: {str(e)}")
        
        return republished
