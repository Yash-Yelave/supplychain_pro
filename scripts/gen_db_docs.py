from __future__ import annotations

from pathlib import Path

from sqlalchemy import Index
from sqlalchemy.schema import ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint

from app.db.base import Base
from app import models  # noqa: F401


DOC_PATH = Path("docs/database_schema.md")


def _format_default(col) -> str:
    if col.server_default is not None:
        return str(col.server_default.arg)
    if col.default is None:
        return ""
    arg = col.default.arg
    if callable(arg):
        return getattr(arg, "__name__", "callable")
    return str(arg)


def _render_table(table) -> str:
    lines: list[str] = []
    lines.append(f"## `{table.name}`\n")

    lines.append("| Column | Type | Nullable | Default |")
    lines.append("|---|---|---:|---|")
    for col in table.columns:
        lines.append(f"| `{col.name}` | `{col.type}` | `{col.nullable}` | `{_format_default(col)}` |")
    lines.append("")

    constraints = list(table.constraints)
    pk = next((c for c in constraints if isinstance(c, PrimaryKeyConstraint)), None)
    if pk is not None:
        lines.append(f"- **Primary key:** {', '.join(f'`{c}`' for c in pk.columns.keys())}")

    for uq in (c for c in constraints if isinstance(c, UniqueConstraint)):
        cols = ", ".join(f"`{c}`" for c in uq.columns.keys())
        name = f" (`{uq.name}`)" if uq.name else ""
        lines.append(f"- **Unique{name}:** {cols}")

    for fk in (c for c in constraints if isinstance(c, ForeignKeyConstraint)):
        cols = ", ".join(f"`{c}`" for c in fk.columns.keys())
        targets = ", ".join(f"`{e.column.table.name}.{e.column.name}`" for e in fk.elements)
        name = f" (`{fk.name}`)" if fk.name else ""
        lines.append(f"- **Foreign key{name}:** {cols} → {targets}")

    indexes = [i for i in table.indexes if isinstance(i, Index)]
    for idx in sorted(indexes, key=lambda i: i.name or ""):
        cols = ", ".join(f"`{c.name}`" for c in idx.columns)
        name = f"`{idx.name}`" if idx.name else "`(unnamed)`"
        unique = " unique" if idx.unique else ""
        lines.append(f"- **Index{unique}:** {name} on {cols}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    tables = list(Base.metadata.sorted_tables)
    out: list[str] = []
    out.append("# Database Schema (Authoritative)\n")
    out.append(
        "This document is generated from SQLAlchemy models (`app/models/*`). "
        "Update models + Alembic migrations first, then regenerate:\n\n"
        "```powershell\n"
        "python -m scripts.gen_db_docs\n"
        "```\n"
    )
    out.append("## Entities\n")
    for t in tables:
        out.append(f"- `{t.name}`")
    out.append("")

    for t in tables:
        out.append(_render_table(t))

    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
