# Event Generator Engine Design for Trade Finance Platform

## 1. Executive Summary

This document outlines the architectural design for an Event Generator Engine within a Trade Finance Platform. Since the platform operates without traditional accounting entries, the Event Generator serves as the primary mechanism for capturing, processing, and propagating business events across the system. This event-driven approach enables real-time processing, audit trails, and integration with external systems while maintaining financial integrity without conventional double-entry bookkeeping.

## 2. Design Principles

The Event Generator Engine adheres to the following foundational principles:

- **Event-First Architecture**: All platform actions generate immutable events as the source of truth
- **Eventual Consistency**: Events propagate asynchronously, ensuring eventual consistency across services
- **Auditability**: Every business action produces a traceable, auditable event record
- **Loose Coupling**: Event generators produce events for consumption by any interested parties
- **Temporal Ordering**: Events include precise timestamps enabling accurate sequencing

## 3. Core Event Schema

### 3.1 Base Event Structure

All events share a common envelope structure:

```json
{
  "eventId": "evt_xxxxxxxxxxxx",
  "eventType": "string",
  "eventVersion": "1.0",
  "timestamp": "ISO8601 UTC",
  "correlationId": "corr_xxxxxxxxxxxx",
  "causationId": "evt_xxxxxxxxxxxx",
  "source": {
    "service": "string",
    "actor": "user|system|external",
    "actorId": "string"
  },
  "payload": { },
  "metadata": {
    "traceId": "string",
    "spanId": "string",
    "tenantId": "string"
  }
}
```

### 3.2 Trade Finance Event Types

The platform generates events across the following categories:

#### Letter of Credit (LC) Events
| Event Type | Description |
|------------|-------------|
| `LC_CREATED` | New LC application submitted |
| `LC_AMENDED` | LC terms modified |
| `LC_APPROVED` | Credit committee approved |
| `LC_ISSUED` | LC formally issued to beneficiary |
| `LC_AMENDED_AFTER_ISSUE` | Amendment after issuance |
| `LC_UTILISED` | Drawing made against LC |
| `LC_SETTLED` | Full payment made |
| `LC_EXPIRED` | LC expired unutilised |
| `LC_TERMINATED` | Early termination |

#### Guarantee/Bond Events
| Event Type | Description |
|------------|-------------|
| `GUARANTEE_CREATED` | Guarantee request initiated |
| `GUARANTEE_ISSUED` | Guarantee issued to beneficiary |
| `GUARANTEE_CLAIMED` | Claim submitted by beneficiary |
| `GUARANTEE_PAID` | Claim paid |
| `GUARANTEE_RELEASED` | Guarantee released |

#### Trade Loan Events
| Event Type | Description |
|------------|-------------|
| `TRADE_LOAN_DISBURSED` | Loan amount disbursed |
| `TRADE_LOAN_REPAID` | Repayment received |
| `TRADE_LOAN_DEFAULTED` | Payment default occurred |
| `TRADE_LOAN_RESTUCTURED` | Terms restructured |

#### Document Events
| Event Type | Description |
|------------|-------------|
| `DOCUMENT_UPLOADED` | Trade document uploaded |
| `DOCUMENT_VERIFIED` | Document authenticity verified |
| `DOCUMENT_REJECTED` | Document rejected |
| `DOCUMENT_RELEASED` | Document released to party |

#### Party Events
| Event Type | Description |
|------------|-------------|
| `PARTY_ONBOARDED` | New customer/beneficiary added |
| `PARTY_KYC_UPDATED` | KYC information updated |
| `PARTY_RISK_RATING_CHANGED` | Risk rating modified |

## 4. Event Generator Architecture

### 4.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRADE FINANCE PLATFORM                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │   Service   │───▶│  Event Generator │───▶│ Event Router  │  │
│  │   Layer     │    │     Engine       │    │               │  │
│  └─────────────┘    └──────────────────┘    └───────┬───────┘  │
│                                                      │          │
│                     ┌──────────────────┐            │          │
│                     │   Event Store    │◀───────────┤          │
│                     │   (Persistence)  │            │          │
│                     └──────────────────┘            ▼          │
│                                          ┌──────────────────┐  │
│                              ┌──────────▶│   Message Queue  │  │
│                              │           │   (Kafka/Rabbit) │  │
│                              │           └────────┬─────────┘  │
│                              │                    │             │
│                              │    ┌───────────────┴──────────┐  │
│                              │    ▼                           ▼  │
│                              │ ┌──────────┐  ┌─────────────┐  │
│                              └─│ Notifier │  │  Downstream │  │
│                                │ Service  │  │  Systems    │  │
│                                └──────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Event Generator Engine Components

