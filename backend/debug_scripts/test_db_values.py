from app.db.session import SessionLocal
from app.models.procurement_request import ProcurementRequest
from sqlalchemy import select

db = SessionLocal()
requests = db.scalars(select(ProcurementRequest).limit(10)).all()
for r in requests:
    print(f"ID: {r.id}, country: {r.target_country_code}, quality: {r.quality_grade}")
db.close()
