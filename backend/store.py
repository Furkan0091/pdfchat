"""
In-memory store for PDF sessions.

Each session is keyed by a unique fileId and holds the extracted
text plus metadata. In a production app this would be replaced
by Redis or a database, but for a portfolio project in-memory
is clean and sufficient.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PDFSession:
    text: str
    filename: str
    pages: int
    word_count: int
    uploaded_at: datetime = field(default_factory=datetime.utcnow)


class PDFStore:
    def __init__(self):
        self._store: Dict[str, PDFSession] = {}

    def save(self, file_id: str, session: PDFSession) -> None:
        self._store[file_id] = session

    def get(self, file_id: str) -> Optional[PDFSession]:
        return self._store.get(file_id)

    def delete(self, file_id: str) -> bool:
        if file_id in self._store:
            del self._store[file_id]
            return True
        return False

    def exists(self, file_id: str) -> bool:
        return file_id in self._store

    def count(self) -> int:
        return len(self._store)


# Single shared instance used across the app
pdf_store = PDFStore()
