# ConstructProcure AI

Backend foundation for a multi-agent construction procurement system. Day 1 scope is intentionally limited to environment configuration, PostgreSQL persistence, SQLAlchemy models, Alembic migrations, supplier seed data, and basic supplier queries.

## Requirements

- Python 3.11
- PostgreSQL database, including Supabase PostgreSQL

## Run Backend

```
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Frontend

```
cd frontend
npm install
npm run dev
```

## Setup

```powershell
py -3.11 -m venv .venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env`. SQLAlchemy must use the `postgresql+psycopg://` prefix:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR-PASSWORD@db.yjntccgwhskykbbsigrr.supabase.co:5432/postgres
```

Replace `YOUR-PASSWORD` with the Supabase database password. If your network cannot reach the direct database host over IPv4, use Supabase Session Pooler details instead and keep the same `postgresql+psycopg://` prefix.

## Database

Run migrations (creates/updates database tables via Alembic):

```powershell
alembic upgrade head
```

Database docs:

- Narrative: `docs/database.md`
- Generated schema snapshot: `docs/database_schema.md` (regenerate from SQLAlchemy models with `python -m scripts.gen_db_docs`)

Regenerate schema snapshot (writes `docs/database_schema.md`):

```powershell
python -m scripts.gen_db_docs
```

Seed suppliers (inserts demo supplier rows used by simulations/tests):

```powershell
python -m scripts.seed_suppliers
```

Validate connection, tables, seed data, and category query (quick DB health check):

```powershell
python -m scripts.check_database
```

## Extraction (Day 2+)

Environment:

```env
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

Run the lightweight extraction demo (uses seeded suppliers; creates a temporary procurement request):

```powershell
python -m scripts.test_extraction --material cement
python -m scripts.test_extraction --material cement --persist
```

## Query Examples

```python
from app.crud.suppliers import (
    get_supplier_by_id,
    get_suppliers_by_category,
    list_all_suppliers,
)

cement_suppliers = get_suppliers_by_category("cement")
all_suppliers = list_all_suppliers()
supplier = get_supplier_by_id("00000000-0000-0000-0000-000000000000")
```

## Project Structure

```text
app/
  core/
    config.py
  crud/
    suppliers.py
  db/
    base.py
    session.py
  models/
    procurement_request.py
    quotation.py
    report.py
    supplier.py
    trust_score.py
alembic/
  versions/
    20260505_0001_create_foundation_tables.py
scripts/
  seed_suppliers.py
  check_database.py
  verify_database.py
```
