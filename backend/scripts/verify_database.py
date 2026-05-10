import os
from urllib.parse import urlsplit

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def _load_database_url_from_env_file(path: str = ".env") -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return value.strip().strip('"').strip("'")
    return None


def _diagnose_error(error: Exception, database_url: str) -> str:
    error_text = str(error).lower()
    parsed = urlsplit(database_url)

    if "getaddrinfo failed" in error_text or "could not translate host name" in error_text:
        return "Host resolution/network issue. Verify host, DNS access, and whether your network can reach Supabase directly."
    if "password authentication failed" in error_text or "authentication failed" in error_text:
        return "Invalid username/password credentials."
    if "connection refused" in error_text or "timeout" in error_text:
        return "Network path blocked or wrong port. Check firewall, VPN, and Supabase connection mode (direct vs pooler)."
    if "does not exist" in error_text and "database" in error_text:
        return "Database name is incorrect."
    if "invalid dsn" in error_text or "could not parse" in error_text:
        return "Malformed DATABASE_URL. Ensure special characters in password are URL-encoded."
    if "@" in parsed.password if parsed.password else False:
        return "Password appears to contain '@'. URL-encode special characters in password (for example '@' -> '%40')."
    return "Check DATABASE_URL format, credentials, Supabase host/port, and internet/network access."


def main() -> None:
    database_url = os.getenv("DATABASE_URL") or _load_database_url_from_env_file(".env")

    if not database_url:
        print("DATABASE_URL not found in .env")
        return

    print("Starting database verification...")
    print("Using DATABASE_URL from environment.")

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(database_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            print("Database connection successful.")

            basic = connection.execute(text("select 1 as ok, current_timestamp as ts")).mappings().one()
            print(f"Basic query successful. select_1={basic['ok']} current_timestamp={basic['ts']}")

            suppliers = connection.execute(
                text(
                    """
                    select id, name, email, location, material_categories, simulated_response_hours
                    from suppliers
                    order by created_at desc
                    limit 5
                    """
                )
            ).mappings().all()

            print(f"Suppliers fetched: {len(suppliers)}")
            if suppliers:
                print("Sample supplier data:")
                for row in suppliers:
                    print(
                        {
                            "id": str(row["id"]),
                            "name": row["name"],
                            "email": row["email"],
                            "location": row["location"],
                            "material_categories": row["material_categories"],
                            "simulated_response_hours": row["simulated_response_hours"],
                        }
                    )
            else:
                print("No supplier rows found in table.")

    except SQLAlchemyError as error:
        print("Database connection/query failed.")
        print(f"Exact error: {error}")
        print(f"Possible cause: {_diagnose_error(error, database_url)}")
    finally:
        engine.dispose()
        print("Connection resources closed.")


if __name__ == "__main__":
    main()