#### 4.2.1 Event Factory

The Event Factory constructs properly formatted events with appropriate metadata:

```python
class EventFactory:
    def create_event(
        self,
        event_type: str,
        payload: dict,
        source: SourceInfo,
        correlation_id: str = None,
        causation_id: str = None
    ) -> Event:
        event_id = self.generate_event_id()
        timestamp = datetime.utcnow()
        
        return Event(
            eventId=event_id,
            eventType=event_type,
            eventVersion="1.0",
            timestamp=timestamp,
            correlationId=correlation_id or event_id,
            causationId=causation_id,
            source=source,
            payload=payload,
            metadata=self._build_metadata(source)
        )
```

#### 4.2.2 Event Enricher

The Event Enricher adds additional context to events:

- Lookup related entities (counterparties, references)
- Add risk scoring context
- Include regulatory compliance flags
- Attach workflow state information

#### 4.2.3 Event Validator

Validates events before persistence:

- Schema validation against event type
- Required field verification
- Business rule validation
- Duplicate detection

#### 4.2.4 Event Publisher

Publishes validated events to the message infrastructure:

- Serialization (JSON/Avro/Protobuf)
- Topic/queue routing determination
- Delivery guarantee configuration
- Retry and dead-letter handling

## 5. Event Generation Patterns

### 5.1 Trigger-Based Generation

Events are generated in response to business operations:

```python
class TradeEventGenerator:
    def on_lc_created(self, lc_application: LCApplication) -> Event:
        payload = {
            "lcReference": lc_application.reference,
            "applicant": lc_application.applicant.party_id,
            "beneficiary": lc_application.beneficiary.party_id,
            "lcType": lc_application.type.value,
            "currency": lc_application.currency,
            "amount": str(lc_application.amount),
            "expiryDate": lc_application.expiry_date.isoformat(),
            "issuingBank": lc_application.issuing_bank.party_id
        }
        
        return self.event_factory.create_event(
            event_type="LC_CREATED",
            payload=payload,
            source=SourceInfo(
                service="lc_service",
                actor="user",
                actor_id=lc_application.created_by
            )
        )
```

### 5.2 Saga Orchestration Events

For multi-step workflows, events track saga state:

```python
class LCIssuanceSagaEvents:
    @staticmethod
    def saga_started(lc_id: str, correlation_id: str) -> Event:
        return Event(
            eventType="LC_ISSUANCE_SAGA_STARTED",
            payload={"lcId": lc_id, "steps": ["approval", "issuance", "notification"]},
            correlationId=correlation_id
        )
    
    @staticmethod
    def saga_step_completed(lc_id: str, step: str, correlation_id: str, causation_id: str) -> Event:
        return Event(
            eventType="LC_ISSUANCE_STEP_COMPLETED",
            payload={"lcId": lc_id, "completedStep": step},
            correlationId=correlation_id,
            causationId=causation_id
        )
    
    @staticmethod
    def saga_completed(lc_id: str, correlation_id: str, causation_id: str) -> Event:
        return Event(
            eventType="LC_ISSUANCE_SAGA_COMPLETED",
            payload={"lcId": lc_id},
            correlationId=correlation_id,
            causationId=causation_id
        )
```

### 5.3 Scheduled Event Generation

For time-based triggers:

```python
class ScheduledEventGenerator:
    def generate_expiry_events(self) -> List[Event]:
        expiring_lcs = self.lc_repository.find_expiring_within(days=7)
        
        events = []
        for lc in expiring_lcs:
            events.append(self.event_factory.create_event(
                event_type="LC_EXPIRY_WARNING",
                payload={
                    "lcId": lc.id,
                    "expiryDate": lc.expiry_date.isoformat(),
                    "daysUntilExpiry": (lc.expiry_date - date.today()).days,
                    "utilisationStatus": lc.utilisation_status
                },
                source=SourceInfo(service="scheduler", actor="system")
            ))
        
        return events
```

