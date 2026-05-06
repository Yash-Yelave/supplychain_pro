# Database (PostgreSQL / Supabase)

Supabase is used only as a hosted PostgreSQL provider. The application uses SQLAlchemy + Alembic and should remain portable to any PostgreSQL deployment.

## Source of truth

- **SQLAlchemy models:** `app/models/*`
- **Migrations:** `alembic/versions/*`
- **Generated schema doc:** `docs/database_schema.md` (generated from models)

Keep these in sync:

1) Change SQLAlchemy models
2) Create an Alembic migration
3) Apply migrations (`alembic upgrade head`)
4) Regenerate docs (`python -m scripts.gen_db_docs`)

## Connection hygiene (Supabase free tier)

- Prefer session pooling (see Supabase “Session Pooler”) if direct connections are flaky.
- Keep pool small to avoid exhausting connection limits:
  - `DB_POOL_SIZE=1`
  - `DB_MAX_OVERFLOW=0`
- Avoid long-lived transactions; commit quickly.

## Migrations

Run:

```powershell
python -m alembic upgrade head
```

If your DB already has tables but Alembic is not initialized, do **not** drop tables in Supabase. Instead:

- Ensure `DATABASE_URL` points to the correct database
- Bring Alembic in sync (either stamp or make base migration idempotent)
- Then continue with migrations normally

## Suppliers seed data (demo)

Seed:

```powershell
python -m scripts.seed_suppliers
```

Verify:

```powershell
python -m scripts.check_database
```

