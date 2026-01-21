from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from src.services.document_parser import ParsedDocument, parse_document
from src.services.llm_client import LLMClient
from src.services.rating_logger import RatingEntry, log_rating
from src.services.session_store import SessionStore

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"
DATA_DIR = BASE_DIR.parent / "data"
UPLOADS_DIR = DATA_DIR / "uploads"

load_dotenv(dotenv_path=BASE_DIR.parent / ".env", override=True)

app = FastAPI(title="AI Contract Assistant Prototype")

app.mount("/static", StaticFiles(directory=UI_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(UI_DIR / "templates"))


class DocumentResponse(BaseModel):
    """Ответный формат документа для клиента."""
    name: str
    text: str
    pages: List[str]


class UploadResponse(BaseModel):
    """Ответ загрузки документов."""
    session_id: str
    documents: List[DocumentResponse]


class ChatRequest(BaseModel):
    """Запрос к чату."""
    session_id: str = Field(..., min_length=8)
    message: str = Field(..., min_length=1, max_length=4000)
    role: str = Field(..., min_length=2)
    mode: str = Field(..., pattern="^(short|extended|full)$")


class ChatResponse(BaseModel):
    """Ответ чата."""
    message_id: str
    answer: str


class PromptImproveRequest(BaseModel):
    """Запрос на улучшение промта."""
    prompt: str = Field(..., min_length=3, max_length=4000)
    role: str = Field(..., min_length=2)


class PromptImproveResponse(BaseModel):
    """Ответ с улучшенным промтом."""
    improved_prompt: str


class RatingRequest(BaseModel):
    """Запрос на логирование рейтинга."""
    session_id: str
    message_id: str
    rating: str = Field(..., pattern="^(up|down)$")
    role: str
    mode: str
    question: str


def get_session_store() -> SessionStore:
    """Получить хранилище сессий."""
    if not hasattr(app.state, "session_store"):
        app.state.session_store = SessionStore()
    return app.state.session_store


def get_llm_client() -> LLMClient:
    """Получить LLM-клиент."""
    if not hasattr(app.state, "llm_client"):
        app.state.llm_client = LLMClient.from_env()
    return app.state.llm_client


def get_rating_log_path() -> Path:
    """Получить путь к файлу логирования рейтинга."""
    if not hasattr(app.state, "rating_log_path"):
        app.state.rating_log_path = DATA_DIR / "logs" / "ratings.jsonl"
    return app.state.rating_log_path


def validate_uploads(files: List[UploadFile]) -> None:
    """Проверить количество загружаемых файлов."""
    if not 1 <= len(files) <= 5:
        raise HTTPException(status_code=400, detail="Можно загрузить от 1 до 5 файлов.")


def validate_file_size(file_bytes: bytes, filename: str) -> None:
    """Проверить размер одного файла."""
    max_bytes = 10 * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Файл {filename} превышает 10 МБ.",
        )


def ensure_uploads_dir() -> None:
    """Создать директорию для загрузок."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Вернуть стартовую страницу UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(
    session_id: str,
    files: List[UploadFile] = File(...),
) -> UploadResponse:
    """Загрузить и распарсить документы."""
    validate_uploads(files)
    ensure_uploads_dir()

    parsed_docs: List[ParsedDocument] = []
    for upload in files:
        file_bytes = await upload.read()
        validate_file_size(file_bytes, upload.filename)
        stored_name = f"{uuid4().hex}_{upload.filename}"
        file_path = UPLOADS_DIR / stored_name
        file_path.write_bytes(file_bytes)
        parsed_docs.append(parse_document(file_path, upload.filename))

    session_store = get_session_store()
    session_store.set_documents(session_id, parsed_docs)

    response_docs = [
        DocumentResponse(name=doc.name, text=doc.text, pages=doc.pages)
        for doc in parsed_docs
    ]
    return UploadResponse(session_id=session_id, documents=response_docs)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Отправить вопрос в LLM с контекстом документов."""
    session_store = get_session_store()
    session = session_store.get_session(request.session_id)
    if session is None or not session.documents:
        raise HTTPException(status_code=400, detail="Сначала загрузите документы.")

    llm_client = get_llm_client()
    try:
        answer = llm_client.ask(
            role=request.role,
            mode=request.mode,
            question=request.message,
            documents=session.documents,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(message_id=uuid4().hex, answer=answer)


@app.post("/api/prompt/improve", response_model=PromptImproveResponse)
async def improve_prompt(request: PromptImproveRequest) -> PromptImproveResponse:
    """Улучшить промт проверки."""
    llm_client = get_llm_client()
    try:
        improved = llm_client.improve_prompt(role=request.role, prompt=request.prompt)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return PromptImproveResponse(improved_prompt=improved)


@app.post("/api/rating")
async def rate_answer(request: RatingRequest, raw_request: Request) -> dict:
    """Логировать оценку ответа."""
    entry = RatingEntry(
        session_id=request.session_id,
        message_id=request.message_id,
        rating=request.rating,
        role=request.role,
        mode=request.mode,
        question=request.question,
        ip=raw_request.client.host if raw_request.client else "unknown",
    )
    log_rating(entry, get_rating_log_path())
    return {"status": "ok"}


@app.get("/api/health")
async def health() -> dict:
    """Проверка доступности сервиса."""
    return {"status": "ok"}


@app.get("/api/env-check")
async def env_check() -> dict:
    """Проверить, что переменные окружения загружены."""
    def mask(value: Optional[str]) -> str:
        if not value:
            return ""
        return f"{value[:2]}***{value[-2:]}"

    return {
        "OPENAI_API_KEY": mask(os.getenv("OPENAI_API_KEY")),
        "OPENAI_SERVER": os.getenv("OPENAI_SERVER", ""),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", ""),
    }


def main() -> None:
    """Локальный запуск приложения."""
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
