from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from openai import OpenAI

from src.services.document_parser import ParsedDocument


@dataclass
class LLMConfig:
    """Конфигурация LLM."""
    api_key: str
    base_url: str
    model: str


class LLMClient:
    """Клиент для работы с OpenAI-совместимым API."""

    def __init__(self, config: LLMConfig) -> None:
        """Создать клиента по конфигурации."""
        self._config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    @classmethod
    def from_env(cls) -> "LLMClient":
        """Создать клиента из переменных окружения."""
        if os.getenv("LLM_STUB") == "1":
            return StubLLMClient()
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_SERVER", "").rstrip("/")
        model = os.getenv("OPENAI_MODEL", "")
        if not api_key or not base_url or not model:
            raise ValueError("OPENAI_API_KEY/OPENAI_SERVER/OPENAI_MODEL не заданы.")
        normalized_base = normalize_base_url(base_url)
        return cls(LLMConfig(api_key=api_key, base_url=normalized_base, model=model))

    def ask(self, role: str, mode: str, question: str, documents: List[ParsedDocument]) -> str:
        """Отправить запрос в LLM."""
        system_prompt = build_system_prompt(role=role, mode=mode)
        document_block = build_document_block(documents)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{document_block}\n\nВопрос: {question}"},
        ]
        try:
            response = self._client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Ошибка запроса к LLM: {exc}") from exc
        return response.choices[0].message.content.strip()

    def improve_prompt(self, role: str, prompt: str) -> str:
        """Сформировать улучшенную версию промта."""
        system_prompt = (
            "Ты помощник по формулировке проверок для договорной документации. "
            "Сделай промт более точным, структурированным и проверяемым. "
            "Верни только улучшенную формулировку, без пояснений."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Роль: {role}\nПромт: {prompt}"},
        ]
        try:
            response = self._client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                temperature=0.3,
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Ошибка запроса к LLM: {exc}") from exc
        return response.choices[0].message.content.strip()


def build_system_prompt(role: str, mode: str) -> str:
    """Сформировать системный промт для режима ответа."""
    role_line = f"Роль пользователя: {role}."
    if mode == "short":
        detail = "Ответь кратко, 1-2 предложения."
    elif mode == "extended":
        detail = "Ответь с кратким обоснованием."
    else:
        detail = (
            "Ответь подробно, включи прямые цитаты и ссылки на страницы "
            "(используй номера PAGE из контекста)."
        )
    return (
        "Ты анализируешь договорную документацию. "
        "Отвечай только на основе предоставленного контекста. "
        f"{role_line} {detail}"
    )


def build_document_block(documents: List[ParsedDocument]) -> str:
    """Собрать текст всех документов в единый блок."""
    parts = []
    for doc in documents:
        parts.append(f"Документ: {doc.name}\n{doc.text}")
    return "\n\n".join(parts)


def normalize_base_url(base_url: str) -> str:
    """Нормализовать base_url до /v1."""
    normalized = base_url.rstrip("/")
    if normalized.endswith("/v1"):
        return normalized
    return f"{normalized}/v1"


class StubLLMClient(LLMClient):
    """Заглушка LLM для тестов и локальной отладки."""

    def __init__(self) -> None:
        """Инициализировать заглушку."""
        self._config = LLMConfig(
            api_key="stub",
            base_url="stub",
            model="stub",
        )
        self._client = None

    def ask(self, role: str, mode: str, question: str, documents: List[ParsedDocument]) -> str:  # type: ignore[override]
        """Вернуть детерминированный ответ для тестов."""
        return (
            "Тестовый ответ. "
            f"Роль: {role}. Режим: {mode}. Вопрос: {question}"
        )

    def improve_prompt(self, role: str, prompt: str) -> str:  # type: ignore[override]
        """Вернуть улучшенный промт без вызова LLM."""
        return f"Улучшенный промт для роли {role}: {prompt}"
