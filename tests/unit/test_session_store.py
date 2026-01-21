from src.services.document_parser import ParsedDocument
from src.services.session_store import SessionStore


def test_session_store_roundtrip() -> None:
    store = SessionStore()
    docs = [ParsedDocument(name="doc", text="text", pages=["text"])]
    store.set_documents("session", docs)

    session = store.get_session("session")
    assert session is not None
    assert session.documents == docs
