from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()
conn.execute(text("DROP TYPE IF EXISTS procurement_request_status CASCADE"))
conn.commit()
conn.close()
