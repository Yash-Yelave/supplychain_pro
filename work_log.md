# Work Log

## 2026-05-06 — Extraction System (DeepSeek + Postgres)

### Summary (what changed)
- Implemented the extraction module skeleton under `app/extraction/` (schemas, prompts, services, validators, pipeline, simulation).
- Added DeepSeek (OpenAI-compatible) client with retries/timeouts and hardened JSON parsing.
- Built a realistic-but-short quote simulator using DB-stored supplier templates.
- Added extraction persistence into PostgreSQL (`quotations`) including `raw_text`, `missing_fields`, `extraction_confidence`, and `notes`.
- Added Alembic migration to add `quotations.notes`.
- Added DB connection pooling knobs for Supabase free tier (`DB_POOL_SIZE=1`, `DB_MAX_OVERFLOW=0`).
- Added test runners:
  - `scripts/test_extraction.py` (simulation-based, optional DB insert)
  - `scripts/validate_deepseek_extraction.py` (real DeepSeek validation with 5 cases, optional DB insert)
- Added database documentation tooling:
  - `docs/database.md` (narrative)
  - `docs/database_schema.md` (generated snapshot)
  - `scripts/gen_db_docs.py` (generator)
- Added DeepSeek usage documentation: `docs/deepseek_extraction_setup.md`

### How to use (copy/paste)

1) Install dependencies:
```powershell
venv\Scripts\pip install -r requirements.txt
```

2) Run migrations (creates/updates tables):
```powershell
venv\Scripts\python -m alembic upgrade head
```

3) Seed suppliers (required for simulation demos):
```powershell
venv\Scripts\python -m scripts.seed_suppliers
```

4) Set DeepSeek key in `.env`:
```env
DEEPSEEK_API_KEY=YOUR_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

5) Run extraction demo (simulation-based):
- Dry run (prints results, no inserts):
```powershell
venv\Scripts\python -m scripts.test_extraction --material cement
```
- Persist (inserts into `quotations` when unit_price+currency are present):
```powershell
venv\Scripts\python -m scripts.test_extraction --material cement --persist
```

6) Run real DeepSeek validation (5 cases):
```powershell
venv\Scripts\python -m scripts.validate_deepseek_extraction
```

### Notes / gotchas
- If you see `Missing DEEPSEEK_API_KEY`, ensure `.env` has `DEEPSEEK_API_KEY=...` and you run via `venv\Scripts\python ...` (the validation script loads `.env`).
- If Supabase direct DB host fails (often IPv6/port blocked), switch `DATABASE_URL` to Supabase **Session Pooler** host/port.
- Keep prompts short to preserve DeepSeek trial quota; prompt truncation is enabled in `app/extraction/prompts/quotation_prompt.py`.