## 6. Event Routing and Filtering

### 6.1 Topic Configuration

Events are routed to topics based on event type:

```yaml
event_routing:
  topics:
    - name: trade.lc.events
      event_types:
        - LC_CREATED
        - LC_AMENDED
        - LC_APPROVED
        - LC_ISSUED
    
    - name: trade.lc.utilisation
      event_types:
        - LC_UTILISED
        - LC_SETTLED
    
    - name: trade.guarantee.events
      event_types:
        - GUARANTEE_CREATED
        - GUARANTEE_ISSUED
        - GUARANTEE_CLAIMED
    
    - name: trade.documents
      event_types:
        - DOCUMENT_UPLOADED
        - DOCUMENT_VERIFIED
    
    - name: trade.risk
      event_types:
        - TRADE_LOAN_DEFAULTED
        - PARTY_RISK_RATING_CHANGED
```

### 6.2 Event Filtering

Consumers can subscribe to filtered event streams:

```python
class EventFilter:
    def __init__(self):
        self.filters = {
            "by_tenant": self._filter_by_tenant,
            "by_currency": self._filter_by_currency,
            "by_amount_range": self._filter_by_amount,
            "by_party": self._filter_by_party
        }
    
    def apply(self, event: Event, filter_criteria: dict) -> bool:
        for criterion, value in filter_criteria.items():
            if criterion in self.filters:
                if not self.filters[criterion](event, value):
                    return False
        return True
```

## 7. Integration Patterns

### 7.1 External System Integration

The Event Generator supports integration with external systems:

```python
class ExternalEventHandler:
    def handle_incoming_swift_message(self, message: SWIFTMessage) -> Event:
        event_type_map = {
            "MT700": "LC_CREATED",
            "MT707": "LC_AMENDED",
            "MT734": "LC_ISSUED",
            "MT750": "LC_UTILISED"
        }
        
        return self.event_factory.create_event(
            event_type=event_type_map.get(message.message_type, "SWIFT_RECEIVED"),
            payload=self.swift_decoder.decode(message),
            source=SourceInfo(
                service="swift_gateway",
                actor="external",
                actor_id=message.sender
            ),
            correlation_id=message.transaction_reference
        )
```

### 7.2 Webhook Events

External parties receive events via webhooks:

```python
class WebhookEventPublisher:
    def publish(self, event: Event, subscription: WebhookSubscription):
        payload = {
            "event": event.event_type,
            "timestamp": event.timestamp,
            "data": self.serializer.serialize(event.payload, subscription.format)
        }
        
        response = httpx.post(
            subscription.url,
            json=payload,
            headers={
                "X-Webhook-Signature": self.sign(event, subscription.secret),
                "X-Event-Id": event.event_id
            }
        )
        
        if response.status_code >= 400:
            self.handle_delivery_failure(event, subscription, response)
```

## 8. Event Storage and Retrieval

### 8.1 Event Store Schema

```sql
CREATE TABLE events (
    event_id VARCHAR(50) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_version VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    correlation_id VARCHAR(50),
    causation_id VARCHAR(50),
    source_service VARCHAR(100) NOT NULL,
    source_actor VARCHAR(50) NOT NULL,
    source_actor_id VARCHAR(100),
    payload JSONB NOT NULL,
    metadata JSONB,
    tenant_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_correlation ON events(correlation_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_tenant ON events(tenant_id);
CREATE INDEX idx_events_payload ON events USING GIN(payload);
```

### 8.2 Event Query API

```python
@router.get("/events")
def query_events(
    event_type: Optional[str] = None,
    correlation_id: Optional[str] = None,
    from_timestamp: Optional[datetime] = None,
    to_timestamp: Optional[datetime] = None,
    tenant_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Event]:
    query = Event.query
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if correlation_id:
        query = query.filter(Event.correlation_id == correlation_id)
    if from_timestamp:
        query = query.filter(Event.timestamp >= from_timestamp)
    if to_timestamp:
        query = query.filter(Event.timestamp <= to_timestamp)
    if tenant_id:
        query = query.filter(Event.tenant_id == tenant_id)
    
    return query.order_by(Event.timestamp.desc()).limit(limit).offset(offset).all()
```

