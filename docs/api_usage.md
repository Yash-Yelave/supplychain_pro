# ConstructProcure AI API Usage

## 1. Setup (venv)

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env`. Optional flags:

```env
PIPELINE_USE_LANGGRAPH=false
DB_POOL_SIZE=1
DB_MAX_OVERFLOW=0
DB_DISABLE_POOLING=false
```

## 2. Database Prep

```powershell
alembic upgrade head
python -m scripts.seed_suppliers
```

## 3. Start FastAPI Server

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

## 4. Endpoint Summary

### Create request

`POST /procurement/request`

Example:

```powershell
curl -X POST "http://127.0.0.1:8000/procurement/request" `
  -H "Content-Type: application/json" `
  -d "{\"material_type\":\"cement\",\"quantity\":100,\"unit\":\"bag\",\"deadline\":\"2026-05-20\"}"
```

Response:

```json
{
  "request_id": "UUID",
  "pipeline_status": "in_progress",
  "current_agent": "supervisor"
}
```

### Get status

`GET /procurement/{request_id}/status`

```powershell
curl "http://127.0.0.1:8000/procurement/<REQUEST_ID>/status"
```

### Get results

`GET /procurement/{request_id}/results`

```powershell
curl "http://127.0.0.1:8000/procurement/<REQUEST_ID>/results"
```

## 5. Local API Flow Test

Start server first, then:

```powershell
python -m scripts.test_api_flow --base-url http://127.0.0.1:8000 --material cement
```

This validates:

- request creation
- pipeline progression
- status polling
- result retrieval

## 6. Common Errors

- `422 deadline must not be in the past`: send a future or current date.
- `404 procurement request not found`: invalid request UUID.
- `failed` status with no results: inspect server logs and `procurement_requests.current_agent`.
- DeepSeek unavailable: pipeline uses fallback extraction persistence.
