"""
Groq Service

Handles all communication with the Groq API.
Keeping AI logic here means if we ever switch providers
(Groq → OpenAI → Anthropic), only this file changes.
"""

import os
import httpx
from fastapi import HTTPException
from typing import List

from models.schemas import ChatMessage


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
MAX_CHARS    = 8000     # stay within free tier limits
MAX_TOKENS   = 1024
TEMPERATURE  = 0.3
TIMEOUT      = 30.0


def trim_text(text: str, max_chars: int = MAX_CHARS) -> str:
    """Trim PDF text to stay within token limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Document truncated due to length...]"


def build_system_prompt(filename: str, pages: int, pdf_text: str) -> str:
    """Build the system prompt that grounds the AI to the document."""
    return f"""You are a helpful AI assistant that answers questions strictly based on the content of a PDF document provided by the user.

PDF Document: "{filename}"
Pages: {pages}

--- DOCUMENT CONTENT START ---
{pdf_text}
--- DOCUMENT CONTENT END ---

Rules:
1. Only answer questions based on the document content above.
2. If the answer is not found in the document, clearly say "I couldn't find information about that in this document."
3. Be concise, accurate, and well-structured in your responses.
4. When referencing specific parts of the document, mention the context.
5. Never make up or infer information not present in the document."""


def build_messages(
    filename: str,
    pages: int,
    pdf_text: str,
    history: List[ChatMessage],
    current_message: str,
) -> list:
    """Assemble the full messages array for the Groq API call."""
    messages = [
        {
            "role":    "system",
            "content": build_system_prompt(filename, pages, pdf_text),
        }
    ]

    for msg in history:
        messages.append({
            "role":    msg.role,
            "content": msg.content,
        })

    messages.append({"role": "user", "content": current_message})
    return messages


async def get_ai_response(
    filename: str,
    pages: int,
    raw_text: str,
    history: List[ChatMessage],
    message: str,
) -> str:
    """
    Send request to Groq and return the AI's reply text.
    Raises HTTPException on API errors.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured. Check your .env file."
        )

    pdf_text = trim_text(raw_text)
    messages = build_messages(filename, pages, pdf_text, history, message)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       GROQ_MODEL,
                    "messages":    messages,
                    "max_tokens":  MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="The AI request timed out. Please try again."
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Could not reach Groq API: {str(e)}"
            )

    data = response.json()

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid Groq API key.")
    if response.status_code == 429:
        raise HTTPException(status_code=429, detail="Rate limit reached. Please wait a moment.")
    if response.status_code != 200:
        error_msg = data.get("error", {}).get("message", "Unknown Groq API error")
        raise HTTPException(status_code=500, detail=error_msg)

    reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not reply:
        raise HTTPException(status_code=500, detail="Empty response from AI. Please try again.")

    return reply
