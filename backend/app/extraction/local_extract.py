from __future__ import annotations

import re
from decimal import Decimal

from app.extraction.schemas.quotation import QuotationExtraction


_CURRENCY_RE = re.compile(r"\b(INR|RS|USD|EUR|GBP|AED|SAR|SGD|AUD|CAD)\b", re.I)
_CURRENCY_PREFIX_RE = re.compile(r"(INR|RS|USD|EUR|GBP|AED|SAR|SGD|AUD|CAD)\s*([0-9])", re.I)
_PRICE_RE = re.compile(
    r"(?:(?:INR|RS|USD|EUR|GBP|AED|SAR|SGD|AUD|CAD)\s*)?([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
    re.I,
)
_MOQ_RE = re.compile(r"\b(?:MOQ|MIN(?:IMUM)?\s*ORDER)\s*[:\-]?\s*([0-9][0-9,]*)", re.I)
_DELIVERY_RE = re.compile(r"\bDELIVERY\s*[:\-]?\s*([0-9]{1,3})\s*(?:D|DAY|DAYS)\b", re.I)
_VALIDITY_RE = re.compile(r"\bVALID(?:ITY)?\s*[:\-]?\s*([0-9]{1,3})\s*(?:D|DAY|DAYS)\b", re.I)
_PAYMENT_RE = re.compile(r"\bPAY(?:MENT)?\b\s*[:\-]?\s*(.{0,80})", re.I)


def local_extract(raw_text: str, *, supplier_hint: str | None, material_hint: str | None) -> QuotationExtraction:
    """
    Token-free extraction for common patterns.

    Intended to run before LLM to reduce calls, and as a fallback if the LLM fails.
    """

    text = raw_text or ""
    t = text.replace("\n", " ").strip()
    t_upper = t.upper()

    currency = None
    m = _CURRENCY_RE.search(t_upper)
    if m:
        currency = m.group(1).upper()
        if currency == "RS":
            currency = "INR"
    else:
        m2 = _CURRENCY_PREFIX_RE.search(t_upper)
        if m2:
            currency = m2.group(1).upper()
            if currency == "RS":
                currency = "INR"

    unit_price = None
    # Prefer price values that appear near a currency token.
    if currency:
        m2 = re.search(rf"{re.escape(currency)}\s*([0-9][0-9,]*(?:\.[0-9]{{1,2}})?)", t_upper, re.I)
        if not m2 and currency == "INR":
            m2 = re.search(r"(?:INR|RS)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", t_upper, re.I)
        if m2:
            unit_price = Decimal(m2.group(1).replace(",", ""))
    if unit_price is None:
        # Fallback: look for "rate" patterns (handles "inr402.50" too).
        m3 = re.search(
            r"\bRATE\s*[:\-]?\s*(?:INR|RS|USD|EUR|GBP|AED|SAR|SGD|AUD|CAD)?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
            t_upper,
            re.I,
        )
        if m3:
            unit_price = Decimal(m3.group(1).replace(",", ""))
        else:
            m4 = re.search(r"\b(?:INR|RS|USD|EUR|GBP|AED|SAR|SGD|AUD|CAD)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", t_upper, re.I)
            if m4:
                unit_price = Decimal(m4.group(1).replace(",", ""))

    moq = None
    m = _MOQ_RE.search(t_upper)
    if m:
        moq = int(m.group(1).replace(",", ""))

    delivery_days = None
    m = _DELIVERY_RE.search(t_upper)
    if m:
        delivery_days = int(m.group(1))

    validity_days = None
    m = _VALIDITY_RE.search(t_upper)
    if m:
        validity_days = int(m.group(1))

    payment_terms = None
    m = _PAYMENT_RE.search(t)
    if m:
        candidate = m.group(1).strip().strip(".").strip()
        # Stop at obvious separators to avoid grabbing signatures/notes.
        candidate = re.split(r"(?i)\b(?:NOTE|GST|REGARDS|THANKS|THX)\b|--", candidate, maxsplit=1)[0].strip()
        if candidate and not candidate.lower().startswith(("subject", "note")):
            payment_terms = candidate

    return QuotationExtraction(
        supplier_name=supplier_hint,
        material_type=material_hint,
        unit_price=unit_price,
        currency=currency,
        minimum_order_quantity=moq,
        delivery_days=delivery_days,
        validity_days=validity_days,
        payment_terms=payment_terms,
        notes=None,
    )
