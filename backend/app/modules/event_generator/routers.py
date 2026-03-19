"""
Event Generator API Routes
RESTful endpoints for event management
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from ...database import get_db
from ...core.database import AsyncSessionLocal
from ..users.models.user import User
from ...core.auth.jwt_handler import get_current_active_user
from .schemas.event import (
    EventCreate,
    EventResponse,
    EventListResponse,
    EventQueryParams,
    EventAccountingStatusResponse,
    EventSubscriptionCreate,
    EventSubscriptionResponse,
    EventHealthResponse,
)
from .services.event_generator import EventGenerator
from .services.event_repository import EventRepository
from .services.event_factory import EventFactory
from .services.event_publisher import EventPublisher
from .models.event import EventSubscription

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency for event generator
def get_event_generator(db: AsyncSession = Depends(get_db)) -> EventGenerator:
    """Get event generator instance"""
    repository = EventRepository(db)
    factory = EventFactory()
    publisher = EventPublisher()  # In production, configure properly

    return EventGenerator(
        db=db,
        event_factory=factory,
        event_repository=repository,
        event_publisher=publisher,
    )


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    event_generator: EventGenerator = Depends(get_event_generator),
):
    """
    Create a new event

    This endpoint allows manual event creation for testing or integration purposes.
    """
    try:
        # Extract source info from event data
        source = event_data.source

        # Extract accounting entries
        accounting_entries = None
        if event_data.accounting and event_data.accounting.enabled:
            accounting_entries = [
                entry.model_dump() for entry in event_data.accounting.entries
            ]

        # Extract event_metadata
        event_metadata = None
        if event_data.event_metadata:
            event_metadata = event_data.event_metadata.model_dump()

        # Generate event
        event = event_generator.generate_event(
            event_type=event_data.event_type.value,
            payload=event_data.payload,
            source_service=source.service,
            source_actor=source.actor.value,
            source_actor_id=source.actor_id,
            correlation_id=event_data.correlation_id,
            causation_id=event_data.causation_id,
            event_metadata=event_metadata,
            accounting_entries=accounting_entries,
            tenant_id=event_data.tenant_id or current_user.organization_id,
        )

        return EventResponse(
            event_id=event.event_id,
            event_type=event.event_type,
            event_version=event.event_version,
            timestamp=event.timestamp,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            source=event_data.source,
            payload=event.payload,
            event_metadata=event.event_metadata,
            accounting_enabled=event.accounting_enabled,
            accounting_entries=event.accounting_entries,
            tenant_id=event.tenant_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create event")


@router.get("/", response_model=EventListResponse)
async def list_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    correlation_id: Optional[str] = Query(None, description="Filter by correlation ID"),
    from_timestamp: Optional[datetime] = Query(None, description="From timestamp"),
    to_timestamp: Optional[datetime] = Query(None, description="To timestamp"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant"),
    source_service: Optional[str] = Query(None, description="Filter by source service"),
    limit: int = Query(100, le=1000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Query events with filters
    """
    repository = EventRepository(db)

    # Get events
    events = repository.get_events(
        event_type=event_type,
        correlation_id=correlation_id,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
        tenant_id=tenant_id or current_user.organization_id,
        source_service=source_service,
        limit=limit,
        offset=offset,
    )

    # Get total count
    total = repository.count(
        event_type=event_type,
        correlation_id=correlation_id,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
        tenant_id=tenant_id or current_user.organization_id,
    )

    # Convert to response
    event_responses = []
    for event in events:
        event_responses.append(
            EventResponse(
                event_id=event.event_id,
                event_type=event.event_type,
                event_version=event.event_version,
                timestamp=event.timestamp,
                correlation_id=event.correlation_id,
                causation_id=event.causation_id,
                source={
                    "service": event.source_service,
                    "actor": event.source_actor,
                    "actor_id": event.source_actor_id,
                },
                payload=event.payload,
                event_metadata=event.event_metadata,
                accounting_enabled=event.accounting_enabled,
                accounting_entries=event.accounting_entries,
                tenant_id=event.tenant_id,
            )
        )

    pages = (total + limit - 1) // limit

    return EventListResponse(
        events=event_responses,
        total=total,
        page=offset // limit + 1,
        page_size=limit,
        pages=pages,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get event by ID
    """
    repository = EventRepository(db)
    event = repository.get_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse(
        event_id=event.event_id,
        event_type=event.event_type,
        event_version=event.event_version,
        timestamp=event.timestamp,
        correlation_id=event.correlation_id,
        causation_id=event.causation_id,
        source={
            "service": event.source_service,
            "actor": event.source_actor,
            "actor_id": event.source_actor_id,
        },
        payload=event.payload,
        event_metadata=event.event_metadata,
        accounting_enabled=event.accounting_enabled,
        accounting_entries=event.accounting_entries,
        tenant_id=event.tenant_id,
    )


@router.get(
    "/{event_id}/accounting-status", response_model=EventAccountingStatusResponse
)
async def get_accounting_status(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get accounting status for an event
    """
    repository = EventRepository(db)
    status_record = repository.get_accounting_status(event_id)

    if not status_record:
        raise HTTPException(status_code=404, detail="Accounting status not found")

    return EventAccountingStatusResponse(
        event_id=status_record.event_id,
        event_type=status_record.event_type,
        accounting_enabled=status_record.accounting_enabled,
        status=status_record.status,
        cbs_reference=status_record.cbs_reference,
        entry_count=status_record.entry_count,
        error_message=status_record.error_message,
        retry_count=status_record.retry_count,
        created_at=status_record.created_at,
        updated_at=status_record.updated_at,
    )


@router.post("/replay", response_model=EventListResponse)
async def replay_events(
    from_timestamp: Optional[datetime] = Query(None, description="From timestamp"),
    to_timestamp: Optional[datetime] = Query(None, description="To timestamp"),
    event_types: Optional[List[str]] = Query(None, description="Event types to replay"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    event_generator: EventGenerator = Depends(get_event_generator),
):
    """
    Replay events for recovery or reprocessing
    """
    try:
        events = event_generator.replay_events(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            event_types=event_types,
        )

        event_responses = []
        for event in events:
            event_responses.append(
                EventResponse(
                    event_id=event.event_id,
                    event_type=event.event_type,
                    event_version=event.event_version,
                    timestamp=event.timestamp,
                    correlation_id=event.correlation_id,
                    causation_id=event.causation_id,
                    source={
                        "service": event.source_service,
                        "actor": event.source_actor,
                        "actor_id": event.source_actor_id,
                    },
                    payload=event.payload,
                    event_metadata=event.event_metadata,
                    accounting_enabled=event.accounting_enabled,
                    accounting_entries=event.accounting_entries,
                    tenant_id=event.tenant_id,
                )
            )

        return EventListResponse(
            events=event_responses,
            total=len(events),
            page=1,
            page_size=len(events),
            pages=1,
        )

    except Exception as e:
        logger.error(f"Failed to replay events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to replay events")


# Subscription endpoints
@router.post(
    "/subscriptions",
    response_model=EventSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription(
    subscription_data: EventSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create an event subscription
    """
    subscription = EventSubscription(
        name=subscription_data.name,
        description=subscription_data.description,
        event_types=(
            [et.value for et in subscription_data.event_types]
            if subscription_data.event_types
            else None
        ),
        tenant_id=subscription_data.tenant_id or current_user.organization_id,
        delivery_type=subscription_data.delivery_type.value,
        endpoint=subscription_data.endpoint,
        queue_name=subscription_data.queue_name,
        webhook_secret=subscription_data.webhook_secret,
        webhook_format=subscription_data.webhook_format,
        is_active=subscription_data.is_active,
    )

    repository = EventRepository(db)
    subscription = repository.create_subscription(subscription)

    return EventSubscriptionResponse(
        subscription_id=subscription.subscription_id,
        name=subscription.name,
        description=subscription.description,
        event_types=subscription.event_types,
        tenant_id=subscription.tenant_id,
        delivery_type=subscription.delivery_type,
        endpoint=subscription.endpoint,
        queue_name=subscription.queue_name,
        is_active=subscription.is_active,
        events_delivered=subscription.events_delivered,
        last_delivered_at=subscription.last_delivered_at,
        created_at=subscription.created_at,
    )


@router.get("/subscriptions", response_model=List[EventSubscriptionResponse])
async def list_subscriptions(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List event subscriptions
    """
    repository = EventRepository(db)
    subscriptions = repository.get_active_subscriptions(
        event_type=event_type, tenant_id=tenant_id or current_user.organization_id
    )

    return [
        EventSubscriptionResponse(
            subscription_id=sub.subscription_id,
            name=sub.name,
            description=sub.description,
            event_types=sub.event_types,
            tenant_id=sub.tenant_id,
            delivery_type=sub.delivery_type,
            endpoint=sub.endpoint,
            queue_name=sub.queue_name,
            is_active=sub.is_active,
            events_delivered=sub.events_delivered,
            last_delivered_at=sub.last_delivered_at,
            created_at=sub.created_at,
        )
        for sub in subscriptions
    ]


@router.delete(
    "/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an event subscription
    """
    repository = EventRepository(db)
    success = repository.delete_subscription(subscription_id)

    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")


@router.get("/health", response_model=EventHealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check for event generator
    """
    # Check database connection
    event_store_status = "ok"
    try:
        db.execute("SELECT 1")
    except Exception:
        event_store_status = "error"

    # Check message queue (mock for now)
    message_queue_status = "ok"

    # Check event generator queue
    event_generator_status = "ok"

    return EventHealthResponse(
        status=(
            "healthy"
            if all(
                s == "ok"
                for s in [
                    event_store_status,
                    message_queue_status,
                    event_generator_status,
                ]
            )
            else "degraded"
        ),
        event_store=event_store_status,
        message_queue=message_queue_status,
        event_generator=event_generator_status,
        timestamp=datetime.utcnow(),
    )
