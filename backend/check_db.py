from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()
print("procurement_requests columns:", [r[0] for r in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'procurement_requests'")).fetchall()])
print("suppliers columns:", [r[0] for r in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'suppliers'")).fetchall()])
conn.close()
