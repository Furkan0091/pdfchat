from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    fileId: str = Field(..., description="Session ID returned after PDF upload")
    message: str = Field(..., min_length=1, description="User's question")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Previous messages")


class UploadResponse(BaseModel):
    fileId: str
    filename: str
    pages: int
    wordCount: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    filename: str


class SessionResponse(BaseModel):
    exists: bool
    filename: str
    pages: int
    wordCount: int


class ErrorResponse(BaseModel):
    detail: str
