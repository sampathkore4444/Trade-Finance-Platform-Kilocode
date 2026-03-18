"""
Smart Engines Router
API endpoints for AI/ML services
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from .services import (
    ocr_service,
    ollama_service,
    compliance_service,
    discrepancy_service,
)

router = APIRouter(prefix="/smart-engines", tags=["Smart Engines"])


# ============== Request/Response Models ==============


class OCRRequest(BaseModel):
    """OCR request model"""

    base64_image: Optional[str] = None
    extract_fields: bool = True


class ClassifyRequest(BaseModel):
    """Document classification request"""

    text: str
    model: Optional[str] = "llama2:7b"


class AnalyzeClausesRequest(BaseModel):
    """Clause analysis request"""

    text: str
    model: Optional[str] = "llama2:13b"


class CheckComplianceRequest(BaseModel):
    """Compliance check request"""

    text: str
    policies: str


class DiscrepancyRequest(BaseModel):
    """Discrepancy detection request"""

    document: Dict[str, Any]
    reference: Dict[str, Any]


class ScreenPartiesRequest(BaseModel):
    """Compliance screening request"""

    parties: List[Dict[str, str]]


class GenerateSummaryRequest(BaseModel):
    """Summary generation request"""

    text: str
    max_length: int = 200


# ============== OCR Endpoints ==============


@router.post("/ocr/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from uploaded document image/PDF
    """
    try:
        contents = await file.read()
        result = ocr_service.OCRService.extract_text_from_bytes(contents)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """
    Complete document analysis: OCR + field extraction
    """
    try:
        contents = await file.read()
        result = ocr_service.OCRService.analyze_document(contents)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Classification Endpoints ==============


@router.post("/classify/document")
async def classify_document(request: ClassifyRequest):
    """
    Classify document type using LLM
    """
    result = ollama_service.classify_document(request.text, request.model)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


# ============== Clause Analysis Endpoints ==============


@router.post("/analyze/clauses")
async def analyze_clauses(request: AnalyzeClausesRequest):
    """
    Analyze document clauses for risk and compliance
    """
    result = ollama_service.analyze_clauses(request.text, request.model)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


# ============== Compliance Endpoints ==============


@router.post("/compliance/screen-name")
async def screen_name(name: str):
    """
    Screen a name against sanctions lists
    """
    result = compliance_service.screen_name(name)
    return result


@router.post("/compliance/screen-country")
async def screen_country(country: str):
    """
    Screen a country for geopolitical risk
    """
    result = compliance_service.screen_country(country)
    return result


@router.post("/compliance/screen-parties")
async def screen_parties(request: ScreenPartiesRequest):
    """
    Screen all parties in a transaction
    """
    result = compliance_service.screen_parties(request.parties)
    return result


@router.post("/compliance/check")
async def check_compliance(request: CheckComplianceRequest):
    """
    Check document against compliance policies using LLM
    """
    result = ollama_service.check_compliance(request.text, request.policies)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


# ============== Discrepancy Endpoints ==============


@router.post("/discrepancy/detect")
async def detect_discrepancies(request: DiscrepancyRequest):
    """
    Detect discrepancies between document and reference
    """
    result = discrepancy_service.detect_discrepancies(
        request.document, request.reference
    )
    return result


@router.post("/discrepancy/check-conditions")
async def check_conditions(conditions: List[str], required: List[str]):
    """
    Check if document meets required conditions
    """
    result = discrepancy_service.check_conditions(conditions, required)
    return result


@router.post("/discrepancy/validate-documents")
async def validate_documents(provided: List[str], required: List[str]):
    """
    Validate that all required documents are provided
    """
    result = discrepancy_service.validate_documents(provided, required)
    return result


# ============== Summary Endpoints ==============


@router.post("/generate/summary")
async def generate_summary(request: GenerateSummaryRequest):
    """
    Generate document summary using LLM
    """
    result = ollama_service.generate_summary(request.text)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


# ============== Health Check ==============


@router.get("/health")
async def health_check():
    """
    Check smart engines availability
    """
    import requests as req

    ollama_status = "unavailable"
    try:
        response = req.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            ollama_status = "available"
            models = response.json().get("models", [])
    except:
        pass

    return {
        "status": "online",
        "services": {
            "ocr": "available (EasyOCR)",
            "ollama": ollama_status,
            "compliance": "available",
            "discrepancy": "available",
        },
    }
