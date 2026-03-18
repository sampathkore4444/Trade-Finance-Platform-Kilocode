"""
Documents Router
Handles HTTP endpoints for document management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.documents.schemas import (
    DocumentUploadResponse,
    DocumentMetadataResponse,
    DocumentUpdate,
    DocumentResponse,
    DocumentType,
    DocumentStatus,
)
from app.modules.documents.services import DocumentService

router = APIRouter(tags=["Documents"])
security = HTTPBearer()


def get_document_service(db=Depends(get_db)):
    """Dependency to get document service"""
    return DocumentService(db)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Upload a document
    """
    document = await service.upload_document(
        file=file,
        document_type=document_type,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=current_user.id,
    )
    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    document_type: Optional[DocumentType] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    status: Optional[DocumentStatus] = None,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    List all documents with optional filters
    """
    documents = await service.list_documents(
        skip=skip,
        limit=limit,
        document_type=document_type,
        entity_type=entity_type,
        entity_id=entity_id,
        status=status,
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Get document metadata by ID
    """
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Download a document
    """
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = await service.get_document_path(document_id)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found",
        )

    return FileResponse(
        path=file_path,
        filename=document.file_name,
        media_type=document.mime_type,
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Update document metadata
    """
    document = await service.update_document(
        document_id=document_id,
        document_data=document_data,
        user_id=current_user.id,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Delete a document
    """
    success = await service.delete_document(
        document_id=document_id,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )


@router.post("/{document_id}/verify", response_model=DocumentResponse)
async def verify_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Mark document as verified
    """
    document = await service.verify_document(
        document_id=document_id,
        user_id=current_user.id,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.post("/{document_id}/reject", response_model=DocumentResponse)
async def reject_document(
    document_id: int,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Reject a document
    """
    document = await service.reject_document(
        document_id=document_id,
        reason=reason,
        user_id=current_user.id,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[DocumentResponse])
async def get_documents_by_entity(
    entity_type: str,
    entity_id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Get all documents for a specific entity
    """
    documents = await service.get_documents_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return documents


@router.get("/pending/list", response_model=List[DocumentResponse])
async def get_pending_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """
    Get all pending documents for review
    """
    documents = await service.get_pending_documents(
        skip=skip,
        limit=limit,
    )
    return documents
