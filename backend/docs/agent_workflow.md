# Agent Workflow (Responsibilities + IO)

All agents operate on the shared `ProcurementState` (`app/procurement/state.py`) and persist outputs in PostgreSQL.

## 1) Supervisor Agent

File: `app/procurement/agents/supervisor.py`

Responsibilities:

- Validate request input (basic sanity checks)
- Create `procurement_requests` row
- Initialize shared state (`request_id`, `status`, logs)
- Handoff to Discovery

## 2) Discovery Agent

File: `app/procurement/agents/discovery.py`

Responsibilities:

- Fetch suppliers from PostgreSQL
- Filter by `material_type` category (`suppliers.material_categories`)
- Store supplier snapshots in shared state
- Handoff to Extraction

## 3) Extraction Agent

File: `app/procurement/agents/extraction.py`

Responsibilities:

- Generate simulated supplier quotations (token/DB-friendly)
- If `DEEPSEEK_API_KEY` is set:
  - Invoke DeepSeek extraction pipeline
  - Validate + compute confidence/missing fields (existing logic)
- Persist `quotations` rows
- Store extracted quotation snapshots in shared state

Notes:

- If `DEEPSEEK_API_KEY` is missing, the agent persists deterministic structured simulated values so the rest of the pipeline remains runnable.

## 4) Scoring Agent

File: `app/procurement/agents/scoring.py`

Responsibilities:

- Compute deterministic, normalized trust scores (no LLM decisions)
- Configurable weights (`app/procurement/scoring.py`)
- Persist `trust_scores` rows (upsert per request+supplier)
- Handoff to Analyst

Scoring dimensions:

- Price competitiveness
- Response speed
- Quote completeness
- Referral score

## 5) Analyst Agent

File: `app/procurement/agents/analyst.py`

Responsibilities:

- Rank suppliers by `composite_score`
- Generate concise summary + structured top supplier output
- Persist `reports` row
- Mark request `complete`

## Running + Testing

DB health check:

```powershell
venv\Scripts\python -m scripts.check_database
```

Extraction-only demo:

```powershell
venv\Scripts\python -m scripts.test_extraction --material cement
venv\Scripts\python -m scripts.test_extraction --material cement --persist
```

Full pipeline:

```powershell
venv\Scripts\python -m scripts.run_procurement_pipeline --material cement
venv\Scripts\python -m scripts.run_procurement_pipeline --material cement --langgraph
```

