from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()
# Fix trailing spaces in status
conn.execute(text("UPDATE procurement_requests SET status = TRIM(status)"))
# Set defaults for new columns if they are null
conn.execute(text("UPDATE procurement_requests SET target_country_code = 'GL' WHERE target_country_code IS NULL"))
conn.execute(text("UPDATE procurement_requests SET quality_grade = 'Standard' WHERE quality_grade IS NULL"))
# Same for suppliers just in case
conn.execute(text("UPDATE suppliers SET country_code = 'GL' WHERE country_code IS NULL"))
conn.execute(text("UPDATE suppliers SET city = 'Unknown' WHERE city IS NULL"))
conn.execute(text("UPDATE suppliers SET region = 'Unknown' WHERE region IS NULL"))
conn.commit()
conn.close()
