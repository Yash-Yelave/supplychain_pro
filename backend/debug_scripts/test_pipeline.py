from app.db.session import SessionLocal
from app.services.procurement_service import create_request, run_pipeline_for_request
from app.schemas.procurement import ProcurementRequestCreate
from datetime import date
import sys

db = SessionLocal()
payload = ProcurementRequestCreate(
    material_type="steel",
    quantity=100.0,
    unit="Tons",
    shipping_deadline=date(2026, 6, 1),
    target_country_code="AE",
    quality_grade="Premium"
)
req = create_request(db=db, payload=payload)
req_id = req.id
db.commit()
db.close() # Close session so pipeline can get one

print(f"Created request: {req_id}")
# We'll run it synchronously, so exceptions will bubble up naturally, except `run_pipeline_for_request` catches them and sets status to failed!
# But since I added traceback.print_exc() in my previous step, it will print it!
run_pipeline_for_request(request_id=req_id, payload=payload)
