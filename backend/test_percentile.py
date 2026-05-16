import uuid
from app.procurement.scoring import compute_trust_scores, TrustScoreWeights

supplier_1 = uuid.uuid4()
supplier_2 = uuid.uuid4()
supplier_3 = uuid.uuid4()
supplier_4 = uuid.uuid4()
supplier_5 = uuid.uuid4()

supplier_ids = [supplier_1, supplier_2, supplier_3, supplier_4, supplier_5]
prices = {
    supplier_1: 100.0,
    supplier_2: 120.0,
    supplier_3: 150.0,
    supplier_4: 150.0,
    supplier_5: 200.0
}

res = compute_trust_scores(
    supplier_ids=supplier_ids,
    supplier_response_hours={s: 1 for s in supplier_ids},
    supplier_referrals={s: 1 for s in supplier_ids},
    supplier_unit_prices=prices,
    supplier_missing_fields={s: [] for s in supplier_ids},
    supplier_extraction_confidence={s: 1.0 for s in supplier_ids},
    weights=TrustScoreWeights(price_competitiveness=1.0, response_speed_score=0.0, quote_completeness=0.0, referral_score=0.0)
)

print(f"100.0: {res[supplier_1]['price_competitiveness']}")
print(f"120.0: {res[supplier_2]['price_competitiveness']}")
print(f"150.0: {res[supplier_3]['price_competitiveness']}")
print(f"150.0: {res[supplier_4]['price_competitiveness']}")
print(f"200.0: {res[supplier_5]['price_competitiveness']}")
