# ConstructProcure AI Database Schema

This document describes the current PostgreSQL schema implemented in the backend foundation.

## Overview

- Database: PostgreSQL (Supabase-compatible)
- ORM: SQLAlchemy 2.x
- Migration tool: Alembic
- UUID primary keys are used across all core tables
- JSONB is used for flexible structured fields

## Entity Relationship Summary

- One `procurement_requests` row can have many `quotations`
- One `suppliers` row can have many `quotations`
- One `procurement_requests` row can have many `trust_scores`
- One `suppliers` row can have many `trust_scores`
- One `procurement_requests` row has one `reports` row

## Enum Types

### `procurement_request_status`

- `pending`
- `in_progress`
- `complete`
- `failed`

## Tables

### `suppliers`

Purpose: Master supplier records for sourcing and simulation.

| Column | Type | Null | Default | Constraints / Notes |
|---|---|---|---|---|
| `id` | `uuid` | No | `uuid4()` (application-side) | Primary key |
| `name` | `varchar(255)` | No |  |  |
| `email` | `varchar(255)` | No |  | Unique, indexed |
| `location` | `varchar(255)` | No |  |  |
| `material_categories` | `jsonb` | No |  | Stores list of categories (example: `["cement", "concrete"]`) |
| `simulated_response_hours` | `integer` | No |  |  |
| `referral_count` | `integer` | No | `0` |  |
| `simulated_reply_template` | `text` | No |  |  |
| `created_at` | `timestamptz` | No | `now()` |  |

Indexes:
- `ix_suppliers_email` (unique)

Referenced by:
- `quotations.supplier_id`
- `trust_scores.supplier_id`

### `procurement_requests`

Purpose: Procurement lifecycle requests initiated by the system/user.

| Column | Type | Null | Default | Constraints / Notes |
|---|---|---|---|---|
| `id` | `uuid` | No | `uuid4()` (application-side) | Primary key |
| `material_type` | `varchar(100)` | No |  | Indexed |
| `quantity` | `float` | No |  |  |
| `unit` | `varchar(50)` | No |  |  |
| `deadline` | `date` | No |  |  |
| `status` | `procurement_request_status` | No | `pending` | Enum |
| `current_agent` | `varchar(100)` | Yes |  |  |
| `created_at` | `timestamptz` | No | `now()` |  |
| `completed_at` | `timestamptz` | Yes |  |  |

Indexes:
- `ix_procurement_requests_material_type`

Referenced by:
- `quotations.request_id`
- `trust_scores.request_id`
- `reports.request_id` (one-to-one)

### `quotations`

Purpose: Extracted/recorded quotations submitted by suppliers for requests.

| Column | Type | Null | Default | Constraints / Notes |
|---|---|---|---|---|
| `id` | `uuid` | No | `uuid4()` (application-side) | Primary key |
| `request_id` | `uuid` | No |  | FK -> `procurement_requests.id` (`ON DELETE CASCADE`), indexed |
| `supplier_id` | `uuid` | No |  | FK -> `suppliers.id` (`ON DELETE CASCADE`), indexed |
| `unit_price` | `numeric(12,2)` | No |  |  |
| `currency` | `varchar(3)` | No | `INR` | ISO-like currency code |
| `moq` | `integer` | Yes |  | Minimum order quantity |
| `delivery_days` | `integer` | Yes |  |  |
| `validity_days` | `integer` | Yes |  |  |
| `payment_terms` | `varchar(255)` | Yes |  |  |
| `extraction_confidence` | `numeric(5,4)` | Yes |  |  |
| `missing_fields` | `jsonb` | No | `'[]'::jsonb` | Stores missing extraction field names |
| `raw_text` | `text` | Yes |  | Original extracted text blob |
| `created_at` | `timestamptz` | No | `now()` |  |

Indexes:
- `ix_quotations_request_id`
- `ix_quotations_supplier_id`

### `trust_scores`

Purpose: Computed trust and ranking metrics per `(request, supplier)` pair.

| Column | Type | Null | Default | Constraints / Notes |
|---|---|---|---|---|
| `id` | `uuid` | No | `uuid4()` (application-side) | Primary key |
| `request_id` | `uuid` | No |  | FK -> `procurement_requests.id` (`ON DELETE CASCADE`), indexed |
| `supplier_id` | `uuid` | No |  | FK -> `suppliers.id` (`ON DELETE CASCADE`), indexed |
| `price_competitiveness` | `numeric(5,4)` | No |  |  |
| `response_speed_score` | `numeric(5,4)` | No |  |  |
| `quote_completeness` | `numeric(5,4)` | No |  |  |
| `referral_score` | `numeric(5,4)` | No |  |  |
| `composite_score` | `numeric(5,4)` | No |  | Indexed |
| `weights_used` | `jsonb` | No |  | Weight map used in scoring computation |
| `computed_at` | `timestamptz` | No | `now()` |  |

Constraints:
- Unique composite key: `uq_trust_scores_request_supplier` on (`request_id`, `supplier_id`)

Indexes:
- `ix_trust_scores_request_id`
- `ix_trust_scores_supplier_id`
- `ix_trust_scores_composite_score`

### `reports`

Purpose: Final synthesized report for one procurement request.