## 9. Idempotency and Deduplication

### 9.1 Idempotency Keys

Events include idempotency keys to prevent duplicate processing:

```python
class IdempotencyManager:
    def check_and_store(self, idempotency_key: str, event: Event) -> bool:
        if self.cache.exists(idempotency_key):
            return False
        
        self.cache.setex(
            idempotency_key,
            timedelta(hours=24),
            event.event_id
        )
        return True
```

### 9.2 Duplicate Detection

```python
class DuplicateDetector:
    def is_duplicate(self, event: Event) -> bool:
        hash_key = self.compute_event_hash(event)
        
        existing = self.event_store.find_by_hash(hash_key)
        
        if existing and existing.timestamp > datetime.utcnow() - timedelta(minutes=5):
            return True
        
        return False
    
    def compute_event_hash(self, event: Event) -> str:
        content = f"{event.event_type}:{event.payload}:{event.source}"
        return hashlib.sha256(content.encode()).hexdigest()
```

## 10. Monitoring and Observability

### 10.1 Event Metrics

```python
class EventMetrics:
    def record_event_generated(self, event_type: str, duration_ms: float):
        self.metrics.increment(
            "trade_finance.events.generated",
            tags={"event_type": event_type}
        )
        self.metrics.histogram(
            "trade_finance.event_generation.duration",
            duration_ms,
            tags={"event_type": event_type}
        )
    
    def record_event_published(self, event_type: str, topic: str, success: bool):
        self.metrics.increment(
            "trade_finance.events.published",
            tags={
                "event_type": event_type,
                "topic": topic,
                "success": str(success).lower()
            }
        )
```

### 10.2 Health Checks

```python
@router.get("/health/events")
def event_health_check() -> HealthStatus:
    checks = {
        "event_store": self.check_event_store_connection(),
        "message_queue": self.check_message_queue_connection(),
        "event_generator": self.check_generator_queue_depth()
    }
    
    return HealthStatus(
        status="healthy" if all(c.status == "ok" for c in checks.values()) else "degraded",
        checks=checks
    )
```

## 11. Core Banking & Accounting Integration

### 11.1 Architecture Overview

Since the Trade Finance Platform operates without its own General Ledger (GL), the Event Generator serves as the **bridge** between trade events and the Core Banking System (CBS). This design uses a **dual approach**:

1. **Event Generator** includes accounting metadata hints in events
2. **Accounting Event Subscriber** consumes events and posts entries to CBS

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRADE FINANCE PLATFORM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐  │
│  │ Trade        │    │ Event Generator │    │ Accounting       │  │
│  │ Services     │───▶│ Engine          │───▶│ Metadata Layer   │  │
│  └──────────────┘    └─────────────────┘    └────────┬─────────┘  │
│                                                       │            │
│                          ┌─────────────────┐          │            │
│                          │ Event Store     │◀─────────┤            │
│                          └────────┬────────┘          │            │
│                                   │                   │            │
│                                   ▼                   │            │
│  ┌─────────────────────────────────────────────────────┴─────────┐  │
│  │                    Message Queue (Kafka)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐ │  │
│  │  │ trade.lc     │  │ trade.loan   │  │ trade.accounting    │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬──────────┘ │  │
│  └─────────┼─────────────────┼─────────────────────┼───────────┘  │
│            │                 │                     │               │
│            ▼                 ▼                     ▼               │
│  ┌──────────────────┐  ┌──────────────┐   ┌──────────────────────┐│
│  │ Trade Finance   │  │ Notification │   │ Accounting Event    ││
│  │ UI/Clients      │  │ Service      │   │ Subscriber           ││
│  └──────────────────┘  └──────────────┘   └──────────┬───────────┘│
│                                                      │              │
│                                                      ▼              │
│                                            ┌──────────────────────┐│
│                                            │  Core Banking System  ││
│                                            │  (GL/Accounting)     ││
│                                            │  ─────────────────    ││
│                                            │  • General Ledger     ││
│                                            │  • Nostro/Vostro      ││
│                                            │  • Interest Accruals  ││
│                                            └──────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 11.2 Recommended Approach: Core Banking Subscribes to Events

