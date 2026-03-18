"""
Accounting Mapper
Maps trade events to accounting entries for Core Banking System
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GLAccountConfig:
    """GL Account configuration"""
    
    # Default GL Account codes (these would come from configuration)
    DEFAULT_ACCOUNTS = {
        # LC Accounts
        "LC_CONTINGENT": {"code": "20100", "type": "GL", "name": "LC Contingent Liability"},
        "LC_PAID": {"code": "20101", "type": "GL", "name": "LC Paid Liability"},
        "LC_SETTLED": {"code": "20102", "type": "GL", "name": "LC Settled"},
        
        # Guarantee Accounts
        "GUARANTEE_CONTINGENT": {"code": "20200", "type": "GL", "name": "Guarantee Contingent"},
        "GUARANTEE_PAID": {"code": "20201", "type": "GL", "name": "Guarantee Paid"},
        
        # Loan Accounts
        "LOAN_RECEIVABLE": {"code": "10100", "type": "GL", "name": "Loan Receivable"},
        "LOAN_INTEREST_RECEIVABLE": {"code": "10101", "type": "GL", "name": "Interest Receivable"},
        "NPL_PROVISION": {"code": "20250", "type": "GL", "name": "NPL Provision"},
        
        # Income Accounts
        "INTEREST_INCOME": {"code": "40100", "type": "GL", "name": "Interest Income"},
        "COMMISSION_INCOME": {"code": "40200", "type": "GL", "name": "Commission Income"},
        "FEE_INCOME": {"code": "40201", "type": "GL", "name": "Fee Income"},
        
        # Nostro Accounts (per currency)
        "USD_NOSTRO": {"code": "10001", "type": "NOSTRO", "name": "USD Nostro"},
        "EUR_NOSTRO": {"code": "10002", "type": "NOSTRO", "name": "EUR NostRO"},
        "GBP_NOSTRO": {"code": "10003", "type": "NOSTRO", "name": "GBP Nostro"},
        "DEFAULT_NOSTRO": {"code": "10000", "type": "NOSTRO", "name": "Default Nostro"},
    }
    
    def __init__(self, custom_accounts: Optional[Dict[str, Dict]] = None):
        self.accounts = {**self.DEFAULT_ACCOUNTS}
        if custom_accounts:
            self.accounts.update(custom_accounts)
    
    def get_gl(self, account_key: str) -> Dict[str, Any]:
        """Get GL account by key"""
        account = self.accounts.get(account_key, self.accounts["DEFAULT_NOSTRO"])
        return {
            "type": account["type"],
            "account_code": account["code"],
            "name": account["name"]
        }
    
    def get_nostro(self, currency: str) -> Dict[str, Any]:
        """Get Nostro account for currency"""
        key = f"{currency}_NOSTRO"
        account = self.accounts.get(key, self.accounts["DEFAULT_NOSTRO"])
        return {
            "type": "NOSTRO",
            "account_code": account["code"],
            "currency": currency,
            "name": account["name"]
        }


class AccountingMapper:
    """
    Maps trade events to accounting entries
    """
    
    # Event to accounting entry mapping
    MAPPING_RULES = {
        # LC Events
        "LC_ISSUED": [
            {
                "entry_type": "CONTINGENT_LIABILITY",
                "debit_gl_key": None,  # No debit for contingent liability creation
                "credit_gl_key": "LC_CONTINGENT",
                "narrative_template": "LC {lcReference} - Issue - {currency} {amount}"
            },
            {
                "entry_type": "COMMISSION_INCOME",
                "debit_gl_key": "COMMISSION_RECEIVABLE",
                "credit_gl_key": "COMMISSION_INCOME",
                "narrative_template": "LC {lcReference} - Commission Income"
            }
        ],
        "LC_UTILISED": [
            {
                "entry_type": "UTILISATION_CONTINGENT",
                "debit_gl_key": "LC_CONTINGENT",
                "credit_gl_key": "LC_PAID",
                "narrative_template": "LC {lcReference} - Utilisation - {currency} {amount}"
            },
            {
                "entry_type": "NOSTRO_OUT",
                "debit_gl_key": None,
                "credit_gl_key": "SETTLEMENT",
                "narrative_template": "LC {lcReference} - Payment - {currency} {amount}"
            }
        ],
        "LC_SETTLED": [
            {
                "entry_type": "SETTLEMENT",
                "debit_gl_key": "LC_PAID",
                "credit_gl_key": "LC_CONTINGENT",
                "narrative_template": "LC {lcReference} - Settlement - {currency} {amount}"
            }
        ],
        
        # Guarantee Events
        "GUARANTEE_ISSUED": [
            {
                "entry_type": "GUARANTEE_CONTINGENT",
                "debit_gl_key": None,
                "credit_gl_key": "GUARANTEE_CONTINGENT",
                "narrative_template": "Guarantee {guaranteeReference} - Issue - {currency} {amount}"
            }
        ],
        "GUARANTEE_CLAIMED": [
            {
                "entry_type": "GUARANTEE_CLAIM",
                "debit_gl_key": "GUARANTEE_CONTINGENT",
                "credit_gl_key": "GUARANTEE_PAID",
                "narrative_template": "Guarantee {guaranteeReference} - Claim - {currency} {amount}"
            }
        ],
        "GUARANTEE_PAID": [
            {
                "entry_type": "GUARANTEE_PAYMENT",
                "debit_gl_key": "GUARANTEE_PAID",
                "credit_gl_key": "SETTLEMENT",
                "narrative_template": "Guarantee {guaranteeReference} - Payment - {currency} {amount}"
            }
        ],
        "GUARANTEE_RELEASED": [
            {
                "entry_type": "GUARANTEE_RELEASE",
                "debit_gl_key": "GUARANTEE_CONTINGENT",
                "credit_gl_key": "SETTLEMENT",
                "narrative_template": "Guarantee {guaranteeReference} - Release - {currency} {amount}"
            }
        ],
        
        # Trade Loan Events
        "TRADE_LOAN_DISBURSED": [
            {
                "entry_type": "LOAN_DISBURSEMENT",
                "debit_gl_key": "LOAN_RECEIVABLE",
                "credit_gl_key": "SETTLEMENT",
                "narrative_template": "Loan {loanReference} - Disbursement - {currency} {amount}"
            }
        ],
        "TRADE_LOAN_REPAID": [
            {
                "entry_type": "LOAN_REPAYMENT",
                "debit_gl_key": "SETTLEMENT",
                "credit_gl_key": "LOAN_RECEIVABLE",
                "narrative_template": "Loan {loanReference} - Repayment - {currency} {amount}"
            },
            {
                "entry_type": "INTEREST_INCOME",
                "debit_gl_key": "SETTLEMENT",
                "credit_gl_key": "INTEREST_INCOME",
                "narrative_template": "Loan {loanReference} - Interest - {currency} {interestAmount}"
            }
        ],
        "TRADE_LOAN_DEFAULTED": [
            {
                "entry_type": "LOAN_DEFAULT",
                "debit_gl_key": "NPL_PROVISION",
                "credit_gl_key": "LOAN_RECEIVABLE",
                "narrative_template": "Loan {loanReference} - Default - {currency} {amount}"
            }
        ]
    }
    
    def __init__(self, gl_config: Optional[GLAccountConfig] = None):
        self.gl_config = gl_config or GLAccountConfig()
    
    def map_to_entries(self, event) -> List[Dict[str, Any]]:
        """
        Map event to accounting entries
        
        Args:
            event: Event object
        
        Returns:
            List of accounting entries
        """
        event_type = event.event_type
        payload = event.payload
        
        # Get mapping rules for this event type
        rules = self.MAPPING_RULES.get(event_type, [])
        
        if not rules:
            logger.warning(f"No accounting mapping found for event type: {event_type}")
            return []
        
        entries = []
        for rule in rules:
            entry = self._build_entry(rule, payload)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _build_entry(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build a single accounting entry from rule and payload"""
        try:
            # Get narrative
            narrative = rule["narrative_template"].format(**payload)
            
            # Get amount from payload
            amount = payload.get("amount", "0")
            
            # Build entry
            entry = {
                "entryType": rule["entry_type"],
                "amount": amount,
                "currency": payload.get("currency", "USD"),
                "narrative": narrative,
                "valueDate": payload.get("issueDate") or payload.get("disbursementDate")
            }
            
            # Add debit account if specified
            if rule.get("debit_gl_key"):
                entry["debitAccount"] = self.gl_config.get_gl(rule["debit_gl_key"])
            else:
                # For Nostro accounts, use currency from payload
                entry["debitAccount"] = self.gl_config.get_nostro(payload.get("currency", "USD"))
            
            # Add credit account if specified
            if rule.get("credit_gl_key"):
                entry["creditAccount"] = self.gl_config.get_gl(rule["credit_gl_key"])
            else:
                entry["creditAccount"] = self.gl_config.get_nostro(payload.get("currency", "USD"))
            
            return entry
            
        except KeyError as e:
            logger.error(f"Missing required field in payload: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error building entry: {str(e)}")
            return None
    
    def get_idempotency_key(self, event) -> str:
        """Generate idempotency key for accounting"""
        return f"idemp_{event.event_type}_{event.payload.get('lcReference') or event.payload.get('guaranteeReference') or event.payload.get('loanReference')}_{event.event_id}"
