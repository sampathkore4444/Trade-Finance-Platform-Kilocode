"""
Event Repository
Handles database operations for events
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from ..models.event import Event, EventAccountingStatus, EventSubscription

logger = logging.getLogger(__name__)


class EventRepository:
    """Repository for event data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, event: Event) -> Event:
        """Create a new event"""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(Event.event_id == event_id).first()
    
    def get_by_correlation_id(self, correlation_id: str) -> List[Event]:
        """Get all events with the same correlation ID"""
        return self.db.query(Event).filter(
            Event.correlation_id == correlation_id
        ).order_by(Event.timestamp.asc()).all()
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        source_service: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """Query events with filters"""
        query = self.db.query(Event)
        
        filters = []
        
        if event_type:
            filters.append(Event.event_type == event_type)
        
        if correlation_id:
            filters.append(Event.correlation_id == correlation_id)
        
        if from_timestamp:
            filters.append(Event.timestamp >= from_timestamp)
        
        if to_timestamp:
            filters.append(Event.timestamp <= to_timestamp)
        
        if tenant_id:
            filters.append(Event.tenant_id == tenant_id)
        
        if source_service:
            filters.append(Event.source_service == source_service)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.order_by(desc(Event.timestamp)).limit(limit).offset(offset).all()
    
    def count(
        self,
        event_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        tenant_id: Optional[str] = None
    ) -> int:
        """Count events with filters"""
        query = self.db.query(Event)
        
        filters = []
        
        if event_type:
            filters.append(Event.event_type == event_type)
        
        if correlation_id:
            filters.append(Event.correlation_id == correlation_id)
        
        if from_timestamp:
            filters.append(Event.timestamp >= from_timestamp)
        
        if to_timestamp:
            filters.append(Event.timestamp <= to_timestamp)
        
        if tenant_id:
            filters.append(Event.tenant_id == tenant_id)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()
    
    def is_duplicate(self, event_hash: str) -> bool:
        """Check if event with same hash exists within time window"""
        if not event_hash:
            return False
        
        # Check for duplicate within 5 minutes
        time_window = datetime.utcnow()
        from_time = time_window.replace(minute=time_window.minute - 5)
        
        existing = self.db.query(Event).filter(
            and_(
                Event.event_hash == event_hash,
                Event.timestamp >= from_time
            )
        ).first()
        
        return existing is not None
    
    def get_uncharged_events(self) -> List[Event]:
        """Get events that haven't been charged/processed"""
        return self.db.query(Event).filter(
            Event.accounting_enabled == True
        ).order_by(Event.timestamp.asc()).all()
    
    # Accounting Status methods
    def get_accounting_status(self, event_id: UUID) -> Optional[EventAccountingStatus]:
        """Get accounting status for an event"""
        return self.db.query(EventAccountingStatus).filter(
            EventAccountingStatus.event_id == event_id
        ).first()
    
    def update_accounting_status(
        self,
        event_id: UUID,
        status: str,
        cbs_reference: Optional[str] = None,
        error_message: Optional[str] = None,
        increment_retry: bool = False
    ) -> Optional[EventAccountingStatus]:
        """Update accounting status"""
        status_record = self.get_accounting_status(event_id)
        
        if not status_record:
            logger.warning(f"No accounting status found for event {event_id}")
            return None
        
        status_record.status = status
        
        if cbs_reference:
            status_record.cbs_reference = cbs_reference
        
        if error_message:
            status_record.error_message = error_message
        
        if increment_retry:
            status_record.retry_count += 1
        
        status_record.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(status_record)
        
        return status_record
    
    def get_pending_accounting_events(
        self,
        limit: int = 100
    ) -> List[EventAccountingStatus]:
        """Get events pending accounting processing"""
        return self.db.query(EventAccountingStatus).filter(
            and_(
                EventAccountingStatus.status == "PENDING",
                EventAccountingStatus.retry_count < 3
            )
        ).order_by(EventAccountingStatus.created_at.asc()).limit(limit).all()
    
    # Subscription methods
    def create_subscription(
        self,
        subscription: EventSubscription
    ) -> EventSubscription:
        """Create event subscription"""
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def get_subscription(self, subscription_id: UUID) -> Optional[EventSubscription]:
        """Get subscription by ID"""
        return self.db.query(EventSubscription).filter(
            EventSubscription.subscription_id == subscription_id
        ).first()
    
    def get_active_subscriptions(
        self,
        event_type: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> List[EventSubscription]:
        """Get active subscriptions"""
        query = self.db.query(EventSubscription).filter(
            EventSubscription.is_active == True
        )
        
        if tenant_id:
            query = query.filter(
                or_(
                    EventSubscription.tenant_id == tenant_id,
                    EventSubscription.tenant_id == None
                )
            )
        
        subscriptions = query.all()
        
        # Filter by event type if specified
        if event_type:
            filtered = []
            for sub in subscriptions:
                if sub.event_types is None or event_type in sub.event_types:
                    filtered.append(sub)
            return filtered
        
        return subscriptions
    
    def update_subscription_delivery_stats(
        self,
        subscription_id: UUID,
        success: bool = True
    ) -> None:
        """Update delivery statistics"""
        subscription = self.get_subscription(subscription_id)
        
        if subscription:
            subscription.events_delivered += 1
            if success:
                subscription.last_delivered_at = datetime.utcnow()
            
            self.db.commit()
    
    def delete_subscription(self, subscription_id: UUID) -> bool:
        """Delete subscription"""
        subscription = self.get_subscription(subscription_id)
        
        if subscription:
            self.db.delete(subscription)
            self.db.commit()
            return True
        
        return False