| Column | Type | Null | Default | Constraints / Notes |
|---|---|---|---|---|
| `id` | `uuid` | No | `uuid4()` (application-side) | Primary key |
| `request_id` | `uuid` | No |  | FK -> `procurement_requests.id` (`ON DELETE CASCADE`), unique, indexed |
| `summary_text` | `text` | No |  |  |
| `top_suppliers` | `jsonb` | No |  | Stores ranked supplier payload |
| `created_at` | `timestamptz` | No | `now()` |  |

Indexes:
- `ix_reports_request_id` (unique)

## Referential Integrity Rules

- Deleting a `procurement_requests` row cascades deletes to:
  - related `quotations`
  - related `trust_scores`
  - related `reports`
- Deleting a `suppliers` row cascades deletes to:
  - related `quotations`
  - related `trust_scores`

## Migration Source

The schema above is implemented by:

- `alembic/versions/20260505_0001_create_foundation_tables.py`

## Notes For Future Changes

- For strict material taxonomy, move `material_categories` to a normalized join table.
- If financial precision requirements increase, consider raising scale/precision for scoring and price fields.
- Add check constraints for score range (for example `0.0 <= score <= 1.0`) when scoring logic is finalized.



-- Optional but recommended for UUID generation
create extension if not exists pgcrypto;
# Supabase Queries
-- Enum type
do $$
begin
    if not exists (
        select 1
        from pg_type
        where typname = 'procurement_request_status'
    ) then
        create type procurement_request_status as enum (
            'pending',
            'in_progress',
            'complete',
            'failed'
        );
    end if;
end $$;

-- =========================
-- suppliers
-- =========================
create table if not exists suppliers (
    id uuid primary key default gen_random_uuid(),
    name varchar(255) not null,
    email varchar(255) not null unique,
    location varchar(255) not null,
    material_categories jsonb not null default '[]'::jsonb,
    simulated_response_hours integer not null,
    referral_count integer not null default 0,
    simulated_reply_template text not null,
    created_at timestamptz not null default now()
);

create index if not exists ix_suppliers_email on suppliers(email);

-- =========================
-- procurement_requests
-- =========================
create table if not exists procurement_requests (
    id uuid primary key default gen_random_uuid(),
    material_type varchar(100) not null,
    quantity double precision not null,
    unit varchar(50) not null,
    deadline date not null,
    status procurement_request_status not null default 'pending',
    current_agent varchar(100),
    created_at timestamptz not null default now(),
    completed_at timestamptz
);

create index if not exists ix_procurement_requests_material_type
    on procurement_requests(material_type);

-- =========================
-- quotations
-- =========================
create table if not exists quotations (
    id uuid primary key default gen_random_uuid(),
    request_id uuid not null references procurement_requests(id) on delete cascade,
    supplier_id uuid not null references suppliers(id) on delete cascade,
    unit_price numeric(12,2) not null,
    currency varchar(3) not null default 'INR',
    moq integer,
    delivery_days integer,
    validity_days integer,
    payment_terms varchar(255),
    extraction_confidence numeric(5,4),
    missing_fields jsonb not null default '[]'::jsonb,
    raw_text text,
    created_at timestamptz not null default now(),

    constraint chk_quotations_extraction_confidence
        check (
            extraction_confidence is null
            or (extraction_confidence >= 0 and extraction_confidence <= 1)
        )
);

create index if not exists ix_quotations_request_id on quotations(request_id);
create index if not exists ix_quotations_supplier_id on quotations(supplier_id);

-- =========================
-- trust_scores
-- =========================
create table if not exists trust_scores (
    id uuid primary key default gen_random_uuid(),
    request_id uuid not null references procurement_requests(id) on delete cascade,
    supplier_id uuid not null references suppliers(id) on delete cascade,
    price_competitiveness numeric(5,4) not null,
    response_speed_score numeric(5,4) not null,
    quote_completeness numeric(5,4) not null,
    referral_score numeric(5,4) not null,
    composite_score numeric(5,4) not null,
    weights_used jsonb not null,
    computed_at timestamptz not null default now(),

    constraint uq_trust_scores_request_supplier unique (request_id, supplier_id),

    constraint chk_price_competitiveness_range
        check (price_competitiveness >= 0 and price_competitiveness <= 1),

    constraint chk_response_speed_score_range
        check (response_speed_score >= 0 and response_speed_score <= 1),

    constraint chk_quote_completeness_range
        check (quote_completeness >= 0 and quote_completeness <= 1),

    constraint chk_referral_score_range
        check (referral_score >= 0 and referral_score <= 1),

    constraint chk_composite_score_range
        check (composite_score >= 0 and composite_score <= 1)
);

create index if not exists ix_trust_scores_request_id on trust_scores(request_id);
create index if not exists ix_trust_scores_supplier_id on trust_scores(supplier_id);
create index if not exists ix_trust_scores_composite_score on trust_scores(composite_score);

-- =========================
-- reports
-- =========================
create table if not exists reports (
    id uuid primary key default gen_random_uuid(),
    request_id uuid not null unique references procurement_requests(id) on delete cascade,
    summary_text text not null,
    top_suppliers jsonb not null,
    created_at timestamptz not null default now()
);

create unique index if not exists ix_reports_request_id on reports(request_id);