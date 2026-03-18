"""
Ollama LLM Service
Using small local models for document analysis and classification
"""

import requests
from typing import Optional, Dict, Any, List
from enum import Enum

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama2:7b"
LARGE_MODEL = "llama2:13b"


class DocumentType(str, Enum):
    SBLC = "SBLC"
    AMENDMENT = "Amendment"
    CLAIM = "Claim"
    INVOICE = "Invoice"
    BILL_OF_LADING = "Bill of Lading"
    CREDIT_NOTE = "Credit Note"
    DEBIT_NOTE = "Debit Note"
    GUARANTEE = "Guarantee"
    LETTER_OF_CREDIT = "Letter of Credit"
    OTHER = "Other"


class OllamaService:
    """LLM Engine using Ollama for local inference"""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.base_url = OLLAMA_BASE_URL

    def _call_ollama(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call Ollama API

        Args:
            prompt: User prompt
            system_prompt: System instructions

        Returns:
            Model response
        """
        try:
            payload = {"model": self.model, "prompt": prompt, "stream": False}

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=120
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json().get("response", ""),
                    "model": self.model,
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}",
                    "details": response.text,
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to Ollama. Make sure it's running on localhost:11434",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Classify document type using LLM

        Args:
            text: Document text content

        Returns:
            Classification result with confidence
        """
        system_prompt = """You are a document classification expert for trade finance.
Classify the document into one of these categories:
- SBLC (Standby Letter of Credit)
- Amendment
- Claim
- Invoice
- Bill of Lading
- Guarantee
- Letter of Credit
- Other

Respond ONLY with the category name and a brief justification."""

        prompt = f"""Classify this trade finance document:

{text[:2000]}

Category:"""

        result = self._call_ollama(prompt, system_prompt)

        if result.get("success"):
            response = result["response"].strip()
            # Extract just the category
            categories = [d.value for d in DocumentType]
            detected = next(
                (c for c in categories if c.lower() in response.lower()), "Other"
            )

            return {
                "success": True,
                "document_type": detected,
                "justification": response,
                "model": self.model,
            }

        return result

    def analyze_clauses(self, text: str) -> Dict[str, Any]:
        """
        Analyze document clauses for risk and compliance

        Args:
            text: Document text content

        Returns:
            Clause analysis with risk scores
        """
        system_prompt = """You are a legal document analyst specializing in trade finance.
Analyze the clauses in the document and identify:
1. Key clauses and their meanings
2. Potential risks or ambiguous language
3. Non-standard terms
4. Compliance issues

Provide a structured analysis."""

        prompt = f"""Analyze these clauses from a trade finance document:

{text[:3000]}

Analysis:"""

        result = self._call_ollama(prompt, system_prompt)

        if result.get("success"):
            return {
                "success": True,
                "analysis": result["response"],
                "model": self.model,
            }

        return result

    def detect_discrepancies(
        self, document_text: str, reference_text: str
    ) -> Dict[str, Any]:
        """
        Detect discrepancies between document and reference

        Args:
            document_text: Current document text
            reference_text: Reference document text

        Returns:
            Discrepancy report
        """
        system_prompt = """You are a document verification expert.
Compare the two documents and identify:
1. Missing required documents/fields
2. Inconsistent dates, amounts, or parties
3. Terms that don't match
4. Any other discrepancies

Be thorough and specific."""

        prompt = f"""Compare this document:

=== DOCUMENT ===
{document_text[:2000]}

=== REFERENCE ===
{reference_text[:2000]}

Discrepancies found:"""

        result = self._call_ollama(prompt, system_prompt)

        if result.get("success"):
            return {
                "success": True,
                "discrepancies": result["response"],
                "model": self.model,
            }

        return result

    def generate_summary(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        """
        Generate document summary

        Args:
            text: Document text
            max_length: Maximum summary length in words

        Returns:
            Summary text
        """
        system_prompt = f"""You are a document summarizer.
Provide a concise summary in no more than {max_length} words.
Focus on key parties, amounts, dates, and obligations."""

        prompt = f"""Summarize this document:

{text[:3000]}

Summary:"""

        result = self._call_ollama(prompt, system_prompt)

        if result.get("success"):
            return {"success": True, "summary": result["response"], "model": self.model}

        return result

    def check_compliance(self, text: str, policies: str) -> Dict[str, Any]:
        """
        Check document against compliance policies

        Args:
            text: Document text
            policies: Compliance policies to check against

        Returns:
            Compliance check results
        """
        system_prompt = """You are a compliance checking system.
Evaluate the document against the given policies.
Identify any violations or concerns."""

        prompt = f"""Check this document against the policies:

=== POLICIES ===
{policies[:1000]}

=== DOCUMENT ===
{text[:2000]}

Compliance Status:"""

        result = self._call_ollama(prompt, system_prompt)

        if result.get("success"):
            return {
                "success": True,
                "compliance_report": result["response"],
                "model": self.model,
            }

        return result

    def explain_decision(self, decision: str, context: str) -> Dict[str, Any]:
        """
        Explain an AI decision in human-readable terms

        Args:
            decision: The decision made
            context: Context and reasoning

        Returns:
            Explanation
        """
        system_prompt = """Explain this decision in simple terms that a non-technical user can understand."""

        prompt = f"""Context: {context[:1000]}

Decision: {decision}

Explanation:"""

        result = self._call_ollama(prompt, system_prompt)

        if result.get("success"):
            return {
                "success": True,
                "explanation": result["response"],
                "model": self.model,
            }

        return result


# Convenience functions
def classify_document(text: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Classify document type"""
    service = OllamaService(model)
    return service.classify_document(text)


def analyze_clauses(text: str, model: str = LARGE_MODEL) -> Dict[str, Any]:
    """Analyze document clauses"""
    service = OllamaService(model)
    return service.analyze_clauses(text)


def detect_discrepancies(doc_text: str, ref_text: str) -> Dict[str, Any]:
    """Detect discrepancies"""
    service = OllamaService(LARGE_MODEL)
    return service.detect_discrepancies(doc_text, ref_text)


def generate_summary(text: str) -> Dict[str, Any]:
    """Generate summary"""
    service = OllamaService()
    return service.generate_summary(text)


def check_compliance(text: str, policies: str) -> Dict[str, Any]:
    """Check compliance"""
    service = OllamaService(LARGE_MODEL)
    return service.check_compliance(text, policies)
