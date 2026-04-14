from __future__ import annotations

import atexit
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings, DATA_DIR

SQLITE_FALLBACK_URL = f"sqlite:///{(DATA_DIR / 'erp_dev.db').as_posix()}"
Base = declarative_base()


def _make_engine(url: str) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(
        url, future=True, connect_args=connect_args,
        pool_pre_ping=not url.startswith("sqlite"),
    )


def _probe(engine: Engine, url: str) -> None:
    if url.startswith("sqlite"):
        return
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def _build_engine() -> tuple[Engine, str]:
    url = settings.database_url
    try:
        eng = _make_engine(url)
        _probe(eng, url)
        return eng, url
    except Exception as exc:
        if settings.database_policy != "dev":
            raise RuntimeError(
                f"ERP database connection failed ({settings.database_policy} mode): {exc}"
            ) from exc
        eng = _make_engine(SQLITE_FALLBACK_URL)
        return eng, SQLITE_FALLBACK_URL


engine, active_url = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def dispose_engine() -> None:
    try:
        engine.dispose()
    except Exception:
        pass


atexit.register(dispose_engine)


def init_db() -> None:
    from . import models  # noqa: F401 — register all models

    if settings.database_policy == "dev":
        Base.metadata.create_all(bind=engine)
        return

    existing = set(inspect(engine).get_table_names())
    required = {t.name for t in Base.metadata.sorted_tables}
    missing = required - existing
    if missing:
        raise RuntimeError(
            f"ERP schema not ready. Missing tables: {', '.join(sorted(missing))}. "
            f"Run Alembic migrations before starting in {settings.database_policy} mode."
        )


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
