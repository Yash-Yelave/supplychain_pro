# ConstructProcure AI

Backend foundation for a multi-agent construction procurement system. Day 1 scope is intentionally limited to environment configuration, PostgreSQL persistence, SQLAlchemy models, Alembic migrations, supplier seed data, and basic supplier queries.

## Requirements

- Python 3.11
- PostgreSQL database, including Supabase PostgreSQL

## Setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env`. SQLAlchemy must use the `postgresql+psycopg://` prefix:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR-PASSWORD@db.yjntccgwhskykbbsigrr.supabase.co:5432/postgres
```

Replace `YOUR-PASSWORD` with the Supabase database password. If your network cannot reach the direct database host over IPv4, use Supabase Session Pooler details instead and keep the same `postgresql+psycopg://` prefix.

## Database

Run migrations:

```powershell
alembic upgrade head
```

Seed suppliers:

```powershell
python -m scripts.seed_suppliers
```

Validate connection, tables, seed data, and category query:

```powershell
python -m scripts.check_database
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

