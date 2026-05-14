from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()
print(conn.execute(text("SELECT data_type, udt_name FROM information_schema.columns WHERE table_name = 'procurement_requests' AND column_name = 'status'")).fetchall())
conn.close()
