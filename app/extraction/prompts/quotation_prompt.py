from __future__ import annotations

from app.extraction.validators.text import normalize_quotation_text, truncate_text


QUOTATION_SYSTEM_PROMPT = (
    "Extract procurement fields from the supplier quotation. "
    "Return ONLY a JSON object with exactly these keys: "
    "supplier_name, material_type, unit_price, currency, minimum_order_quantity, "
    "delivery_days, validity_days, payment_terms, notes. "
    "Use null when unknown. No extra keys. No markdown."
)


def build_quotation_user_prompt(
    *,
    raw_text: str,
    supplier_hint: str | None = None,
    material_hint: str | None = None,
    max_chars: int = 1400,
) -> str:
    clean = truncate_text(normalize_quotation_text(raw_text), max_chars=max_chars)
    hint_lines: list[str] = []
    if supplier_hint:
        hint_lines.append(f"Supplier hint: {supplier_hint.strip()}")
    if material_hint:
        hint_lines.append(f"Material hint: {material_hint.strip()}")
    hints = "\n".join(hint_lines)
    if hints:
        return f"{hints}\n\nQuotation:\n{clean}"
    return f"Quotation:\n{clean}"

