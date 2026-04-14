from __future__ import annotations

from sqlalchemy.orm import Session

from ..repositories import logging as repo

PRODUCTION_LOG_STATUSES = {"recorded", "verified", "closed"}


def list_production_logs(
    session: Session,
    status: str | None = None,
    work_order_id: str | None = None,
    station_id: str | None = None,
    lot_no: str | None = None,
) -> list[dict]:
    rows = repo.list_production_logs(
        session, status=status, work_order_id=work_order_id,
        station_id=station_id, lot_no=lot_no,
    )
    return [_log_to_dict(r) for r in rows]


def get_production_log(session: Session, log_id: str) -> dict | None:
    row = repo.get_production_log(session, log_id)
    return _log_to_dict(row) if row else None


def create_production_log(session: Session, data: dict) -> dict:
    if repo.get_production_log_by_no(session, data["log_no"]):
        raise ValueError(f"Production log '{data['log_no']}' already exists")
    checks = data.pop("param_checks", [])
    return _log_to_dict(repo.create_production_log(session, data, param_checks=checks))


def update_production_log(session: Session, log_id: str, data: dict) -> dict | None:
    if "status" in data and data["status"] is not None:
        if data["status"] not in PRODUCTION_LOG_STATUSES:
            raise ValueError(
                f"Invalid status '{data['status']}'. Allowed: {sorted(PRODUCTION_LOG_STATUSES)}"
            )
    checks = data.pop("param_checks", None)
    row = repo.update_production_log(session, log_id, data, param_checks=checks)
    return _log_to_dict(row) if row else None


def delete_production_log(session: Session, log_id: str) -> bool:
    return repo.delete_production_log(session, log_id)


def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _log_to_dict(log) -> dict:
    d = _row_to_dict(log)
    d["param_checks"] = [_row_to_dict(pc) for pc in log.param_checks]
    return d
