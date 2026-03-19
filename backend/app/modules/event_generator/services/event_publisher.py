"""
Event Publisher
Publishes events to message queues (Kafka/RabbitMQ)
"""

import json
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class MessageQueueType(str, Enum):
    """Message queue types"""

    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    REDIS = "redis"


class EventPublisher:
    """
    Publishes events to message queues and handles webhook delivery
    """

    # Topic mapping for different event types
    TOPIC_MAPPING = {
        # LC Events
        "LC_CREATED": "trade.lc.events",
        "LC_AMENDED": "trade.lc.events",
        "LC_APPROVED": "trade.lc.events",
        "LC_ISSUED": "trade.lc.events",
        "LC_AMENDED_AFTER_ISSUE": "trade.lc.events",
        "LC_UTILISED": "trade.lc.utilisation",
        "LC_SETTLED": "trade.lc.utilisation",
        "LC_EXPIRED": "trade.lc.events",
        "LC_TERMINATED": "trade.lc.events",
        # Guarantee Events
        "GUARANTEE_CREATED": "trade.guarantee.events",
        "GUARANTEE_ISSUED": "trade.guarantee.events",
        "GUARANTEE_CLAIMED": "trade.guarantee.events",
        "GUARANTEE_PAID": "trade.guarantee.events",
        "GUARANTEE_RELEASED": "trade.guarantee.events",
        # Trade Loan Events
        "TRADE_LOAN_DISBURSED": "trade.loan.events",
        "TRADE_LOAN_REPAID": "trade.loan.events",
        "TRADE_LOAN_DEFAULTED": "trade.risk",
        "TRADE_LOAN_RESTUCTURED": "trade.loan.events",
        # Collection Events
        "COLLECTION_CREATED": "trade.collection.events",
        "COLLECTION_SENT": "trade.collection.events",
        "COLLECTION_RECEIVED": "trade.collection.events",
        "COLLECTION_ACCEPTED": "trade.collection.events",
        "COLLECTION_REJECTED": "trade.collection.events",
        "COLLECTION_PAID": "trade.collection.events",
        # Invoice Events
        "INVOICE_CREATED": "trade.invoice.events",
        "INVOICE_FINANCED": "trade.invoice.events",
        "INVOICE_REPAID": "trade.invoice.events",
        "INVOICE_DEFAULTED": "trade.risk",
        # Document Events
        "DOCUMENT_UPLOADED": "trade.documents",
        "DOCUMENT_VERIFIED": "trade.documents",
        "DOCUMENT_REJECTED": "trade.documents",
        "DOCUMENT_RELEASED": "trade.documents",
        # Party Events
        "PARTY_ONBOARDED": "trade.parties",
        "PARTY_KYC_UPDATED": "trade.parties",
        "PARTY_RISK_RATING_CHANGED": "trade.risk",
    }

    # Events that need accounting processing
    ACCOUNTING_TOPIC = "trade.accounting"

    def __init__(
        self,
        queue_type: MessageQueueType = MessageQueueType.KAFKA,
        kafka_bootstrap_servers: Optional[str] = None,
        rabbitmq_url: Optional[str] = None,
        webhook_timeout: int = 30,
    ):
        self.queue_type = queue_type
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.rabbitmq_url = rabbitmq_url
        self.webhook_timeout = webhook_timeout
        self._producer = None

        # For now, we'll use a simple HTTP-based approach
        # In production, this would use actual Kafka/RabbitMQ clients

    def _get_topic(self, event_type: str) -> str:
        """Get topic for event type"""
        return self.TOPIC_MAPPING.get(event_type, "trade.general")

    def publish(self, event) -> bool:
        """
        Publish event to message queue

        Args:
            event: Event object to publish

        Returns:
            True if published successfully
        """
        topic = self._get_topic(event.event_type)
        message = self._serialize_event(event)

        try:
            if self.queue_type == MessageQueueType.KAFKA:
                return self._publish_to_kafka(topic, message)
            elif self.queue_type == MessageQueueType.RABBITMQ:
                return self._publish_to_rabbitmq(topic, message)
            else:
                logger.warning(f"Unknown queue type: {self.queue_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {str(e)}")
            raise

    def publish_to_accounting(self, event) -> bool:
        """Publish event to accounting topic"""
        message = self._serialize_event(event)

        try:
            if self.queue_type == MessageQueueType.KAFKA:
                return self._publish_to_kafka(self.ACCOUNTING_TOPIC, message)
            else:
                logger.warning(f"Accounting topic not supported for {self.queue_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to publish to accounting: {str(e)}")
            raise

    def _serialize_event(self, event) -> str:
        """Serialize event to JSON"""
        data = {
            "eventId": str(event.event_id),
            "eventType": event.event_type,
            "eventVersion": event.event_version,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "correlationId": event.correlation_id,
            "causationId": str(event.causation_id) if event.causation_id else None,
            "source": {
                "service": event.source_service,
                "actor": event.source_actor,
                "actorId": event.source_actor_id,
            },
            "payload": event.payload,
            "event_metadata": event.event_metadata,
            "accounting": (
                {
                    "enabled": event.accounting_enabled,
                    "entries": event.accounting_entries,
                }
                if event.accounting_enabled
                else None
            ),
            "tenantId": event.tenant_id,
        }

        return json.dumps(data)

    def _publish_to_kafka(self, topic: str, message: str) -> bool:
        """Publish to Kafka"""
        # In production, use kafka-python or confluent-kafka
        # For now, log the message
        logger.info(f"[KAFKA] Publishing to {topic}: {message[:200]}...")

        # Simulate successful publish
        # In production:
        # from kafka import KafkaProducer
        # self._producer.send(topic, value=message)
        # self._producer.flush()

        return True

    def _publish_to_rabbitmq(self, topic: str, message: str) -> bool:
        """Publish to RabbitMQ"""
        # In production, use pika
        logger.info(f"[RABBITMQ] Publishing to {topic}: {message[:200]}...")

        # Simulate successful publish
        return True

    def publish_webhook(
        self,
        event,
        webhook_url: str,
        webhook_secret: Optional[str] = None,
        format: str = "json",
    ) -> bool:
        """Publish event via webhook"""
        import hmac
        import hashlib

        payload = {
            "event": event.event_type,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "data": event.payload,
        }

        headers = {
            "Content-Type": "application/json",
            "X-Event-Id": str(event.event_id),
            "X-Event-Type": event.event_type,
        }

        # Add signature if secret is provided
        if webhook_secret:
            payload_str = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                webhook_secret.encode(), payload_str.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature

        try:
            response = httpx.post(
                webhook_url, json=payload, headers=headers, timeout=self.webhook_timeout
            )
            response.raise_for_status()
            logger.info(f"Webhook delivered successfully to {webhook_url}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Webhook delivery failed: {str(e)}")
            raise

    def close(self):
        """Close producer connections"""
        if self._producer:
            try:
                self._producer.close()
            except Exception as e:
                logger.error(f"Error closing producer: {str(e)}")


class MockEventPublisher(EventPublisher):
    """Mock publisher for testing"""

    def __init__(self):
        super().__init__()
        self.published_events = []

    def publish(self, event) -> bool:
        """Store event in memory"""
        self.published_events.append(
            {
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "topic": self._get_topic(event.event_type),
                "message": self._serialize_event(event),
            }
        )
        logger.info(f"[MOCK] Published event {event.event_id}")
        return True

    def publish_to_accounting(self, event) -> bool:
        """Store accounting event in memory"""
        logger.info(f"[MOCK] Published to accounting: {event.event_id}")
        return True
