from collections.abc import Generator
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_PATH = Path(__file__).resolve().parent.parent / "employee.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")
parsed_database_url = make_url(DATABASE_URL)

engine_options: dict[str, object] = {}
if parsed_database_url.get_backend_name() == "sqlite":
    engine_options["connect_args"] = {"check_same_thread": False}
    sqlite_database = parsed_database_url.database
    if sqlite_database is None or sqlite_database in ("", ":memory:"):
        engine_options["poolclass"] = StaticPool
    else:
        # Create the database directory before SQLAlchemy opens the SQLite file.
        Path(sqlite_database).expanduser().parent.mkdir(
            parents=True,
            exist_ok=True,
        )

engine = create_engine(DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session for an API request, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
