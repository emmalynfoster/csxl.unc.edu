"""Helper function to reset the ID sequence of an entity.

When we reset the database and insert data with predefined IDs, Postgres does
not automatically reset the id counter of the database. This helper function
emits a SQL statament to do so."""

from sqlalchemy import text
from sqlalchemy.orm import Session, DeclarativeBase, InstrumentedAttribute


def reset_table_id_seq(
    session: Session,
    entity: type[DeclarativeBase],
    entity_id_column: InstrumentedAttribute[int],
    next_id: int,
) -> None:
    """Reset the ID sequence of an entity table.

    Args:
        session (Session) - A SQLAlchemy Session
        entity (DeclarativeBase) - The SQLAlchemy Entity table to target
        entity_id_column (MappedColumn) - The ID column (should be an int column)
        next_id (int) - Where the next inserted, autogenerated ID should begin

    Returns:
        None"""
    table = entity.__table__
    id_column_name = entity_id_column.name
    sql = text(f"ALTER SEQUENCe {table}_{id_column_name}_seq RESTART WITH {next_id}")
    session.execute(sql)
