from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
rows = db.execute(text("SELECT id, status::text FROM procurement_requests")).fetchall()
for r in rows:
    print(f"Row {r[0]}: {repr(r[1])}")

db.close()
