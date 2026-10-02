"""Database schema and engine helpers for Decision Tracker."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    event,
)

metadata = MetaData()

decisions = Table(
    "decisions",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("title", String(500), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

options = Table(
    "decision_options",
    metadata,
    Column("id", String(36), primary_key=True),
    Column(
        "decision_id",
        String(36),
        ForeignKey("decisions.id", name="fk_decision_options_decision", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("title", String(255), nullable=False),
    Column("is_selected", Boolean, nullable=False, default=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

pros_cons = Table(
    "pros_cons",
    metadata,
    Column("id", String(36), primary_key=True),
    Column(
        "option_id",
        String(36),
        ForeignKey("decision_options.id", name="fk_pros_cons_option", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("type", String(3), nullable=False),
    Column("text", Text, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    CheckConstraint("type IN ('pro', 'con')", name="ck_pros_cons_type"),
)


def make_engine(database_url: str):
    """Create a SQLAlchemy engine. SQLite is supported for quick local testing."""
    engine = create_engine(database_url, pool_pre_ping=True, future=True)

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine
