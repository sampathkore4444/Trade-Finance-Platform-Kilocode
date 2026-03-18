"""
Accounting Event Subscriber
Consumes events and posts accounting entries to Core Banking System
"""

import logging
import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

import httpx

from .event_repository import EventRepository
from .accounting_mapper import AccountingMapper, GLAccountConfig

logger = logging.getLogger(__name__)


class AccountingStatus(str, Enum):
    """Accounting processing status"""
    PENDING = "PENDING"
    POSTED = "POSTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class CoreBankingClient:
    """
    Client for Core Banking System API
    """
    
    def __init__(
        self,
        base_url: str,
        auth_token: str,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def post_accounting_entries(
        self,
        entries: List[Dict[str, Any]],
        event_id: str,
        idempotency_key: str,
        narrative: str = ""
    ) -> Dict[str, Any]:
        """
        Post accounting entries to CBS
        
        Args:
            entries: List of accounting entries
            event_id: Event ID
            idempotency_key: Idempotency key
            narrative: Transaction narrative
        
        Returns:
            CBS response with reference
        """
        payload = {
            "idempotencyKey": idempotency_key,
            "eventId": event_id,
            "narrative": narrative,
            "entries": entries
        }
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/accounting/entries",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Accounting entries posted successfully: {result.get('reference')}")
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to post accounting entries: {str(e)}")
            raise
    
    def get_entry_status(self, reference: str) -> Dict[str, Any]:
        """Get status of posted entries"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/accounting/entries/{reference}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get entry status: {str(e)}")
            raise
    
    def close(self):
        """Close HTTP client"""
        self.client.close()


class AccountingEventSubscriber:
    """
    Subscriber that processes events with accounting entries
    and posts them to the Core Banking System
    """
    
    # Event types that require accounting
    ACCOUNTING_EVENT_TYPES = {
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
        db,
        cbs_client: Optional[CoreBankingClient] = None,
        accounting_mapper: Optional[AccountingMapper] = None,
        event_repository: Optional[EventRepository] = None
    ):
        self.db = db
        self.cbs_client = cbs_client
        self.accounting_mapper = accounting_mapper or AccountingMapper()
        self.event_repository = event_repository or EventRepository(db)
        
        # Track processed events for deduplication
        self._processed_events = set()
    
    def process_event(self, event) -> bool:
        """
        Process an event for accounting
        
        Args:
            event: Event to process
        
        Returns:
            True if processed successfully
        """
        # Check if event requires accounting
        if event.event_type not in self.ACCOUNTING_EVENT_TYPES:
            logger.debug(f"Event {event.event_type} does not require accounting")
            return True
        
        # Check if accounting is enabled for this event
        if not event.accounting_enabled:
            logger.info(f"Accounting not enabled for event {event.event_id}")
            self._update_status(event.event_id, AccountingStatus.SKIPPED)
            return True
        
        # Check for duplicate processing
        if str(event.event_id) in self._processed_events:
            logger.warning(f"Event {event.event_id} already processed")
            return True
        
        try:
            # Map event to accounting entries
            entries = self.accounting_mapper.map_to_entries(event)
            
            if not entries:
                logger.warning(f"No accounting entries generated for event {event.event_id}")
                self._update_status(event.event_id, AccountingStatus.SKIPPED)
                return True
            
            # Post to CBS
            if self.cbs_client:
                idempotency_key = self.accounting_mapper.get_idempotency_key(event)
                
                result = self.cbs_client.post_accounting_entries(
                    entries=entries,
                    event_id=str(event.event_id),
                    idempotency_key=idempotency_key,
                    narrative=f"Trade Finance Event: {event.event_type}"
                )
                
                cbs_reference = result.get("reference")
            else:
                # Mock response for testing
                cbs_reference = f"MOCK_{event.event_id.hex[:8]}"
                logger.warning(f"No CBS client configured, using mock reference: {cbs_reference}")
            
            # Update status
            self._update_status(
                event.event_id,
                AccountingStatus.POSTED,
                cbs_reference=cbs_reference
            )
            
            # Mark as processed
            self._processed_events.add(str(event.event_id))
            
            logger.info(f"Event {event.event_id} accounting posted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {str(e)}")
            self._update_status(
                event.event_id,
                AccountingStatus.FAILED,
                error_message=str(e)
            )
            return False
    
    def process_pending_events(self, limit: int = 100) -> Dict[str, int]:
        """
        Process all pending events
        
        Args:
            limit: Maximum events to process
        
        Returns:
            Processing statistics
        """
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Get events with accounting enabled that are pending
        pending_statuses = self.event_repository.get_pending_accounting_events(limit=limit)
        
        for status_record in pending_statuses:
            event = self.event_repository.get_by_id(status_record.event_id)
            
            if not event:
                logger.warning(f"Event {status_record.event_id} not found")
                continue
            
            stats["total"] += 1
            
            if self.process_event(event):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        logger.info(f"Processed {stats['total']} events: {stats['success']} success, {stats['failed']} failed")
        return stats
    
    def retry_failed_events(self, max_retries: int = 3) -> Dict[str, int]:
        """Retry failed events"""
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0
        }
        
        # Get failed events that haven't exceeded retry limit
        from ..models.event import EventAccountingStatus
        failed_events = self.db.query(EventAccountingStatus).filter(
            EventAccountingStatus.status == AccountingStatus.FAILED.value,
            EventAccountingStatus.retry_count < max_retries
        ).all()
        
        for status_record in failed_events:
            event = self.event_repository.get_by_id(status_record.event_id)
            
            if not event:
                continue
            
            stats["total"] += 1
            
            if self.process_event(event):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        return stats
    
    def _update_status(
        self,
        event_id: UUID,
        status: AccountingStatus,
        cbs_reference: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update accounting status in database"""
        self.event_repository.update_accounting_status(
            event_id=event_id,
            status=status.value,
            cbs_reference=cbs_reference,
            error_message=error_message,
            increment_retry=(status == AccountingStatus.FAILED)
        )


class MockAccountingSubscriber(AccountingEventSubscriber):
    """Mock subscriber for testing"""
    
    def __init__(self, db):
        super().__init__(db, cbs_client=None)
        self.posted_entries = []
    
    def process_event(self, event) -> bool:
        """Mock processing - just store entries"""
        if event.event_type not in self.ACCOUNTING_EVENT_TYPES:
            return True
        
        entries = self.accounting_mapper.map_to_entries(event)
        self.posted_entries.append({
            "event_id": str(event.event_id),
            "event_type": event.event_type,
            "entries": entries,
            "processed_at": datetime.utcnow().isoformat()
        })
        
        self._update_status(event.event_id, AccountingStatus.POSTED)
        return True
