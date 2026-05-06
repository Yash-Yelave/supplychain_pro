from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal

from app.models.supplier import Supplier


@dataclass(frozen=True)
class SimulatedQuote:
    supplier_id: str
    supplier_name: str
    raw_text: str
    unit_price: Decimal
    currency: str
    moq: int | None
    delivery_days: int | None
    validity_days: int | None
    payment_terms: str | None


def generate_supplier_quote(
    *,
    supplier: Supplier,
    material_type: str,
    seed: int | None = None,
) -> SimulatedQuote:
    rng = random.Random(seed)

    currency = "INR"
    unit_price = _jitter_price(rng, base=_base_price_for(material_type), pct=0.12)
    moq = rng.choice([None, 50, 100, 200, 500])
    delivery_days = rng.choice([None, 2, 3, 5, 7, 10, 14])
    validity_days = rng.choice([None, 3, 5, 7, 10, 15])
    payment_terms = rng.choice(
        [
            None,
            "50% advance, balance on delivery",
            "Net 7 days",
            "Net 15 days",
            "100% advance",
            "30% advance, 70% on dispatch",
        ]
    )

    raw_text = _render_noisy_template(
        rng=rng,
        template=supplier.simulated_reply_template,
        supplier=supplier.name,
        material_type=material_type,
        unit_price=unit_price,
        currency=currency,
        moq=moq,
        delivery_days=delivery_days,
        validity_days=validity_days,
        payment_terms=payment_terms,
    )

    return SimulatedQuote(
        supplier_id=str(supplier.id),
        supplier_name=supplier.name,
        raw_text=raw_text,
        unit_price=unit_price,
        currency=currency,
        moq=moq,
        delivery_days=delivery_days,
        validity_days=validity_days,
        payment_terms=payment_terms,
    )


def _base_price_for(material_type: str) -> Decimal:
    t = material_type.strip().lower()
    if "cement" in t:
        return Decimal("395.00")
    if "steel" in t or "tmt" in t:
        return Decimal("61250.00")
    if "sand" in t:
        return Decimal("1450.00")
    if "aggregate" in t:
        return Decimal("1250.00")
    if "brick" in t:
        return Decimal("8.50")
    return Decimal("999.00")


def _jitter_price(rng: random.Random, *, base: Decimal, pct: float) -> Decimal:
    factor = Decimal(str(1 + rng.uniform(-pct, pct)))
    v = (base * factor).quantize(Decimal("0.01"))
    return v if v > 0 else base


def _render_noisy_template(
    *,
    rng: random.Random,
    template: str,
    supplier: str,
    material_type: str,
    unit_price: Decimal,
    currency: str,
    moq: int | None,
    delivery_days: int | None,
    validity_days: int | None,
    payment_terms: str | None,
) -> str:
    # Supplier templates are stored in DB; keep output short but noisy.
    base = template.format(
        supplier=supplier,
        material_type=material_type,
        unit_price=str(unit_price),
        currency=currency,
        moq=("N/A" if moq is None else str(moq)),
        delivery_days=("TBD" if delivery_days is None else str(delivery_days)),
        validity_days=("TBD" if validity_days is None else str(validity_days)),
        payment_terms=(payment_terms or "TBD"),
    )

    # Ensure core fields appear even if the supplier template is generic.
    parts: list[str] = [base.strip()]
    rate_line = f"Rate: {currency} {unit_price}"
    if rng.random() < 0.35:
        rate_line = f"RATE - {currency} {unit_price}"
    parts.append(rate_line)
    if moq is not None:
        parts.append(f"MOQ: {moq}")
    if delivery_days is not None:
        parts.append(f"Delivery: {delivery_days} days")
    if validity_days is not None:
        parts.append(f"Validity: {validity_days} days")
    if payment_terms:
        parts.append(f"Payment: {payment_terms}")

    base = "\n".join(parts)

    extras = rng.choice(
        [
            "",
            "\n\npls confirm qty + delivery address.",
            "\n\nRates may vary if site is outside city limits.",
            "\n\nNote: GST extra as applicable.",
            "\n\nRegards,\nProcurement Desk",
        ]
    )

    if rng.random() < 0.35:
        base = base.replace(":", " : ").replace("  ", " ")
    if rng.random() < 0.25:
        base = base.replace("\n", "\n ")
    if rng.random() < 0.20:
        base = base.replace(currency, currency.lower())

    return (base.strip() + extras).strip()
