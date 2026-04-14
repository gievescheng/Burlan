"""Shared fixtures for erp_qms_core tests.

Uses an in-memory SQLite database so tests run fast and leave no artifacts.
"""
from __future__ import annotations

from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from erp_qms_core.database import Base
from erp_qms_core import models  # noqa: F401 — register models


def _make_test_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )


@pytest.fixture()
def db_session():
    """Yield a SQLAlchemy session backed by in-memory SQLite."""
    engine = _make_test_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(monkeypatch):
    """FastAPI TestClient with the database pointed at in-memory SQLite."""
    import erp_qms_core.database as db_mod

    engine = _make_test_engine()
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    @contextmanager
    def _test_scope():
        session = TestSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    monkeypatch.setattr(db_mod, "session_scope", _test_scope)

    from erp_qms_core.main import app
    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
