from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class RatingEntry:
    """Данные о рейтинге ответа."""
    session_id: str
    message_id: str
    rating: str
    role: str
    mode: str
    question: str
    ip: str
    timestamp: str = ""


def log_rating(entry: RatingEntry, log_path: Path) -> None:
    """Сохранить рейтинг в JSONL файле."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry.timestamp = datetime.now(timezone.utc).isoformat()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
