from __future__ import annotations

import math
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TrustScoreWeights:
    price_competitiveness: float = 0.50
    response_speed_score: float = 0.0
    quote_completeness: float = 0.50
    referral_score: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "price_competitiveness": float(self.price_competitiveness),
            "response_speed_score": float(self.response_speed_score),
            "quote_completeness": float(self.quote_completeness),
            "referral_score": float(self.referral_score),
        }

    def normalized(self) -> "TrustScoreWeights":
        total = (
            float(self.price_competitiveness)
            + float(self.response_speed_score)
            + float(self.quote_completeness)
            + float(self.referral_score)
        )
        if total <= 0:
            return TrustScoreWeights()
        return TrustScoreWeights(
            price_competitiveness=float(self.price_competitiveness) / total,
            response_speed_score=float(self.response_speed_score) / total,
            quote_completeness=float(self.quote_completeness) / total,
            referral_score=float(self.referral_score) / total,
        )


def _min_max(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    return min(values), max(values)


def _normalize_low_is_better(v: float, *, v_min: float, v_max: float) -> float:
    if v_max <= v_min:
        return 1.0
    return max(0.0, min(1.0, (v_max - v) / (v_max - v_min)))


def price_percentile_score(v: float, values: list[float]) -> float:
    if not values or len(values) <= 1 or max(values) == min(values):
        return 1.0
    worse_count = sum(1 for x in values if x > v)
    max_worse = sum(1 for x in values if x > min(values))
    if max_worse == 0:
        return 1.0
    return worse_count / max_worse


def _normalize_high_is_better(v: float, *, v_min: float, v_max: float) -> float:
    if v_max <= v_min:
        return 1.0
    return max(0.0, min(1.0, (v - v_min) / (v_max - v_min)))


def referral_score_log(referrals: int, *, max_referrals: int) -> float:
    if max_referrals <= 0:
        return 0.0
    return max(0.0, min(1.0, math.log1p(max(0, referrals)) / math.log1p(max_referrals)))


def completeness_score(*, missing_fields: list[str], core_field_count: int, extraction_confidence: float) -> float:
    if core_field_count <= 0:
        return 0.0
    missing_ratio = min(1.0, max(0.0, len(missing_fields) / core_field_count))
    base = 1.0 - missing_ratio
    confidence = max(0.0, min(1.0, float(extraction_confidence)))
    return max(0.0, min(1.0, base * (0.5 + 0.5 * confidence)))


def compute_trust_scores(
    *,
    supplier_ids: list[uuid.UUID],
    supplier_response_hours: dict[uuid.UUID, int],
    supplier_referrals: dict[uuid.UUID, int],
    supplier_unit_prices: dict[uuid.UUID, float],
    supplier_missing_fields: dict[uuid.UUID, list[str]],
    supplier_extraction_confidence: dict[uuid.UUID, float],
    weights: TrustScoreWeights | None = None,
    core_field_count: int = 8,
) -> dict[uuid.UUID, dict[str, float]]:
    """
    Deterministic trust scoring.

    Returns per-supplier scores:
      - price_competitiveness
      - response_speed_score
      - quote_completeness
      - referral_score
      - composite_score
    """

    w = (weights or TrustScoreWeights()).normalized()
    weights_dict = w.as_dict()

    prices = [float(supplier_unit_prices[sid]) for sid in supplier_ids if sid in supplier_unit_prices]
    resp = [float(supplier_response_hours.get(sid, 0)) for sid in supplier_ids]
    refs = [int(supplier_referrals.get(sid, 0)) for sid in supplier_ids]

    price_min, price_max = _min_max(prices)
    resp_min, resp_max = _min_max(resp)
    max_referrals = max(refs) if refs else 0

    out: dict[uuid.UUID, dict[str, Any]] = {}
    for sid in supplier_ids:
        price = float(supplier_unit_prices.get(sid, price_max if prices else 0.0))
        response_h = float(supplier_response_hours.get(sid, resp_max if resp else 0.0))
        referrals = int(supplier_referrals.get(sid, 0))
        missing_fields = supplier_missing_fields.get(sid, [])
        extraction_conf = float(supplier_extraction_confidence.get(sid, 0.0))

        price_score = price_percentile_score(price, prices) if prices else 0.0
        response_score = _normalize_low_is_better(response_h, v_min=resp_min, v_max=resp_max) if resp else 0.0
        complete_score = completeness_score(
            missing_fields=missing_fields,
            core_field_count=core_field_count,
            extraction_confidence=extraction_conf,
        )
        ref_score = referral_score_log(referrals, max_referrals=max_referrals)

        composite = (
            weights_dict["price_competitiveness"] * price_score
            + weights_dict["response_speed_score"] * response_score
            + weights_dict["quote_completeness"] * complete_score
            + weights_dict["referral_score"] * ref_score
        )

        worse_count = sum(1 for x in prices if x > price) if prices else 0
        total_unique = sum(1 for x in prices if x > min(prices)) if prices else 0

        score_analysis = {
            "price_logic": f"Price AED {price:.2f}. " + (f"Cheaper than {worse_count} out of {total_unique} competing price tiers." if total_unique > 0 else "Sole or best price tier."),
            "speed_logic": f"Response in {response_h} hours (Best: {resp_min}h, Worst: {resp_max}h).",
            "quality_logic": f"Extracted {core_field_count - len(missing_fields)}/{core_field_count} core fields with {extraction_conf*100:.0f}% LLM confidence.",
            "trust_logic": f"Supplier has {referrals} referrals (Market Max: {max_referrals}).",
            "final_logic": f"Composite score calculated using weights: Price ({weights_dict['price_competitiveness']*100:.0f}%), Speed ({weights_dict['response_speed_score']*100:.0f}%), Quality ({weights_dict['quote_completeness']*100:.0f}%), Trust ({weights_dict['referral_score']*100:.0f}%)."
        }

        out[sid] = {
            "price_competitiveness": float(price_score),
            "response_speed_score": float(response_score),
            "quote_completeness": float(complete_score),
            "referral_score": float(ref_score),
            "composite_score": float(max(0.0, min(1.0, composite))),
            "weights_used": weights_dict,
            "score_analysis": score_analysis,
        }
    return out

