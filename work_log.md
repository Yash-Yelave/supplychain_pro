# Work Log

## 2026-05-15 - Backend Pipeline Fixes & Dynamic Materials Dropdown

### Summary (what changed)
- Fixed backend pipeline crashes:
  - Resolved case-sensitive array search for material categories in `app/crud/suppliers.py` by using `cast(material_categories, String).ilike(...)`.
  - Fixed missing `location` property in `app/procurement/agents/discovery.py` by constructing it from `city`, `region`, and `country_code`.
  - Resolved PostgreSQL enum casting issues by mapping `status` as `String(50)` instead of `Enum` in `app/models/procurement_request.py` and removing the dropped type `procurement_request_status`.
  - Fixed accessing renamed property `deadline` to `shipping_deadline` in `app/procurement/agents/analyst.py`.
- Added new backend endpoint:
  - `GET /procurement/materials` to fetch unique available materials from suppliers.
- Upgraded frontend `RequestForm.tsx`:
  - Converted "Material Type" text input into a dynamic `<select>` dropdown populated from the new backend endpoint.
- Cleaned up backend directory:
  - Moved temporary/test scripts (`check_categories.py`, `check_db.py`, etc.) to `backend/debug_scripts`.

### What was validated
- Pipeline runs successfully end-to-end via manual test script.
- Frontend dropdown correctly populates with materials from database.

## 2026-05-14 - Frontend UI Upgrades & Branching Strategy

### Summary (what changed)
- Upgraded the procurement request form in `frontend/src/components/RequestForm.tsx`:
  - Added "Target Supplier Region" dropdown (Global, UAE, China, India).
  - Added "Quality Grade" dropdown (Standard, Premium, Industrial Grade).
  - Renamed "Deadline" label to "Shipping deadline".
  - Converted "Units" input to a `<select>` dropdown with standard construction units (Tons, Kilograms (kg), Liters, Cubic Meters (cbm), Bags, Pieces).
  - Ensured new fields are included in the API submission payload.
- Implemented a tabbed interface in `frontend/src/pages/Home.tsx`:
  - Tab 1: "Submit Request" (contains the form).
  - Tab 2: "Current Data" (placeholder table for active leads).
- Established a new branching strategy:
  - `main` branch is for production.
  - `stagging` branch is for staging/review before merging to production.
- Pushed the new `stagging` branch to GitHub.

### What was validated
- Frontend components render correctly with new fields and tabs.
- State management updated to handle new form fields.

## 2026-05-11 - Project Restructuring & Deployment Hardening

### Summary (what changed)
- Reorganized the project structure into a clean split: `frontend/` and `backend/` directories.
- Moved all backend-related files (`app/`, `alembic/`, `scripts/`, `venv/`, configs) into the `backend/` folder.
- Audited and updated CORS configuration in `backend/app/main.py` to explicitly allow the production Vercel origin.
- Hardened frontend API client (`src/api/client.ts`) with `try/catch` blocks for better error handling during backend sleep/fail states.
- Patched database connection session handling in `backend/app/db/session.py` to auto-correct Supabase URL schemes (`postgres://` -> `postgresql://`) and enforce `sslmode=require`.
- Added a root health check endpoint (`/`) returning 200 OK in `main.py` to resolve Render deployment loops.
- Unsilenced backend database errors by adding traceback printing to the `SQLAlchemyError` exception handler in `error_handlers.py`.
- Wrapped the `/procurement/request` endpoint with explicit try/except blocks to print tracebacks and return error messages to the client for easier debugging on Render.

### What was validated
- Project successfully restructured without breaking relative paths.

## 2026-05-09 - Frontend Dashboard + Backend Integration

### Summary (what changed)
- Built a minimal, professional React + Vite + TypeScript frontend dashboard in `frontend/`.
- Implemented TailwindCSS for utility-based styling with zero extra bloat.
- Built reusable frontend components: `RequestForm`, `StatusTracker`, `SupplierTable`, `FinalRecommendation`.
- Implemented core frontend pages: `Home.tsx` and `Results.tsx` with React Router.
- Integrated the frontend with the FastAPI backend using Axios and a centralized API client (`src/api/client.ts`).
- Configured FastAPI `CORSMiddleware` in `app/main.py` with dynamic allowed origins (`FRONTEND_CORS_ORIGINS`).
- Replaced hardcoded `localhost` references with environment variables (`VITE_API_BASE_URL`) for deployment readiness.
- Fixed frontend/backend pipeline status enum mismatch (`complete` vs `completed`) and optimized frontend API polling logic with recursive `setTimeout`.
- Created robust deployment and environment configuration documentation:
  - `docs/deployment.md`
  - `frontend/README.md`
  - `frontend/.env.development` and `frontend/.env.production`
  - Updated backend `.env.example`