The recommended pattern is that **Core Banking System subscribes to events** from the Trade Finance Platform and posts its own accounting entries. This maintains separation of concerns:

- **Trade Finance Platform**: Handles trade lifecycle, documents, workflows, risk
- **Core Banking System**: Owns GL accounts, posting rules, regulatory accounting

#### Event Flow to Core Banking

```
Trade Finance Platform              Core Banking System
─────────────────────               ───────────────────
     
LC_ISSUED Event ──────────────────▶ Receive Event
    │                                    │
    │  {                                 │  Lookup GL Accounts:
    │    "lcId": "LC/001",              │  • Nostro Account
    │    "amount": "100000",           │  • LC Contingent Liability
    │    "currency": "USD",            │  • Commission Income
    │    "accountingHint": {            │
    │      "nostroAccount": "USD001",  ├─────────────────────▶ Post Entries:
    │      "contingentGl": "20100",     │                        Dr. Nostro    100,000
    │      "commissionGl": "40100"      │                        Cr. LC Liab.  100,000
    │    }                               │
    │  }                                 │  Return: AC/2026/001
```

### 11.3 Event Schema with Accounting Metadata

Each event includes an optional `accounting` section that provides hints for the CBS:

```json
{
  "eventId": "evt_abc123",
  "eventType": "LC_ISSUED",
  "timestamp": "2026-03-18T10:00:00Z",
  "correlationId": "corr_xyz789",
  "source": {
    "service": "lc_service",
    "actor": "system",
    "actorId": "workflow-engine"
  },
  "payload": {
    "lcReference": "LC/2026/001",
    "applicantPartyId": "PTY001",
    "beneficiaryPartyId": "PTY002",
    "amount": "100000.00",
    "currency": "USD",
    "issuingBank": "BANK001",
    "issueDate": "2026-03-18",
    "expiryDate": "2026-09-18"
  },
  "accounting": {
    "enabled": true,
    "entries": [
      {
        "entryType": "CONTINGENT_LIABILITY",
        "debitAccount": {
          "type": "GL",
          "accountCode": "20100",
          "branchCode": "HO",
          "currency": "USD"
        },
        "creditAccount": {
          "type": "GL",
          "accountCode": "20101",
          "branchCode": "HO",
          "currency": "USD"
        },
        "amount": "100000.00",
        "narrative": "LC 001 - Issue - USD 100,000.00"
      },
      {
        "entryType": "COMMISSION_INCOME",
        "debitAccount": {
          "type": "DORMANT",
          "accountCode": "001",
          "partyId": "PTY001"
        },
        "creditAccount": {
          "type": "GL",
          "accountCode": "40100",
          "branchCode": "HO"
        },
        "amount": "500.00",
        "narrative": "LC 001 - Commission"
      }
    ]
  },
  "metadata": {
    "tenantId": "TENANT001",
    "traceId": "trace_abc"
  }
}
```

### 11.4 Event-to-GL Entry Mapping

#### Letter of Credit (LC) Events

| Event Type | Debit Entry | Credit Entry | GL Account Codes |
|------------|-------------|--------------|------------------|
| `LC_CREATED` | — | — | No GL impact (application only) |
| `LC_APPROVED` | — | — | No GL impact |
| `LC_ISSUED` | Nostro Account | LC Contingent Liability | Dr. 1xxx / Cr. 2xxx |
| `LC_UTILISED` | Nostro Account | LC Paid Liability | Dr. 1xxx / Cr. 2xxx |
| `LC_SETTLED` | LC Paid Liability | Nostro Account | Dr. 2xxx / Cr. 1xxx |
| `LC_EXPIRED` | LC Contingent Liability | Nostro/Release | Dr. 2xxx / Cr. 1xxx |

#### Guarantee Events

