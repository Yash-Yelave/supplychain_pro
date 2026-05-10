from sqlalchemy import inspect, text

from app.crud.suppliers import get_suppliers_by_category, list_all_suppliers
from app.db.session import engine


def main() -> None:
    with engine.connect() as connection:
        connection.execute(text("select 1"))

    inspector = inspect(engine)
    expected_tables = {"suppliers", "procurement_requests", "quotations", "trust_scores", "reports"}
    missing_tables = expected_tables.difference(inspector.get_table_names())
    if missing_tables:
        raise RuntimeError(f"Missing tables: {sorted(missing_tables)}")

    suppliers = list_all_suppliers()
    cement_suppliers = get_suppliers_by_category("cement")

    print(f"Database connection: OK")
    print(f"Tables present: {', '.join(sorted(expected_tables))}")
    print(f"Supplier rows: {len(suppliers)}")
    print(f"Cement supplier rows: {len(cement_suppliers)}")


if __name__ == "__main__":
    main()