### What was validated
- Frontend builds cleanly without TypeScript errors (`npm run build`).
- Frontend interacts successfully with backend API across local environments via CORS.
- Polling correctly stops when the pipeline signals `complete`.
- Final recommendation results render effectively.

### How to use (copy/paste)

1) Start Backend (Terminal 1):
```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2) Start Frontend (Terminal 2):
```powershell
cd frontend
npm run dev
```

### Notes / gotchas
- `FRONTEND_CORS_ORIGINS` in the backend must exactly match the frontend URL without trailing slashes.
- Frontend uses `VITE_API_BASE_URL` to dynamically connect to the backend instance.

## 2026-05-08 - FastAPI Backend Layer + API/Pipeline Integration

### Summary (what changed)
- Implemented FastAPI backend entrypoint and API structure for procurement lifecycle:
  - `app/main.py`
  - `app/api/router.py`
  - `app/api/routes/procurement.py`
  - `app/schemas/procurement.py`
  - `app/services/procurement_service.py`
  - `app/middleware/error_handlers.py`
  - `app/dependencies/db.py`
- Added procurement API endpoints:
  - `POST /procurement/request`
  - `GET /procurement/{request_id}/status`
  - `GET /procurement/{request_id}/results`
- Integrated existing multi-agent pipeline into API flow using FastAPI background tasks.
- Added continuation pipeline runners for existing request IDs (so API-created requests can run agents without re-running supervisor):
  - `run_sequential_from_existing_request(...)`
  - `run_langgraph_from_existing_request(...)`
- Added config for orchestration mode selection:
  - `PIPELINE_USE_LANGGRAPH` (default `false`)
- Updated requirements with API/testing dependencies:
  - `fastapi`, `uvicorn`, `requests`
- Added API docs and validation artifacts:
  - `docs/api_overview.md`
  - `docs/api_usage.md`
  - `docs/backend_validation_report.md`
  - `scripts/test_api_flow.py`

### Runtime issues found and fixed
- **QueuePool timeout during background execution** with Supabase-friendly pool (`pool_size=1`, `max_overflow=0`):
  - Root cause: request-scoped session/connection lifecycle clashed with background task DB session demand.
  - Fix: route handlers now use explicit short-lived `SessionLocal()` usage with immediate close; creation route commits and releases promptly before background work progresses.
- **`RuntimeError: Caught handled exception, but response already started`**:
  - Root cause: exception re-raised from background task after response start.
  - Fix: pipeline background failures are persisted as `failed` status and not re-raised to ASGI stack.
- **500 on `POST /procurement/request` after session close**:
  - Root cause: reading ORM attributes from detached/expired instance after closing DB session.
  - Fix: copy response fields (`request_id`, `status`, `current_agent`) before closing session.

### What was validated
- FastAPI server boots successfully with reload.
- `POST /procurement/request` returns `202 Accepted` and enqueues pipeline.
- Python compile checks passed for new API/service modules.
- End-to-end API lifecycle script (`scripts/test_api_flow.py`) is available for local validation.

### How to use (copy/paste)

1) Start server:
```powershell
venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

2) Run API lifecycle validation in another terminal:
```powershell
venv\Scripts\Activate.ps1
python -m scripts.test_api_flow --base-url http://127.0.0.1:8000
```

3) Manual status/results checks:
```powershell
curl http://127.0.0.1:8000/procurement/<REQUEST_ID>/status
curl http://127.0.0.1:8000/procurement/<REQUEST_ID>/results
```

### Notes / gotchas
- Keep `DB_POOL_SIZE=1` and `DB_MAX_OVERFLOW=0` for Supabase free tier; avoid long-lived request sessions that hold the only connection.
- If DeepSeek key is missing/unavailable, extraction falls back to deterministic simulation/local extraction path.
- LangGraph remains optional and controlled by `PIPELINE_USE_LANGGRAPH=true|false`.

## 2026-05-07 - LangGraph Procurement Pipeline + Extraction Reliability Fixes

### Summary (what changed)
- Implemented MVP multi-agent procurement pipeline with optional LangGraph orchestration.
- Added shared, JSON-serializable `ProcurementState` with explicit agent transition logs for debugging.
- Added deterministic supplier trust scoring (configurable weights; no LLM scoring decisions).
- Hardened quotation extraction to avoid "all None / confidence 0" when LLM calls fail:
  - Added token-free local regex pre-extraction (currency/unit price, MOQ, delivery, validity) used before LLM calls and as fallback.
  - Added `DEEPSEEK_DEBUG` debug mode to print request errors and raw model content previews (when available).