| Event Type | Debit Entry | Credit Entry | GL Account Codes |
|------------|-------------|--------------|------------------|
| `GUARANTEE_ISSUED` | Nostro Account | Guarantee Contingent | Dr. 1xxx / Cr. 2xxx |
| `GUARANTEE_CLAIMED` | Nostro Account | Guarantee Paid | Dr. 1xxx / Cr. 2xxx |
| `GUARANTEE_PAID` | Guarantee Paid | Nostro Account | Dr. 2xxx / Cr. 1xxx |
| `GUARANTEE_RELEASED` | Guarantee Contingent | Nostro Account | Dr. 2xxx / Cr. 1xxx |

#### Trade Loan Events

| Event Type | Debit Entry | Credit Entry | GL Account Codes |
|------------|-------------|--------------|------------------|
| `TRADE_LOAN_DISBURSED` | Loan Receivable | Nostro Account | Dr. 1xxx / Cr. 1xxx |
| `TRADE_LOAN_REPAID` | Nostro Account | Loan Receivable | Dr. 1xxx / Cr. 1xxx |
| `TRADE_LOAN_REPAID` | Nostro Account | Interest Income | Dr. 1xxx / Cr. 4xxx |
| `TRADE_LOAN_DEFAULTED` | Loan Receivable | NPL Provision | Dr. 1xxx / Cr. 2xxx |

### 11.5 Accounting Event Subscriber Component

The Accounting Event Subscriber consumes events and sends accounting requests to CBS:

```python
class AccountingEventSubscriber:
    def __init__(
        self,
        event_consumer: EventConsumer,
        cbs_client: CoreBankingClient,
        accounting_mapper: AccountingMapper
    ):
        self.consumer = event_consumer
        self.cbs = cbs_client
        self.mapper = accounting_mapper
        self.accounting_event_types = {
            "LC_ISSUED", "LC_UTILISED", "LC_SETTLED", "LC_EXPIRED",
            "GUARANTEE_ISSUED", "GUARANTEE_CLAIMED", "GUARANTEE_PAID",
            "TRADE_LOAN_DISBURSED", "TRADE_LOAN_REPAID", "TRADE_LOAN_DEFAULTED"
        }
    
    async def start(self):
        await self.consumer.subscribe(
            topics=["trade.accounting"],
            group_id="accounting-subscriber",
            callback=self.process_event
        )
    
    async def process_event(self, event: Event):
        if event.event_type not in self.accounting_event_types:
            return
        
        if not event.accounting or not event.accounting.get("enabled"):
            return
        
        # Map event to accounting entries
        accounting_entries = self.mapper.map_to_entries(event)
        
        # Post to Core Banking System
        try:
            result = await self.cbs.post_accounting_entries(
                entries=accounting_entries,
                event_id=event.event_id,
                idempotency_key=self.generate_idempotency_key(event)
            )
            
            # Update event status
            await self.update_event_accounting_status(
                event.event_id,
                status="POSTED",
                cbs_reference=result.reference
            )
            
        except CBSException as e:
            # Handle failure - retry or dead-letter
            await self.handle_accounting_failure(event, e)
```

### 11.6 Accounting Mapper

Maps trade events to accounting entries based on configuration:

```python
class AccountingMapper:
    def __init__(self, gl_account_config: GLAccountConfig):
        self.config = gl_account_config
    
    def map_to_entries(self, event: Event) -> List[AccountingEntry]:
        mapping_rules = self.get_mapping_rules(event.event_type)
        
        entries = []
        for rule in mapping_rules:
            entry = self.build_entry(event, rule)
            entries.append(entry)
        
        return entries
    
    def get_mapping_rules(self, event_type: str) -> List[MappingRule]:
        return {
            "LC_ISSUED": [
                MappingRule(
                    entry_type="CONTINGENT_LIABILITY",
                    debit_gl=self.config.get_gl("LC_CONTINGENT"),
                    credit_gl=self.config.get_nostro(event.payload["currency"]),
                    amount_source="payload.amount",
                    narrative_template="LC {lcRef} - Issue - {currency} {amount}"
                )
            ],
            "LC_UTILISED": [
                MappingRule(
                    entry_type="UTILISATION",
                    debit_gl=self.config.get_gl("LC_CONTINGENT"),
                    credit_gl=self.config.get_gl("LC_PAID"),
                    amount_source="payload.amount",
                    narrative_template="LC {lcRef} - Utilisation - {currency} {amount}"
                ),
                MappingRule(
                    entry_type="NOSTRO_OUT",
                    debit_gl=self.config.get_nostro(event.payload["currency"]),
                    credit_gl=self.config.get_gl("SETTLEMENT"),
                    amount_source="payload.amount",
                    narrative_template="LC {lcRef} - Payment - {currency} {amount}"
                )
            ]
        }.get(event_type, [])
```

