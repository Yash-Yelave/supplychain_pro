from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()
rows = conn.execute(text("SELECT id, name, material_categories FROM suppliers")).fetchall()
for r in rows:
    print(r[0], r[1], r[2])
conn.close()
