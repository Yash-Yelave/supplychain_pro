# DeepSeek V3 Extraction Setup (ConstructProcure AI)

This project uses **DeepSeek (OpenAI-compatible chat API)** to extract structured quotation fields from messy supplier messages, then validates and (optionally) persists results into PostgreSQL (Supabase-hosted).

## 1) Overview

**Purpose**
- Convert unstructured supplier quotations (emails / WhatsApp-like replies) into **strict JSON** fields.
- Validate and score extraction quality (confidence + missing fields).
- Persist into the existing `quotations` table (`raw_text`, extracted fields, `missing_fields`, `extraction_confidence`, `notes`).

**Token optimization strategy**
- Keep prompts short and extraction-only (no examples).
- Truncate long supplier text before sending to the model.
- Force output to a single JSON object with fixed keys.
- Low `max_tokens` and deterministic `temperature=0`.
- Avoid retries unless a request fails (network/429/5xx).

## 2) Environment Setup

Add these to `.env` (see `.env.example`):

```env
DEEPSEEK_API_KEY=YOUR_KEY_HERE
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT_S=20
DEEPSEEK_MAX_RETRIES=2
```

Database (Supabase Postgres):

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR-PASSWORD@YOUR-HOST:5432/postgres
DB_POOL_SIZE=1
DB_MAX_OVERFLOW=0
DB_POOL_TIMEOUT_S=30
DB_DISABLE_POOLING=0
```

Notes:
- If your password contains special characters, URL-encode them (example: `@` → `%40`).
- If you cannot connect to Supabase direct host (common on some networks/IPv6 paths), use Supabase **Session Pooler** host/port and keep the `postgresql+psycopg://` prefix.
- When using the Supabase Session Pooler, you can set `DB_DISABLE_POOLING=1` to avoid holding connections on the client side (the pooler already multiplexes connections).

## 3) How the Extraction Pipeline Works

**A) Quote simulation (demo)**
- Uses supplier templates stored in `suppliers.simulated_reply_template`.
- Adds short “Rate / MOQ / Delivery / Validity / Payment” lines with noisy formatting.
- Module: `app/extraction/simulation/quote_generator.py`

**B) DeepSeek extraction**
- Prompt is split into:
  - System prompt (fixed, compact): `app/extraction/prompts/quotation_prompt.py`
  - User prompt (truncated raw quote + optional hints)
- Client: `app/extraction/services/deepseek_client.py`
  - Environment-variable configuration
  - Retry on 429/5xx + timeouts
  - Robust JSON extraction (handles code fences and extra text around JSON)

**C) Validation**
- Schema: `app/extraction/schemas/quotation.py` (Pydantic; `extra="forbid"`)
- Missing fields: `app/extraction/validators/quotation_validator.py`
- Confidence score: `app/extraction/validators/quotation_validator.py`

**D) PostgreSQL persistence**
- If `unit_price` and `currency` are present, inserts a row into `quotations`.
- Stored fields:
  - `unit_price`, `currency`, `moq`, `delivery_days`, `validity_days`, `payment_terms`
  - `notes`, `raw_text`, `missing_fields`, `extraction_confidence`
- Pipeline: `app/extraction/pipeline/quotation_pipeline.py`

## 4) How to Run Tests (copy/paste)

Install deps:

```powershell
venv\Scripts\pip install -r requirements.txt
```

Run migrations:

```powershell
venv\Scripts\python -m alembic upgrade head
```

Seed suppliers (required for simulation-based demos):

```powershell
venv\Scripts\python -m scripts.seed_suppliers
```

Quick DB health check:

```powershell
venv\Scripts\python -m scripts.check_database
```

### A) Extraction demo (simulation-based)

Dry run (prints extractions; no DB inserts):

```powershell
venv\Scripts\python -m scripts.test_extraction --material cement
```

Persist (inserts into `quotations` when extraction has required fields):

```powershell
venv\Scripts\python -m scripts.test_extraction --material cement --persist
```

### B) DeepSeek real validation (fixed 5 test cases)

Runs 5 cases and prints:
- raw input
- extracted JSON fields
- confidence
- missing fields
- (if DB is reachable) verifies insert and prints stored values

```powershell
venv\Scripts\python -m scripts.validate_deepseek_extraction
```

### C) DeepSeek debug mode

Enable debug logging (prints raw response content previews + request errors):

```powershell
$env:DEEPSEEK_DEBUG=1
venv\Scripts\python -m scripts.validate_deepseek_extraction
```

If you see `WinError 10013` (socket access forbidden), your machine/network is blocking outbound HTTPS requests from Python. Allow outbound access for Python (or run on a different network/VPN) to validate real DeepSeek calls.

### D) Token-saving local fallback (regex pre-extraction)

The extraction pipeline runs a lightweight local regex pass (currency/unit price, MOQ, delivery, validity) before calling the LLM, and uses it as a fallback if the LLM fails. This reduces DeepSeek token usage and prevents DB persistence from being blocked when obvious fields are present.

## 5) Example Workflow

1) You receive a supplier message like:
   - “RATE - INR 399.00, MOQ 200, delivery 2 days…”
2) Run extraction:
   - `QuotationExtractor.extract(raw_text=...)`
3) The model returns strict JSON:
   - keys: `supplier_name`, `material_type`, `unit_price`, `currency`, `minimum_order_quantity`, `delivery_days`, `validity_days`, `payment_terms`, `notes`
4) Validation computes:
   - `missing_fields` list
   - `extraction_confidence` float in `[0,1]`
5) Persistence inserts into `quotations` if required fields are present.

## 6) Common Errors & Fixes

**Invalid API key**
- Symptom: HTTP 401/403 from DeepSeek.
- Fix: check `DEEPSEEK_API_KEY` in `.env`.

**Malformed JSON from model**
- Symptom: JSON parse error.
- Fix:
  - Prompts already enforce JSON-only.
  - Client extracts the first JSON object even if the model adds extra text.
  - If it still fails, reduce input size and keep supplier text short.

**Rate limit / quota**
- Symptom: HTTP 429.
- Fix: lower test volume, keep prompts small, avoid repeated retries.

**Supabase connection errors (network / IPv6 / permission denied)**
- Symptom: connection fails to the direct host (often resolves to IPv6).
- Fix: use Supabase **Session Pooler** connection string from the dashboard.

**Alembic fails with `invalid interpolation syntax`**
- Symptom: happens when `%` appears in your password inside `DATABASE_URL`.
- Fix: URL-encode `%` as `%25` in the URL, or keep special chars URL-encoded.

## 7) Token Optimization Notes

Why prompts are short:
- Every extra instruction consumes tokens and cost; extraction quality improves more from clear keys than verbosity.

Why compact JSON output:
- Smaller model output = lower tokens and fewer parsing errors.

How unnecessary usage is avoided:
- Truncation of long raw text before LLM calls.
- Quick local reject for non-quotation text.
- Deterministic settings (`temperature=0`) to reduce variance and retries.
