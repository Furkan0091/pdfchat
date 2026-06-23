"""
Chat Router

Handles AI chat requests against an uploaded PDF session.
Delegates AI logic to groq_service.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse, SessionResponse
from services.groq_service import get_ai_response
from store import pdf_store

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Send a message about an uploaded PDF and receive an AI response.
    Requires a valid fileId from a previous upload.
    """
    session = pdf_store.get(req.fileId)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="PDF session not found. Please re-upload your PDF."
        )

    reply = await get_ai_response(
        filename=session.filename,
        pages=session.pages,
        raw_text=session.text,
        history=req.history,
        message=req.message,
    )

    return ChatResponse(reply=reply, filename=session.filename)


@router.get("/session/{file_id}", response_model=SessionResponse)
def get_session(file_id: str):
    """Check if a PDF session is still active."""
    session = pdf_store.get(file_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    return SessionResponse(
        exists=True,
        filename=session.filename,
        pages=session.pages,
        wordCount=session.word_count,
    )
