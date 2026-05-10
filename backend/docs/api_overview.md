# ConstructProcure AI API Overview

## Architecture

- `app/main.py`: FastAPI application entrypoint.
- `app/api/routes/procurement.py`: procurement HTTP endpoints.
- `app/schemas/procurement.py`: request/response models.
- `app/services/procurement_service.py`: API service logic + pipeline trigger.
- `app/dependencies/db.py`: SQLAlchemy session dependency.
- `app/middleware/error_handlers.py`: HTTP + DB error handlers.

## Pipeline Integration Model

- `POST /procurement/request` persists a procurement request immediately.
- Pipeline execution starts in a FastAPI background task.
- Default mode is sequential agents.
- LangGraph execution is optional via `PIPELINE_USE_LANGGRAPH=true`.
- Status is persisted on `procurement_requests.status/current_agent`.

## Status Lifecycle

- `in_progress`: request accepted and pipeline running.
- `complete`: pipeline finished and report persisted.
- `failed`: pipeline failed (validation/discovery/extraction/etc).

## Supabase/DeepSeek Optimizations

- DB pool defaults remain free-tier friendly: `pool_size=1`, `max_overflow=0`.
- Optional `DB_DISABLE_POOLING=true` for transaction-pooler setups.
- Extraction keeps local parsing first and only calls DeepSeek when needed.
- DeepSeek calls are bounded by timeout and retry limits from env config.