- Added Supabase stability knob to disable client-side pooling when using Supabase Session Pooler (`DB_DISABLE_POOLING=1` -> `NullPool`).

### What was validated
- Extraction validation cases now populate required fields via local pre-extraction (so DB persistence is no longer blocked by missing `unit_price`/`currency` when the text contains them).
- Real DeepSeek calls were NOT validated successfully in this environment due to outbound network restrictions:
  - DeepSeek: `WinError 10013` (socket access forbidden) during HTTPS calls.
  - Supabase: direct DB connectivity fails to IPv6 host on port 5432 with permission denied.

### How to use (copy/paste)

1) Validate DB connectivity:
```powershell
venv\Scripts\python -m scripts.verify_database
venv\Scripts\python -m scripts.check_database
```

2) Validate DeepSeek extraction (with debug logs):
```powershell
$env:DEEPSEEK_DEBUG=1
venv\Scripts\python -m scripts.validate_deepseek_extraction
```

3) Run full procurement pipeline:
```powershell
venv\Scripts\python -m scripts.run_procurement_pipeline --material cement
venv\Scripts\python -m scripts.run_procurement_pipeline --material cement --langgraph
```

### Notes / gotchas
- If DeepSeek requests fail with `WinError 10013`, allow outbound HTTPS for Python on your machine/network (or use a network/VPN that permits it) to validate real DeepSeek extraction end-to-end.
- If Supabase direct host fails (often IPv6/port blocked), switch `DATABASE_URL` to Supabase Session Pooler host/port and consider disabling client-side pooling:
```powershell
$env:DB_DISABLE_POOLING=1
```

## 2026-05-06 - Extraction System (DeepSeek + Postgres)

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
- If Supabase direct DB host fails (often IPv6/port blocked), switch `DATABASE_URL` to Supabase Session Pooler host/port.
- Keep prompts short to preserve DeepSeek trial quota; prompt truncation is enabled in `app/extraction/prompts/quotation_prompt.py`.

## 2026-05-05 — Backend Foundation (PostgreSQL + Supabase-compatible)

Project: ConstructProcure AI (backend foundation)

### Summary
Day 1 backend foundation was created: PostgreSQL (Supabase-compatible) persistence with SQLAlchemy models, Alembic migrations, supplier seed data, and basic supplier query utilities. Repository was cleaned to remove the earlier Day 3 extraction prototype and other non-Day-1 artifacts.

### Cleanup
- Removed previous Groq/PDF extraction prototype code and Day 3 test scaffolding because agents/APIs/extraction are out of Day 1 scope.
- Removed empty/placeholder directories and generated Python bytecode artifacts (`__pycache__`, `.pyc`) that were committed previously.
- Replaced the previous secret-bearing `.env` contents with database placeholders and added `.env.example`.
- Kept `docs/` and `data/` reference assets (planning PDFs, workflow image, etc.).

### Backend foundation added
- Environment/config
  - `.python-version` set to `3.11` (note: local shell still uses Python 3.10; this file is the target runtime).
  - `.env` + `.env.example` with Supabase-ready `DATABASE_URL`.
  - `requirements.txt` pinned to minimal backend DB dependencies.
  - `app/core/config.py` for env-based configuration.
- Database wiring
  - `app/db/base.py` Declarative base.
  - `app/db/session.py` SQLAlchemy engine + `SessionLocal`.
- Models (SQLAlchemy)
  - `app/models/supplier.py`
  - `app/models/procurement_request.py`
  - `app/models/quotation.py`
  - `app/models/trust_score.py`
  - `app/models/report.py`
- Migrations (Alembic)
  - `alembic/` initialized with `alembic.ini`.
  - First migration added: `alembic/versions/20260505_0001_create_foundation_tables.py`.
- Seed + queries
  - Seed script: `scripts/seed_suppliers.py` inserts ~30 realistic suppliers with varied categories/locations/templates.
  - Query helpers: `app/crud/suppliers.py`
    - `list_all_suppliers()`
    - `get_supplier_by_id(id)`
    - `get_suppliers_by_category(material_type)`
  - Sanity check script: `scripts/check_database.py`

### Documentation added
- Schema documentation: `docs/database_schema.md` (tables, enums, constraints, indexes, relationships).
- README updated with Day 1 scope and run instructions.

### Database connection verification
Added verifier script: `scripts/verify_database.py`.

Observed result in this environment on 2026-05-05:
- Connection failed with host parse/resolution error: host appeared as `1@db.yjntccgwhskykbbsigrr.supabase.co`.
- Likely root cause: malformed `DATABASE_URL` (typically an unencoded special character in password, especially `@`).
- Fix: ensure `DATABASE_URL` is `postgresql+psycopg://postgres:<URL-ENCODED_PASSWORD>@db...:5432/postgres`.
