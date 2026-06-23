"""
PDF Service

Responsible for reading and extracting text from uploaded PDF files.
Keeps all PDF-related logic isolated from the route layer.
"""

import io
import uuid
import PyPDF2
from fastapi import HTTPException

from store import pdf_store, PDFSession


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIN_TEXT_LENGTH = 10


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """
    Extract raw text from PDF bytes using PyPDF2.
    Returns (extracted_text, page_count).
    Raises HTTPException if extraction fails.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        page_count = len(reader.pages)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()
        return full_text, page_count

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse PDF: {str(e)}"
        )


def validate_upload(filename: str, content_type: str, file_bytes: bytes) -> None:
    """Validate file type and size before processing."""
    if content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be under 10MB."
        )


def process_upload(filename: str, content_type: str, file_bytes: bytes) -> dict:
    """
    Full upload pipeline:
    1. Validate file
    2. Extract text
    3. Store session
    4. Return metadata
    """
    validate_upload(filename, content_type, file_bytes)

    extracted_text, page_count = extract_text_from_pdf(file_bytes)

    if len(extracted_text) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from this PDF. It may be scanned or image-based."
        )

    word_count = len(extracted_text.split())
    file_id = f"pdf_{uuid.uuid4().hex}"

    session = PDFSession(
        text=extracted_text,
        filename=filename,
        pages=page_count,
        word_count=word_count,
    )

    pdf_store.save(file_id, session)

    return {
        "fileId":    file_id,
        "filename":  filename,
        "pages":     page_count,
        "wordCount": word_count,
        "message":   "PDF uploaded and processed successfully",
    }