### 11.7 Core Banking Integration API

The CBS client interface for posting accounting entries:

```python
class CoreBankingClient:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth = auth_token
    
    async def post_accounting_entries(
        self,
        entries: List[AccountingEntry],
        event_id: str,
        idempotency_key: str
    ) -> CBSResponse:
        """
        POST /api/v1/accounting/entries
        
        Request:
        {
            "idempotencyKey": "idemp_lc001_123",
            "eventId": "evt_abc123",
            "entries": [
                {
                    "entryType": "CONTINGENT_LIABILITY",
                    "debitAccount": {"type": "GL", "code": "20100"},
                    "creditAccount": {"type": "GL", "code": "20101"},
                    "amount": "100000.00",
                    "currency": "USD",
                    "valueDate": "2026-03-18",
                    "narrative": "LC 001 - Issue"
                }
            ]
        }
        
        Response:
        {
            "status": "POSTED",
            "reference": "AC/2026/0001",
            "entryReferences": ["AE/001", "AE/002"]
        }
        """
        response = await httpx.post(
            f"{self.base_url}/api/v1/accounting/entries",
            json={
                "idempotencyKey": idempotency_key,
                "eventId": event_id,
                "entries": [e.to_dict() for e in entries]
            },
            headers={"Authorization": f"Bearer {self.auth}"}
        )
        response.raise_for_status()
        return CBSResponse(**response.json())
```

### 11.8 Accounting Status Tracking

Track accounting entry status for each event:

```sql
CREATE TABLE event_accounting_status (
    event_id VARCHAR(50) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    accounting_enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) NOT NULL,  -- PENDING, POSTED, FAILED, SKIPPED
    cbs_reference VARCHAR(50),
    entry_count INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_accounting_status ON event_accounting_status(status, retry_count);
```

## 13. Security Considerations

### 13.1 Event Signing

All events are signed for integrity verification:

```python
class EventSigner:
    def sign(self, event: Event, private_key: str) -> str:
        payload = json.dumps(event.payload, sort_keys=True)
        signature = rsa.sign(
            payload.encode(),
            private_key,
            padding.PKCS1v15(),
            hash.SHA256()
        )
        return base64.b64encode(signature).decode()
```

### 11.2 Data Masking

Sensitive fields are masked in events:

```python
class EventDataMasker:
    SENSITIVE_FIELDS = {
        "account_number": mask_account_number,
        "iban": mask_iban,
        "amount": lambda x: "***",
        "party_id": lambda x: x[:8] + "****"
    }
    
    def mask_event(self, event: Event) -> Event:
        masked_payload = self.mask_dict(event.payload, self.SENSITIVE_FIELDS)
        return Event(**{**event.__dict__, "payload": masked_payload})
```

## 13. Implementation Roadmap

### Phase 1: Core Infrastructure
- Event schema definition
- Event factory implementation
- Basic event persistence
- Event query API

### Phase 2: Event Generation
- Service layer integration
- Trigger-based event creation
- Saga event handling
- Scheduled event generation

### Phase 3: Distribution
- Message queue integration
- Topic routing configuration
- Webhook delivery
- External system connectors

### Phase 4: Accounting Integration
- Accounting metadata in event payload
- Accounting event subscriber implementation
- CBS API integration
- GL account mapping configuration
- Accounting status tracking

### Phase 5: Advanced Features
- Event enrichment
- Filtering and transformation
- Idempotency handling
- Monitoring and alerting

## 14. Conclusion

The Event Generator Engine provides the foundational event-driven infrastructure for the Trade Finance Platform. By capturing all business actions as immutable events, the system achieves transparency, auditability, and real-time processing capabilities without relying on traditional accounting entries. The modular design ensures scalability and maintainability as the platform grows.

---

*Document Version: 1.0*
*Last Updated: 2026-03-18*
