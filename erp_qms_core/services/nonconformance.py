from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.transitions import validate_status_transition
from ..repositories import nonconformance as repo

VALID_SEVERITIES = {"critical", "major", "minor"}
VALID_CATEGORIES = {"process", "material", "equipment", "human", "design", "external"}
VALID_DISPOSITIONS = {
    "", "rework", "scrap", "return_to_supplier",
    "concession", "use_as_is", "regrade",
}
VALID_REWORK_RESULTS = {"", "passed", "failed"}


# ── NCR ────────────────────────────────────────────────

def list_ncrs(
    session: Session,
    status: str | None = None,
    severity: str | None = None,
    category: str | None = None,
    disposition: str | None = None,
    work_order_id: str | None = None,
    product_id: str | None = None,
    inspection_lot_id: str | None = None,
    requires_capa: bool | None = None,
    lot_no: str | None = None,
) -> list[dict]:
    rows = repo.list_ncrs(
        session,
        status=status, severity=severity, category=category,
        disposition=disposition, work_order_id=work_order_id,
        product_id=product_id, inspection_lot_id=inspection_lot_id,
        requires_capa=requires_capa, lot_no=lot_no,
    )
    return [_ncr_to_dict(r) for r in rows]


def get_ncr(session: Session, ncr_id: str) -> dict | None:
    row = repo.get_ncr(session, ncr_id)
    return _ncr_to_dict(row) if row else None


def create_ncr(session: Session, data: dict) -> dict:
    if repo.get_ncr_by_no(session, data["ncr_no"]):
        raise ValueError(f"NCR '{data['ncr_no']}' already exists")
    if data.get("severity") and data["severity"] not in VALID_SEVERITIES:
        raise ValueError(f"Invalid severity. Allowed: {sorted(VALID_SEVERITIES)}")
    if data.get("category") and data["category"] not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Allowed: {sorted(VALID_CATEGORIES)}")
    # critical 缺陷強制標記需 CAPA（ISO 10.2 — 重大不符合須矯正措施）
    if data.get("severity") == "critical":
        data["requires_capa"] = True
    return _ncr_to_dict(repo.create_ncr(session, data))


def update_ncr(session: Session, ncr_id: str, data: dict) -> dict | None:
    current = repo.get_ncr(session, ncr_id)
    if not current:
        return None
    if "status" in data and data["status"] is not None:
        err = validate_status_transition("ncr", current.status, data["status"])
        if err:
            raise ValueError(err)
    if "severity" in data and data["severity"] is not None:
        if data["severity"] not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity. Allowed: {sorted(VALID_SEVERITIES)}")
        if data["severity"] == "critical":
            data["requires_capa"] = True
    if "category" in data and data["category"] is not None:
        if data["category"] not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category. Allowed: {sorted(VALID_CATEGORIES)}")
    if "disposition" in data and data["disposition"] is not None:
        if data["disposition"] not in VALID_DISPOSITIONS:
            raise ValueError(
                f"Invalid disposition. Allowed: {sorted(VALID_DISPOSITIONS - {''})}"
            )
        # 設定處置時，若狀態還在 open/under_review，強制推進到 disposition_decided
        if data["disposition"] and current.status in ("open", "under_review"):
            err = validate_status_transition(
                "ncr", current.status, "disposition_decided",
            )
            if err is None:
                data.setdefault("status", "disposition_decided")
    row = repo.update_ncr(session, ncr_id, data)
    return _ncr_to_dict(row) if row else None


def delete_ncr(session: Session, ncr_id: str) -> bool:
    return repo.delete_ncr(session, ncr_id)


# ── ReworkOrder ────────────────────────────────────────

def list_rework_orders(
    session: Session,
    ncr_id: str | None = None,
    work_order_id: str | None = None,
    status: str | None = None,
    result: str | None = None,
) -> list[dict]:
    rows = repo.list_rework_orders(
        session, ncr_id=ncr_id, work_order_id=work_order_id,
        status=status, result=result,
    )
    return [_row_to_dict(r) for r in rows]


def get_rework_order(session: Session, rework_id: str) -> dict | None:
    row = repo.get_rework_order(session, rework_id)
    return _row_to_dict(row) if row else None


def create_rework_order(session: Session, ncr_id: str, data: dict) -> dict:
    ncr = repo.get_ncr(session, ncr_id)
    if not ncr:
        raise LookupError(f"NCR '{ncr_id}' not found")
    if ncr.disposition != "rework":
        raise ValueError(
            f"Cannot create rework order: NCR disposition is '{ncr.disposition or '(unset)'}', expected 'rework'"
        )
    if repo.get_rework_order_by_no(session, data["rework_no"]):
        raise ValueError(f"Rework order '{data['rework_no']}' already exists")
    return _row_to_dict(repo.create_rework_order(session, ncr_id, data))


def update_rework_order(session: Session, rework_id: str, data: dict) -> dict | None:
    current = repo.get_rework_order(session, rework_id)
    if not current:
        return None
    if "status" in data and data["status"] is not None:
        err = validate_status_transition("rework_order", current.status, data["status"])
        if err:
            raise ValueError(err)
    if "result" in data and data["result"] is not None:
        if data["result"] not in VALID_REWORK_RESULTS:
            raise ValueError(
                f"Invalid result. Allowed: {sorted(VALID_REWORK_RESULTS - {''})}"
            )
    row = repo.update_rework_order(session, rework_id, data)
    return _row_to_dict(row) if row else None


def delete_rework_order(session: Session, rework_id: str) -> bool:
    return repo.delete_rework_order(session, rework_id)


# ── helpers ────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _ncr_to_dict(ncr) -> dict:
    d = _row_to_dict(ncr)
    d["rework_orders"] = [_row_to_dict(rw) for rw in ncr.rework_orders]
    return d
