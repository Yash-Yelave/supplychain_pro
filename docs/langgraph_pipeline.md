# LangGraph Procurement Pipeline (MVP)

This project includes a lightweight sequential procurement workflow with an optional LangGraph orchestration layer.

Pipeline order:

1. Supervisor
2. Discovery
3. Extraction
4. Scoring
5. Analyst
6. Final report

## Shared State

The shared state model is `app/procurement/state.py` (`ProcurementState`). It is intentionally JSON-serializable so you can dump it for debugging, and it stores:

- Procurement request input + DB `request_id`
- Current `status` and `active_agent`
- Discovered suppliers
- Simulated + extracted quotations
- Deterministic trust scores (with weights used)
- Final recommendations + report
- Transition logs (`logs[]`)

## Setup (venv)

```powershell
venv\Scripts\python -m pip install -r requirements.txt
alembic upgrade head
venv\Scripts\python -m scripts.seed_suppliers
```

Validate DB connectivity + expected tables:

```powershell
venv\Scripts\python -m scripts.check_database
```

## Run Pipeline

Sequential runner (no LangGraph dependency):

```powershell
venv\Scripts\python -m scripts.run_procurement_pipeline --material cement
```

LangGraph runner (requires `langgraph` installed via `requirements.txt`):

```powershell
venv\Scripts\python -m scripts.run_procurement_pipeline --material cement --langgraph
```

## Expected Persistence

Each successful run should persist:

- `procurement_requests` row (status transitions to `complete`)
- `quotations` rows (one per supplier considered)
- `trust_scores` rows (one per supplier considered)
- `reports` row (one per request)

## Debugging Tips

- If `scripts.check_database` fails with networking errors:
  - Supabase direct DB host can be blocked on some networks (especially IPv6-only routes).
  - Use Supabase Session Pooler connection details for `DATABASE_URL` (keep the `postgresql+psycopg://` prefix).
  - The helper `venv\Scripts\python -m scripts.verify_database` prints more connection diagnostics.

- If `scripts.validate_deepseek_extraction` shows DeepSeek request failures:
  - Enable `DEEPSEEK_DEBUG=1` to see the exact exception and raw response previews (when available).
  - `WinError 10013` indicates outbound HTTPS from Python is blocked on the machine/network.

- The pipeline prints:
  - State transitions from `state.logs`
  - DB counts for `quotations`, `trust_scores`, and `reports`
