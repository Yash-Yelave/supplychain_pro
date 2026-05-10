# Database Schema (Authoritative)

This document is generated from SQLAlchemy models (`app/models/*`). Update models + Alembic migrations first, then regenerate:

```powershell
python -m scripts.gen_db_docs
```

## Entities

- `procurement_requests`
- `suppliers`
- `quotations`
- `reports`
- `trust_scores`

## `procurement_requests`

| Column | Type | Nullable | Default |
|---|---|---:|---|
| `id` | `UUID` | `False` | `uuid4` |
| `material_type` | `VARCHAR(100)` | `False` | `` |
| `quantity` | `FLOAT` | `False` | `` |
| `unit` | `VARCHAR(50)` | `False` | `` |
| `deadline` | `DATE` | `False` | `` |
| `status` | `VARCHAR(11)` | `False` | `pending` |
| `current_agent` | `VARCHAR(100)` | `True` | `` |
| `created_at` | `DATETIME` | `False` | `now()` |
| `completed_at` | `DATETIME` | `True` | `` |

- **Primary key:** `id`
- **Index:** `ix_procurement_requests_material_type` on `material_type`

## `suppliers`

| Column | Type | Nullable | Default |
|---|---|---:|---|
| `id` | `UUID` | `False` | `uuid4` |
| `name` | `VARCHAR(255)` | `False` | `` |
| `email` | `VARCHAR(255)` | `False` | `` |
| `location` | `VARCHAR(255)` | `False` | `` |
| `material_categories` | `JSONB` | `False` | `` |
| `simulated_response_hours` | `INTEGER` | `False` | `` |
| `referral_count` | `INTEGER` | `False` | `0` |
| `simulated_reply_template` | `TEXT` | `False` | `` |
| `created_at` | `DATETIME` | `False` | `now()` |

- **Primary key:** `id`
- **Index unique:** `ix_suppliers_email` on `email`

## `quotations`

| Column | Type | Nullable | Default |
|---|---|---:|---|
| `id` | `UUID` | `False` | `uuid4` |
| `request_id` | `UUID` | `False` | `` |
| `supplier_id` | `UUID` | `False` | `` |
| `unit_price` | `NUMERIC(12, 2)` | `False` | `` |
| `currency` | `VARCHAR(3)` | `False` | `INR` |
| `moq` | `INTEGER` | `True` | `` |
| `delivery_days` | `INTEGER` | `True` | `` |
| `validity_days` | `INTEGER` | `True` | `` |
| `payment_terms` | `VARCHAR(255)` | `True` | `` |
| `notes` | `TEXT` | `True` | `` |
| `extraction_confidence` | `NUMERIC(5, 4)` | `True` | `` |
| `missing_fields` | `JSONB` | `False` | `'[]'::jsonb` |
| `raw_text` | `TEXT` | `True` | `` |
| `created_at` | `DATETIME` | `False` | `now()` |

- **Primary key:** `id`
- **Foreign key:** `supplier_id` → `suppliers.id`
- **Foreign key:** `request_id` → `procurement_requests.id`
- **Index:** `ix_quotations_request_id` on `request_id`
- **Index:** `ix_quotations_supplier_id` on `supplier_id`

## `reports`

| Column | Type | Nullable | Default |
|---|---|---:|---|
| `id` | `UUID` | `False` | `uuid4` |
| `request_id` | `UUID` | `False` | `` |
| `summary_text` | `TEXT` | `False` | `` |
| `top_suppliers` | `JSONB` | `False` | `` |
| `created_at` | `DATETIME` | `False` | `now()` |

- **Primary key:** `id`
- **Foreign key:** `request_id` → `procurement_requests.id`
- **Index unique:** `ix_reports_request_id` on `request_id`

## `trust_scores`

| Column | Type | Nullable | Default |
|---|---|---:|---|
| `id` | `UUID` | `False` | `uuid4` |
| `request_id` | `UUID` | `False` | `` |
| `supplier_id` | `UUID` | `False` | `` |
| `price_competitiveness` | `NUMERIC(5, 4)` | `False` | `` |
| `response_speed_score` | `NUMERIC(5, 4)` | `False` | `` |
| `quote_completeness` | `NUMERIC(5, 4)` | `False` | `` |
| `referral_score` | `NUMERIC(5, 4)` | `False` | `` |
| `composite_score` | `NUMERIC(5, 4)` | `False` | `` |
| `weights_used` | `JSONB` | `False` | `` |
| `computed_at` | `DATETIME` | `False` | `now()` |

- **Primary key:** `id`
- **Unique (`uq_trust_scores_request_supplier`):** `request_id`, `supplier_id`
- **Foreign key:** `request_id` → `procurement_requests.id`
- **Foreign key:** `supplier_id` → `suppliers.id`
- **Index:** `ix_trust_scores_composite_score` on `composite_score`
- **Index:** `ix_trust_scores_request_id` on `request_id`
- **Index:** `ix_trust_scores_supplier_id` on `supplier_id`
