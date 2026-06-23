"""
PDFChat API — Main Entry Point

This file is intentionally minimal. It only handles:
- App initialization
- Middleware configuration
- Router registration

All business logic lives in services/
All route handlers live in routes/
All data models live in models/
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.upload import router as upload_router
from routes.chat import router as chat_router

load_dotenv()

app = FastAPI(
    title="PDFChat API",
    description="Upload a PDF and chat with it using Groq AI (LLaMA 3.3)",
    version="1.0.0",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "PDFChat API is running"}
