"""Migrações mínimas para bancos SQLite criados por versões anteriores."""

from sqlalchemy import inspect, text

from app.database import engine


def migrate_legacy_schema() -> None:
    """Mantém o banco local existente compatível sem apagar dados."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "properties" not in tables:
        return

    property_columns = {column["name"] for column in inspector.get_columns("properties")}
    with engine.begin() as connection:
        if "owner_id" not in property_columns:
            connection.execute(
                text("ALTER TABLE properties ADD COLUMN owner_id INTEGER")
            )

        if engine.dialect.name == "sqlite" and "favorites" in tables:
            # Favoritos antigos eram globais e usavam a string 'guest'.
            connection.execute(
                text("DELETE FROM favorites WHERE CAST(user_id AS TEXT) = 'guest'")
            )
            connection.execute(
                text(
                    "DELETE FROM favorites WHERE id NOT IN "
                    "(SELECT MIN(id) FROM favorites GROUP BY property_id, user_id)"
                )
            )
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS "
                    "uq_favorites_property_user_idx "
                    "ON favorites(property_id, user_id)"
                )
            )
