"""
Discrepancy Detection Service
Validates documents against references and detects inconsistencies
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class DiscrepancyType(str, Enum):
    AMOUNT_MISMATCH = "amount_mismatch"
    DATE_MISMATCH = "date_mismatch"
    PARTY_MISMATCH = "party_mismatch"
    MISSING_FIELD = "missing_field"
    MISSING_DOCUMENT = "missing_document"
    CONDITION_NOT_MET = "condition_not_met"
    REFERENCE_MISMATCH = "reference_mismatch"


class DiscrepancySeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class DiscrepancyService:
    """Document discrepancy detection engine"""

    @staticmethod
    def parse_amount(text: str) -> Optional[float]:
        """Extract amount from text"""
        patterns = [
            r"([\d,]+\.?\d*)\s*(?:USD|EUR|GBP|JPY|CHF|SGD)",
            r"(?:USD|EUR|GBP|JPY|CHF|SGD)\s*([\d,]+\.?\d*)",
            r"([\d,]+\.\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(",", ""))
                except ValueError:
                    continue
        return None

    @staticmethod
    def parse_date(text: str) -> Optional[str]:
        """Extract and normalize date from text"""
        patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def extract_fields(text: str) -> Dict[str, Any]:
        """Extract key fields from document text"""
        return {
            "amount": DiscrepancyService.parse_amount(text),
            "date": DiscrepancyService.parse_date(text),
            "reference": re.search(
                r"(?:ref|no|number)[:\s#]*([A-Z0-9/-]+)", text, re.IGNORECASE
            ),
        }

    @staticmethod
    def compare_amounts(
        amount1: Optional[float], amount2: Optional[float], tolerance: float = 0.01
    ) -> bool:
        """Compare two amounts with tolerance"""
        if amount1 is None or amount2 is None:
            return True  # Can't compare
        return abs(amount1 - amount2) > tolerance

    @staticmethod
    def detect_discrepancies(
        document: Dict[str, Any], reference: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect discrepancies between document and reference

        Args:
            document: Current document data
            reference: Reference document data

        Returns:
            Discrepancy report
        """
        discrepancies = []

        # Check amount
        doc_amount = document.get("amount") or DiscrepancyService.parse_amount(
            str(document.get("text", ""))
        )
        ref_amount = reference.get("amount") or DiscrepancyService.parse_amount(
            str(reference.get("text", ""))
        )

        if doc_amount and ref_amount:
            if DiscrepancyService.compare_amounts(doc_amount, ref_amount):
                discrepancies.append(
                    {
                        "type": DiscrepancyType.AMOUNT_MISMATCH,
                        "severity": DiscrepancySeverity.CRITICAL,
                        "field": "amount",
                        "document_value": doc_amount,
                        "reference_value": ref_amount,
                        "message": f"Amount mismatch: {doc_amount} vs {ref_amount}",
                    }
                )

        # Check dates
        doc_date = document.get("expiry_date") or document.get("date")
        ref_date = reference.get("expiry_date") or reference.get("date")

        if doc_date and ref_date and doc_date != ref_date:
            discrepancies.append(
                {
                    "type": DiscrepancyType.DATE_MISMATCH,
                    "severity": DiscrepancySeverity.MAJOR,
                    "field": "date",
                    "document_value": doc_date,
                    "reference_value": ref_date,
                    "message": f"Date mismatch: {doc_date} vs {ref_date}",
                }
            )

        # Check parties
        doc_applicant = document.get("applicant_name", "").lower()
        ref_applicant = reference.get("applicant_name", "").lower()

        if doc_applicant and ref_applicant and doc_applicant != ref_applicant:
            discrepancies.append(
                {
                    "type": DiscrepancyType.PARTY_MISMATCH,
                    "severity": DiscrepancySeverity.CRITICAL,
                    "field": "applicant",
                    "document_value": document.get("applicant_name"),
                    "reference_value": reference.get("applicant_name"),
                    "message": f"Applicant mismatch: {document.get('applicant_name')} vs {reference.get('applicant_name')}",
                }
            )

        doc_beneficiary = document.get("beneficiary_name", "").lower()
        ref_beneficiary = reference.get("beneficiary_name", "").lower()

        if doc_beneficiary and ref_beneficiary and doc_beneficiary != ref_beneficiary:
            discrepancies.append(
                {
                    "type": DiscrepancyType.PARTY_MISMATCH,
                    "severity": DiscrepancySeverity.CRITICAL,
                    "field": "beneficiary",
                    "document_value": document.get("beneficiary_name"),
                    "reference_value": reference.get("beneficiary_name"),
                    "message": f"Beneficiary mismatch: {document.get('beneficiary_name')} vs {reference.get('beneficiary_name')}",
                }
            )

        # Check reference number
        doc_ref = document.get("reference_number") or document.get("guarantee_number")
        ref_ref = reference.get("reference_number") or reference.get("guarantee_number")

        if doc_ref and ref_ref and doc_ref != ref_ref:
            discrepancies.append(
                {
                    "type": DiscrepancyType.REFERENCE_MISMATCH,
                    "severity": DiscrepancySeverity.MAJOR,
                    "field": "reference",
                    "document_value": doc_ref,
                    "reference_value": ref_ref,
                    "message": f"Reference mismatch: {doc_ref} vs {ref_ref}",
                }
            )

        # Determine overall status
        if not discrepancies:
            status = "MATCH"
            severity = None
        else:
            status = "DISCREPANCY"
            critical_count = sum(
                1
                for d in discrepancies
                if d["severity"] == DiscrepancySeverity.CRITICAL
            )
            major_count = sum(
                1 for d in discrepancies if d["severity"] == DiscrepancySeverity.MAJOR
            )

            if critical_count > 0:
                severity = DiscrepancySeverity.CRITICAL
            elif major_count > 0:
                severity = DiscrepancySeverity.MAJOR
            else:
                severity = DiscrepancySeverity.MINOR

        return {
            "success": True,
            "status": status,
            "severity": severity.value if severity else None,
            "discrepancy_count": len(discrepancies),
            "discrepancies": discrepancies,
            "recommendation": (
                "REJECT"
                if severity == DiscrepancySeverity.CRITICAL
                else "REVIEW" if severity == DiscrepancySeverity.MAJOR else "APPROVE"
            ),
        }

    @staticmethod
    def check_conditions(
        document_conditions: List[str], required_conditions: List[str]
    ) -> Dict[str, Any]:
        """
        Check if document meets required conditions

        Args:
            document_conditions: Conditions present in document
            required_conditions: Required conditions to check

        Returns:
            Condition check result
        """
        missing_conditions = []

        for req in required_conditions:
            found = False
            for doc_cond in document_conditions:
                if req.lower() in doc_cond.lower():
                    found = True
                    break
            if not found:
                missing_conditions.append(req)

        if missing_conditions:
            return {
                "success": True,
                "status": "CONDITIONS_NOT_MET",
                "missing_conditions": missing_conditions,
                "severity": DiscrepancySeverity.CRITICAL,
                "message": f"Missing required conditions: {', '.join(missing_conditions)}",
            }

        return {
            "success": True,
            "status": "CONDITIONS_MET",
            "missing_conditions": [],
            "severity": None,
            "message": "All required conditions met",
        }

    @staticmethod
    def validate_document_set(
        provided_docs: List[str], required_docs: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that all required documents are provided

        Args:
            provided_docs: List of provided document types
            required_docs: List of required document types

        Returns:
            Validation result
        """
        missing_docs = []

        for req in required_docs:
            found = False
            for doc in provided_docs:
                if req.lower() in doc.lower():
                    found = True
                    break
            if not found:
                missing_docs.append(req)

        if missing_docs:
            return {
                "success": True,
                "status": "INCOMPLETE",
                "missing_documents": missing_docs,
                "severity": DiscrepancySeverity.CRITICAL,
                "message": f"Missing documents: {', '.join(missing_docs)}",
            }

        return {
            "success": True,
            "status": "COMPLETE",
            "missing_documents": [],
            "severity": None,
            "message": "All required documents provided",
        }


# Convenience functions
def detect_discrepancies(
    document: Dict[str, Any], reference: Dict[str, Any]
) -> Dict[str, Any]:
    """Detect discrepancies"""
    return DiscrepancyService.detect_discrepancies(document, reference)


def check_conditions(conditions: List[str], required: List[str]) -> Dict[str, Any]:
    """Check conditions"""
    return DiscrepancyService.check_conditions(conditions, required)


def validate_documents(provided: List[str], required: List[str]) -> Dict[str, Any]:
    """Validate document set"""
    return DiscrepancyService.validate_document_set(provided, required)
