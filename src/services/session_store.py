from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.services.document_parser import ParsedDocument


@dataclass
class SessionData:
    session_id: str
    documents: List[ParsedDocument] = field(default_factory=list)


class SessionStore:
    """Простое хранилище сессий в памяти."""

    def __init__(self) -> None:
        """Инициализировать хранилище."""
        self._sessions: Dict[str, SessionData] = {}

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Получить данные сессии."""
        return self._sessions.get(session_id)

    def set_documents(self, session_id: str, documents: List[ParsedDocument]) -> None:
        """Сохранить документы для сессии."""
        session = self._sessions.get(session_id)
        if session is None:
            session = SessionData(session_id=session_id)
            self._sessions[session_id] = session
        session.documents = documents
