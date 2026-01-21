# TECHNICAL_DOCUMENTATION

## Обзор архитектуры
Приложение построено на FastAPI с серверным рендерингом шаблонов Jinja2 и статическими JS/CSS ассетами. Все данные пользовательских сессий хранятся в памяти, рейтинги логируются на сервере в JSONL.

## Компоненты
- `src/app.py` — FastAPI приложение, API и UI.
- `src/services/document_parser.py` — извлечение текста из файлов.
- `src/services/llm_client.py` — интеграция с Qwen через OpenAI SDK.
- `src/services/session_store.py` — хранение документов по сессии.
- `src/services/rating_logger.py` — запись рейтинга ответов.
- `src/ui/templates/index.html` — UI.
- `src/ui/static/app.js`, `styles.css` — фронтенд логика и стили.

## API
- `POST /api/upload?session_id=...` — загрузка документов.
- `POST /api/chat` — запрос к LLM.
- `POST /api/prompt/improve` — улучшение промта.
- `POST /api/rating` — логирование оценки.
- `GET /api/health` — healthcheck.

## Хранилище данных
- `localStorage`: роль, кастомные проверки, скрытые дефолтные проверки.
- Сервер: `data/logs/ratings.jsonl` (IP, роль, режим, вопрос, оценка).

## Ограничения
- История чата не сохраняется между сессиями.
- Контекст документов обрезается при превышении лимита символов.
- Полный режим ответа — plain text без форматирования.

## Запуск
См. `README.md` для локального запуска и Docker.
