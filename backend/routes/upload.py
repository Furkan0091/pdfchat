"""
Upload Router

Handles PDF file upload and text extraction.
Delegates all business logic to pdf_service.
"""

from fastapi import APIRouter, UploadFile, File
from models.schemas import UploadResponse
from services.pdf_service import process_upload

router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("", response_model=UploadResponse)
async def upload_pdf(pdf: UploadFile = File(..., description="PDF file to upload")):
    """
    Upload a PDF file and extract its text content.
    Returns a session fileId to use in subsequent chat requests.
    """
    file_bytes = await pdf.read()
    result = process_upload(
        filename=pdf.filename,
        content_type=pdf.content_type,
        file_bytes=file_bytes,
    )
    return result
