"""
Event Generator Integration Helpers
This module provides mixins and helpers to integrate event generation
into existing services (LC, Guarantee, Trade Loan, etc.)
"""

import logging
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from .services.event_generator import EventGenerator
from .services.event_factory import EventFactory
from .services.accounting_mapper import AccountingMapper

logger = logging.getLogger(__name__)


class EventGeneratorMixin:
    """
    Mixin class to add event generation capabilities to services
    
    Usage:
        class LCService(EventGeneratorMixin, BaseService):
            def __init__(self, db, event_generator):
                self.db = db
                self.event_generator = event_generator
                self.accounting_mapper = AccountingMapper()
            
            def create_lc(self, lc_data):
                # Create LC
                lc = self._create_lc_record(lc_data)
                
                # Generate event
                self.generate_lc_created_event(lc)
                
                return lc
    """
    
    # Override these in subclasses
    event_generator: EventGenerator = None
    accounting_mapper: AccountingMapper = None
    
    def generate_lc_created_event(
        self,
        lc,
        actor: str = "user",
        actor_id: Optional[str] = None
        ):
        """Generate LC_CREATED event"""
        lc_data = {
            "id": str(lc.id),
            "reference": lc.reference,
            "applicant_party_id": str(lc.applicant_id),
            "beneficiary_party_id": str(lc.beneficiary_id),
            "type": lc.lc_type,
            "currency": lc.currency,
            "amount": str(lc.amount),
            "expiry_date": lc.expiry_date.isoformat() if lc.expiry_date else None,
            "issue_date": lc.issue_date.isoformat() if lc.issue_date else None,
            "issuing_bank": str(lc.issuing_bank_id) if lc.issuing_bank_id else None
        }
        
        # No accounting entries for creation
        event = self.event_generator.generate_lc_event(
            event_type="LC_CREATED",
            lc_data=lc_data,
            actor=actor,
            actor_id=actor_id,
            accounting_entries=None,
            tenant_id=str(lc.organization_id) if hasattr(lc, 'organization_id') else None
        )
        
        logger.info(f"Generated LC_CREATED event: {event.event_id}")
        return event
    
    def generate_lc_issued_event(
        self,
        lc,
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Generate LC_ISSUED event with accounting entries"""
        lc_data = {
            "id": str(lc.id),
            "reference": lc.reference,
            "applicant_party_id": str(lc.applicant_id),
            "beneficiary_party_id": str(lc.beneficiary_id),
            "type": lc.lc_type,
            "currency": lc.currency,
            "amount": str(lc.amount),
            "expiry_date": lc.expiry_date.isoformat() if lc.expiry_date else None,
            "issue_date": lc.issue_date.isoformat() if lc.issue_date else None,
            "issuing_bank": str(lc.issuing_bank_id) if lc.issuing_bank_id else None
        }
        
        # Generate accounting entries using mapper
        # Create a mock event for the mapper
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        mock_event = MockEvent("LC_ISSUED", lc_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        event = self.event_generator.generate_lc_event(
            event_type="LC_ISSUED",
            lc_data=lc_data,
            actor=actor,
            actor_id=actor_id,
            correlation_id=correlation_id,
            accounting_entries=accounting_entries,
            tenant_id=str(lc.organization_id) if hasattr(lc, 'organization_id') else None
        )
        
        logger.info(f"Generated LC_ISSUED event: {event.event_id}")
        return event
    
    def generate_lc_utilised_event(
        self,
        lc,
        utilisation_amount: str,
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Generate LC_UTILISED event with accounting entries"""
        lc_data = {
            "id": str(lc.id),
            "reference": lc.reference,
            "applicant_party_id": str(lc.applicant_id),
            "beneficiary_party_id": str(lc.beneficiary_id),
            "type": lc.lc_type,
            "currency": lc.currency,
            "amount": utilisation_amount,
            "expiry_date": lc.expiry_date.isoformat() if lc.expiry_date else None,
            "issue_date": lc.issue_date.isoformat() if lc.issue_date else None,
            "issuing_bank": str(lc.issuing_bank_id) if lc.issuing_bank_id else None
        }
        
        # Generate accounting entries
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        mock_event = MockEvent("LC_UTILISED", lc_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        event = self.event_generator.generate_lc_event(
            event_type="LC_UTILISED",
            lc_data=lc_data,
            actor=actor,
            actor_id=actor_id,
            correlation_id=correlation_id,
            accounting_entries=accounting_entries,
            tenant_id=str(lc.organization_id) if hasattr(lc, 'organization_id') else None
        )
        
        logger.info(f"Generated LC_UTILISED event: {event.event_id}")
        return event
    
    def generate_lc_settled_event(
        self,
        lc,
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Generate LC_SETTLED event with accounting entries"""
        lc_data = {
            "id": str(lc.id),
            "reference": lc.reference,
            "applicant_party_id": str(lc.applicant_id),
            "beneficiary_party_id": str(lc.beneficiary_id),
            "type": lc.lc_type,
            "currency": lc.currency,
            "amount": str(lc.amount),
            "expiry_date": lc.expiry_date.isoformat() if lc.expiry_date else None,
            "issue_date": lc.issue_date.isoformat() if lc.issue_date else None,
            "issuing_bank": str(lc.issuing_bank_id) if lc.issuing_bank_id else None
        }
        
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        mock_event = MockEvent("LC_SETTLED", lc_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        event = self.event_generator.generate_lc_event(
            event_type="LC_SETTLED",
            lc_data=lc_data,
            actor=actor,
            actor_id=actor_id,
            correlation_id=correlation_id,
            accounting_entries=accounting_entries,
            tenant_id=str(lc.organization_id) if hasattr(lc, 'organization_id') else None
        )
        
        logger.info(f"Generated LC_SETTLED event: {event.event_id}")
        return event
    
    # Guarantee events
    def generate_guarantee_issued_event(
        self,
        guarantee,
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Generate GUARANTEE_ISSUED event"""
        guarantee_data = {
            "id": str(guarantee.id),
            "reference": guarantee.reference,
            "applicant_party_id": str(guarantee.applicant_id),
            "beneficiary_party_id": str(guarantee.beneficiary_id),
            "type": guarantee.guarantee_type,
            "currency": guarantee.currency,
            "amount": str(guarantee.amount),
            "expiry_date": guarantee.expiry_date.isoformat() if guarantee.expiry_date else None,
            "issue_date": guarantee.issue_date.isoformat() if guarantee.issue_date else None,
            "issuing_bank": str(guarantee.issuing_bank_id) if guarantee.issuing_bank_id else None
        }
        
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        mock_event = MockEvent("GUARANTEE_ISSUED", guarantee_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        event = self.event_generator.generate_guarantee_event(
            event_type="GUARANTEE_ISSUED",
            guarantee_data=guarantee_data,
            actor=actor,
            actor_id=actor_id,
            correlation_id=correlation_id,
            accounting_entries=accounting_entries,
            tenant_id=str(guarantee.organization_id) if hasattr(guarantee, 'organization_id') else None
        )
        
        logger.info(f"Generated GUARANTEE_ISSUED event: {event.event_id}")
        return event
    
    # Trade Loan events
    def generate_trade_loan_disbursed_event(
        self,
        loan,
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Generate TRADE_LOAN_DISBURSED event"""
        loan_data = {
            "id": str(loan.id),
            "reference": loan.reference,
            "borrower_party_id": str(loan.borrower_id),
            "type": loan.loan_type,
            "currency": loan.currency,
            "amount": str(loan.amount),
            "disbursement_date": loan.disbursement_date.isoformat() if loan.disbursement_date else None,
            "maturity_date": loan.maturity_date.isoformat() if loan.maturity_date else None,
            "lending_bank": str(loan.lending_bank_id) if loan.lending_bank_id else None
        }
        
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        mock_event = MockEvent("TRADE_LOAN_DISBURSED", loan_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        event = self.event_generator.generate_trade_loan_event(
            event_type="TRADE_LOAN_DISBURSED",
            loan_data=loan_data,
            actor=actor,
            actor_id=actor_id,
            correlation_id=correlation_id,
            accounting_entries=accounting_entries,
            tenant_id=str(loan.organization_id) if hasattr(loan, 'organization_id') else None
        )
        
        logger.info(f"Generated TRADE_LOAN_DISBURSED event: {event.event_id}")
        return event
    
    def generate_trade_loan_repaid_event(
        self,
        loan,
        repayment_amount: str,
        interest_amount: str,
        actor: str = "system",
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Generate TRADE_LOAN_REPAID event"""
        loan_data = {
            "id": str(loan.id),
            "reference": loan.reference,
            "borrower_party_id": str(loan.borrower_id),
            "type": loan.loan_type,
            "currency": loan.currency,
            "amount": repayment_amount,
            "interestAmount": interest_amount,
            "disbursement_date": loan.disbursement_date.isoformat() if loan.disbursement_date else None,
            "maturity_date": loan.maturity_date.isoformat() if loan.maturity_date else None,
            "lending_bank": str(loan.lending_bank_id) if loan.lending_bank_id else None
        }
        
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        mock_event = MockEvent("TRADE_LOAN_REPAID", loan_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        event = self.event_generator.generate_trade_loan_event(
            event_type="TRADE_LOAN_REPAID",
            loan_data=loan_data,
            actor=actor,
            actor_id=actor_id,
            correlation_id=correlation_id,
            accounting_entries=accounting_entries,
            tenant_id=str(loan.organization_id) if hasattr(loan, 'organization_id') else None
        )
        
        logger.info(f"Generated TRADE_LOAN_REPAID event: {event.event_id}")
        return event


# Helper function to create event generator with dependencies
def create_event_generator(db):
    """Create event generator with all dependencies"""
    from ...database import SessionLocal
    
    event_factory = EventFactory()
    event_repository = EventRepository(db)
    
    # In production, configure the publisher properly
    # event_publisher = EventPublisher(...)
    event_publisher = None
    
    return EventGenerator(
        db=db,
        event_factory=event_factory,
        event_repository=event_repository,
        event_publisher=event_publisher
    )


def create_accounting_subscriber(db):
    """Create accounting event subscriber"""
    from .services.accounting_subscriber import AccountingSubscriber
    
    accounting_mapper = AccountingMapper()
    event_repository = EventRepository(db)
    
    return AccountingSubscriber(
        db=db,
        accounting_mapper=accounting_mapper,
        event_repository=event_repository
    )
