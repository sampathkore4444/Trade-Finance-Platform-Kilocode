"""
OCR Service using EasyOCR
Best open-source OCR library for document extraction
"""

import io
import base64
from typing import Optional, Dict, Any, List
import easyocr
from PIL import Image
import numpy as np

# Initialize EasyOCR reader (lazy loading)
# Using English and common trade finance languages
_reader: Optional[easyocr.Reader] = None


def get_reader() -> easyocr.Reader:
    """Get or create EasyOCR reader instance"""
    global _reader
    if _reader is None:
        # Initialize with English - can add more languages as needed
        _reader = easyocr.Reader(["en"], gpu=True, verbose=False)
    return _reader


class OCRService:
    """OCR Engine for document processing"""

    @staticmethod
    def extract_text_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from image bytes

        Args:
            image_bytes: Raw image data

        Returns:
            Dictionary with extracted text, confidence scores, and bounding boxes
        """
        try:
            # Convert bytes to numpy array for EasyOCR
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)

            # Run OCR
            reader = get_reader()
            results = reader.readtext(image_array)

            # Parse results
            extracted_text = []
            detailed_results = []

            for bbox, text, confidence in results:
                extracted_text.append(text)
                detailed_results.append(
                    {"text": text, "confidence": round(confidence, 4), "bbox": bbox}
                )

            return {
                "success": True,
                "full_text": " ".join(extracted_text),
                "lines": extracted_text,
                "details": detailed_results,
                "word_count": len(extracted_text),
                "avg_confidence": (
                    round(
                        sum(r["confidence"] for r in detailed_results)
                        / len(detailed_results),
                        4,
                    )
                    if detailed_results
                    else 0
                ),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "full_text": "",
                "lines": [],
                "details": [],
            }

    @staticmethod
    def extract_text_from_base64(base64_string: str) -> Dict[str, Any]:
        """
        Extract text from base64 encoded image

        Args:
            base64_string: Base64 encoded image string

        Returns:
            Dictionary with extracted text
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]

            image_bytes = base64.b64decode(base64_string)
            return OCRService.extract_text_from_bytes(image_bytes)

        except Exception as e:
            return {"success": False, "error": str(e), "full_text": ""}

    @staticmethod
    def extract_fields_from_text(full_text: str) -> Dict[str, Any]:
        """
        Extract key fields from OCR text using pattern matching

        Args:
            full_text: Extracted text from OCR

        Returns:
            Dictionary with extracted fields
        """
        import re

        fields = {
            "bank_name": None,
            "beneficiary": None,
            "applicant": None,
            "amount": None,
            "currency": None,
            "expiry_date": None,
            "issue_date": None,
            "document_type": None,
            "reference_number": None,
        }

        # Amount pattern (e.g., USD 100,000 or 100,000 USD)
        amount_pattern = r"(USD|EUR|GBP|JPY|CHF|SGD)\s*([\d,]+(?:\.\d{2})?)"
        amount_match = re.search(amount_pattern, full_text, re.IGNORECASE)
        if amount_match:
            fields["currency"] = amount_match.group(1).upper()
            fields["amount"] = amount_match.group(2).replace(",", "")

        # Date patterns
        date_patterns = [
            (r"expiry\s*(?:date)?:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "expiry_date"),
            (r"issue\s*(?:date)?:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "issue_date"),
            (
                r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
                "expiry_date",
            ),
        ]

        for pattern, field_name in date_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                fields[field_name] = match.group(1)
                break

        # Reference number patterns
        ref_patterns = [
            r"(?:sb|lc|bg|guarantee)\s*(?:no|number|#)?:?\s*([A-Z0-9/-]+)",
            r"(?:reference|ref)\s*(?:no|number|#)?:?\s*([A-Z0-9/-]+)",
        ]

        for pattern in ref_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                fields["reference_number"] = match.group(1)
                break

        return fields

    @staticmethod
    def analyze_document(image_bytes: bytes) -> Dict[str, Any]:
        """
        Complete document analysis: OCR + field extraction

        Args:
            image_bytes: Raw image data

        Returns:
            Complete analysis result
        """
        # Step 1: Extract text
        ocr_result = OCRService.extract_text_from_bytes(image_bytes)

        if not ocr_result.get("success"):
            return ocr_result

        # Step 2: Extract structured fields
        fields = OCRService.extract_fields_from_text(ocr_result["full_text"])

        return {
            "success": True,
            "ocr": ocr_result,
            "extracted_fields": fields,
            "document_type": fields.get("document_type", "Unknown"),
        }


# Convenience functions
def extract_text(image_bytes: bytes) -> str:
    """Quick text extraction"""
    result = OCRService.extract_text_from_bytes(image_bytes)
    return result.get("full_text", "")


def analyze_document(image_bytes: bytes) -> Dict[str, Any]:
    """Complete document analysis"""
    return OCRService.analyze_document(image_bytes)
